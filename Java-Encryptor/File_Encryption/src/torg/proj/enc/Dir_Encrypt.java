package torg.proj.enc;
import java.io.*;
import java.lang.reflect.Array;
import java.math.BigInteger;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;
import java.util.Scanner;
import java.util.TreeMap;

public class Dir_Encrypt extends File_Encrypt {
	
	public static TreeMap<String, List<String>> dict = new TreeMap<String, List<String>>();
	File_Encrypt enc = new File_Encrypt();

	//recursively check all contents of target folder along with all subfolders and their files
	private static void Recursive_Check(String Dir_Name) {
		File f = new File(Dir_Name);
		List<String> empty_list = new ArrayList<String>();
		
		//Make sure this directory is in the dict
		if (dict.get(Dir_Name) == null) {
			dict.put(Dir_Name, empty_list);
		}
		
		//if the directory has contents loop through them
		if (f.list() != null) {
			for (String pathname : f.list()) {
				File check_file = new File(Dir_Name + "/" + pathname);
				//if another directory is encountered then recur with new directory
				if (check_file.isDirectory() == true) {
					Recursive_Check(Dir_Name + "/" + pathname);
				}
				//normal files are added to dict
				else {
					dict.get(Dir_Name).add(pathname);
				}
			}
		}
	}
	
	//store the file and its size
	private static void Store_File(RandomAccessFile file_pointer, String key, String file_name) throws IOException {
		File f = new File(key + "/" + file_name);
		//store the size of the opened file and move to store it
		file_pointer.writeLong(f.length());
		file_pointer.seek(file_pointer.length());
		FileInputStream reader = new FileInputStream(f);
		//copy the file byte by byte
		while (reader.available() > 0) {
			file_pointer.write(reader.read());
		}
		reader.close();
	}
	
	//go through the info, put where the file will be, its size, and add the file
	private static void Parse_Files(RandomAccessFile file_pointer) throws IOException {
		long curr_pointer_loc = 0;
		for (String dirs : dict.keySet()) {
			byte[] byteArray = dirs.getBytes();
			file_pointer.seek(file_pointer.getFilePointer() + byteArray.length + 2);
			for (String file : dict.get(dirs)) {
				byte[] byteArray2 = file.getBytes();
				//read through the length of the file name and the end-str byte
				file_pointer.seek(file_pointer.getFilePointer() + byteArray2.length + 2);
				//write where the file will be placed
				file_pointer.writeLong(file_pointer.length());
				curr_pointer_loc = file_pointer.getFilePointer() + 8;
				Store_File(file_pointer, dirs, file);
				file_pointer.seek(curr_pointer_loc);
			}
		}
	}
	
	//the initial decryption file. The subfolders and files are added to a treemap. 
	//Then the treemap is gone through with names and appropriate flags added along with gaps for file size and data address.
	//Metadata length is appended to the beginning then one last walk through is done to actually place file sizes, starting addresses, along with adding the file to their addresses
	public void Encrypt(String file_name, String pass) throws IOException {	
		Recursive_Check(file_name);
		Path checkExistence = Paths.get(file_name);
		if (Files.exists(checkExistence) == false) {
			throw new IOException();
		}
		RandomAccessFile enc_writer = new RandomAccessFile("enc_" + file_name + "_temp", "rw");
		long info_end = 0;
		enc_writer.seek(8);
		//write each directory, the files they contain, and leave a space for the file addr
		for (String dirs : dict.keySet()) {
			byte[] byteArray = dirs.getBytes();
			enc_writer.write(1);
			enc_writer.write(byteArray);
			enc_writer.write(3);
			for (String file : dict.get(dirs)) {
				enc_writer.write(2);
				enc_writer.write(file.getBytes());
				for (int i=0; i < 17; i ++) {
					enc_writer.write(3);
				}
			}
		}
		//go to the start of the metadata, write the metadata length, call Parse_Files to go through and add files
		enc_writer.seek(0);
		info_end = enc_writer.length();
		enc_writer.writeLong(info_end);
		Parse_Files(enc_writer);
		enc_writer.close();

		//have the finished file encrypted and unencrypted one deleted
		enc.Encrypt("enc_" + file_name + "_temp", pass);
		Path fileToDeletePath = Paths.get("enc_" + file_name + "_temp");
		Files.delete(fileToDeletePath);
	}
	
	//read the file's size and data address, then read that many bytes from that address
	private static void writeDecryptedFile(RandomAccessFile enc_reader, String dir, String file) throws IOException {
		long loc = enc_reader.readLong();
		long size = enc_reader.readLong();
		long file_loc = enc_reader.getFilePointer();
		File f = new File(dir + "/" +  file);
		f.createNewFile();
		FileOutputStream writer = new FileOutputStream("./" + dir + "/" + file, false);
		enc_reader.seek(loc);
		for (int i=0; i != size; i++) {
			writer.write(enc_reader.read());
		}
		writer.close();
		enc_reader.seek(file_loc);
	}
	
	//go through the decrypted metadata block, create directories as they are encountered, write the files belonging to that directory
	private void goThroughMetadata(RandomAccessFile reader) throws IOException {
		int holder = 0;
		boolean isDir = true;
		long info_len;
		String dir_str = "";
		String file_str = "";
		info_len = reader.readLong();
		while (reader.getFilePointer() < info_len) {
			holder = reader.read();
			// if holder isn't 1,2, or 3 then add to correct String
			if (holder != 2 && holder != 1) {
				if (holder != 3) {
					if (isDir == false) {
						file_str = file_str + (char) holder;
					}
					else {
						dir_str = dir_str + (char) holder;
					}
				}
				else if (isDir == true) {
					File f = new File(dir_str);
					f.mkdir();
				}
			}
			//if its 1 or 2 then change isDir bool
			else {
				if (holder == 2) {
					isDir = false;
				}
				else {
					dir_str = "";
					isDir = true;
				}
			}
			//if hit a string end symbol (3) and currently on a file name then create this file
			if (isDir == false && holder == 3) {
				writeDecryptedFile(reader, dir_str, file_str);
				//createDecryptedFile(reader, dir_str, file_str);
				file_str = "";
			}
		}
	}
	
	//the initial directory decrypting method. Has the file decryptor decrypt the whole file,
	//has the directories and files actually be created using newly made decrypted file, then deletes the decrypted file it used
	public void Decrypt(String file_name, String pass) throws IOException {
		String dec_string = "";
		RandomAccessFile reader;
		//have the whole file decrypted and reader correctly selecting the named file that will be created
		enc.Decrypt(file_name, pass);
		if (file_name.startsWith("enc_")) {
			dec_string = "dec_" + file_name.substring(4, file_name.length());
			reader = new RandomAccessFile("dec_" + file_name.substring(4, file_name.length()), "r");
		}
		else {
			dec_string = "dec_" + file_name;
			reader = new RandomAccessFile("dec_" + file_name, "r");
		}
		goThroughMetadata(reader);
		reader.close();
		Path fileToDeletePath = Paths.get(dec_string);
		Files.delete(fileToDeletePath);
	}
	
	public static void main(String[] args) throws IOException {
		File_Encrypt file_enc = new File_Encrypt();
		Dir_Encrypt dir_enc = new Dir_Encrypt();
		
		if (args.length == 3) {
			args[0] = args[0].toLowerCase();
			try {
				if (args[0].contains("encryptdir")) {
					dir_enc.Encrypt(args[1], args[2]);
				}
				else if (args[0].contains("encryptfile")) {
					file_enc.Encrypt(args[1], args[2]);
				}
			}
			catch (Exception e) {
				System.out.println("Something went wrong. Encryption failed.");
			}
			
			try {
				if (args[0].contains("decryptdir")) {
					dir_enc.Decrypt(args[1], args[2]);
				}
				else if (args[0].contains("decryptfile")) {
					file_enc.Decrypt(args[1], args[2]);
				}
			}
			catch (Exception e) {
				System.out.println("Something went wrong. Decryption failed.");
			}
		}
		else {
			System.out.println("Error. Incorrect number of arguments.");
		}
	}
}

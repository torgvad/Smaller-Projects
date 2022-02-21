package torg.proj.enc;
import java.io.*;
import java.util.Vector;

public class File_Encrypt {
	
	//pass string and comma count to create a vector of Integers
	private static Vector<Integer> Create_Pass_Vector(String pass, int pass_len) {
		Vector<Integer> pass_array = new Vector<Integer>(pass_len+1);
		int pass_index = 0;
		while (pass_index < pass.length()) {
			if (pass.charAt(pass_index) != ',') {
				pass_array.add(pass.charAt(pass_index) - '0');
			}
			pass_index++;
		}
		return pass_array;
	}
	
	//file encryption method. 
	//Firstly checks if the name matches the temp file the directory encryptor creates
	//The pass is converted a vector of numbers correlating to the ASCII values
	//then the file is traversed with each byte being modified by the corresponding password value (pass is looped until finished)
	public void Encrypt(String file_name, String pass) throws IOException {
		File f = new File(file_name);
		FileInputStream reader = new FileInputStream(f);
		FileOutputStream writer;
		int holder = 0;
		int pass_index_counter = 0;
		int modified_byte = 0;
		int pass_len = pass.length();
		
		if (file_name.startsWith("enc_") && file_name.endsWith("_temp")) {
			writer = new FileOutputStream(file_name.substring(0, file_name.length()-5));
		}
		else {
			writer = new FileOutputStream("enc_" + file_name);
		}
		Vector<Integer> pass_array = new Vector<Integer>(pass_len);
		pass_array = Create_Pass_Vector(pass, pass_len);
		
		//go through whole file and cycle through password to add the correct digit
		while (reader.available() > 0) {
			holder = reader.read();
			modified_byte = holder + pass_array.get(pass_index_counter);
			pass_index_counter++;
			if (modified_byte <= 255) {
				writer.write(modified_byte);
			}
			else {
				writer.write(modified_byte - 256);
			}
			
			if (pass_index_counter == pass_len) {
				pass_index_counter = 0;
			}
		}
		writer.close();
		reader.close(); 
	}
	
	//primary file decryption method. Firtly it removes the "enc_" the encrpytor method adds
	//like the encryptor the pass is turned into a value vector and the file is gone over except the pass values are added instead of subtracted
	public void Decrypt(String file_name, String pass) throws IOException {
		File f = new File(file_name);
		FileInputStream reader = new FileInputStream(f);
		FileOutputStream writer = null;
		int pass_index_counter = 0;
		int modified_byte = 0;
		int pass_len = pass.length();
		int holder = 0;

		//if file starts with 'enc_' remove that
		if (file_name.startsWith("enc_")) {
			writer = new FileOutputStream("dec_" + file_name.substring(4, file_name.length()));
		}
		else {
			writer = new FileOutputStream("dec_" + file_name);
		}
		Vector<Integer> pass_array = new Vector<Integer>(pass_len);
		pass_array = Create_Pass_Vector(pass, pass_len);
		
		//go through whole file and cycle through password to subtract the correct digit
		while (reader.available() > 0) {
			holder = reader.read();
			modified_byte = holder - pass_array.get(pass_index_counter);
			pass_index_counter++;
			if (modified_byte >= 0) {
				writer.write(modified_byte);
			}
			else {
				writer.write(modified_byte + 256);
			}
			
			if (pass_index_counter == pass_len) {
				pass_index_counter = 0;
			}		
		}
		writer.close();
		reader.close();
	}
	
	public static void main(String[] args) throws IOException {
	}
	
}
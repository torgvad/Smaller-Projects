from PyQt6.QtWidgets import QApplication, \
    QWidget, QTableWidget, QVBoxLayout, QTableWidgetItem, QPushButton, QGridLayout, QHBoxLayout, QLineEdit, QHeaderView
from PyQt6.QtGui import QIcon, QFont
import sys
import sqlite3

conn = sqlite3.connect('data/beer_manager.db')
cursor = conn.cursor()
cursor.execute("PRAGMA foreign_keys = ON;")


def get_data(file_name):
    return_list = []
    file = open(file_name, "r")
    for line in file:
         return_list.append(line[:len(line)-1].split(', '))
    return return_list

def create_beer_db():
    beers_list = get_data("data/beers.txt")
    cursor.execute('''CREATE TABLE beer_stock(
                    BeerID integer PRIMARY KEY,
                    Name varchar(255),
                    IBU integer,
                    Alc_content float,
                    Brew_loc varchar(255),
                    Wholesale_price float,
                    Sale_price float, 
                    Style varchar(255),
                    Stock integer);''')
    conn.commit()
    for beer in beers_list:
        cursor.execute('''INSERT INTO beer_stock
                        (Name, IBU, Alc_content, Brew_loc, Wholesale_price, Sale_price, Style, Stock)
                        VALUES
                        (?, ?, ?, ?, ?, ?, ?, ?)''', beer)
    conn.commit()


def create_customer_profile_db():
    customer_profile_list = get_data("data/customer_profiles.txt")
    cursor.execute('''CREATE TABLE customer_profiles (
                    CustomerID integer PRIMARY KEY,
                    Name varchar(255),
                    Email varchar(255),
                    Phone varchar(15),
                    Preferences text,
                    Dislikes text,
                    FOREIGN KEY (CustomerID) REFERENCES customer_info (CustomerID));''')
    conn.commit()
    for customer in customer_profile_list:
        cursor.execute('''INSERT INTO customer_profiles
                        (Name, Email, Phone, Preferences, Dislikes)
                        VALUES
                        (?, ?, ?, ?, ?)''', customer)
    conn.commit()
    print(cursor.execute('''SELECT * FROM customer_profiles;''').fetchall())


def create_customer_info_db():
    customer_profile_list = get_data("data/customer_info.txt")
    cursor.execute('''CREATE TABLE customer_info (
                    CustomerID integer PRIMARY KEY,
                    Name varchar(255),
                    Email varchar(255),
                    Phone varchar(15),
                    Password varchar(255),
                    Shipping_addr text,
                    Billing_addr text,
                    Card_info text);''')
    conn.commit()
    for customer in customer_profile_list:
        cursor.execute('''INSERT INTO customer_info
                        (Name, Email, Phone, Password, Shipping_addr, Billing_addr, Card_info)
                        VALUES
                        (?, ?, ?, ?, ?, ?, ?)''', customer)
    conn.commit()


def create_purchases_db():
    customer_profile_list = get_data("data/purchases.txt")
    cursor.execute('''CREATE TABLE purchases (
                    PurchaseID integer PRIMARY KEY,
                    CustomerID integer,
                    Last_4_Card_Nums varchar(4),
                    Addr text,
                    Sale_date date,
                    Ship_date date, 
                    Beer_IDs text,
                    Quantities text,
                    Tracking text,
                    FOREIGN KEY (CustomerID) REFERENCES customer_profiles (CustomerID));''')
    conn.commit()
    for customer in customer_profile_list:
        print(customer)
        cursor.execute('''INSERT INTO purchases
                        (CustomerID, Last_4_Card_Nums, Addr, Sale_date, Ship_date, Beer_IDs, Quantities, Tracking)
                        VALUES
                        (?, ?, ?, ?, ?, ?, ?, ?)''', customer)
    conn.commit()


def db_generator():
    create_beer_db()
    create_customer_info_db()
    create_customer_profile_db()
    create_purchases_db()


class Window(QWidget):
    global tableWidget
    global search_bar

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Beer Database Lookup")
        self.setWindowIcon(QIcon("qt.png"))
        self.setGeometry(500, 200, 1400, 800)
        self.createUI()

    def createUI(self):
        global tableWidget, search_bar
        button_layout = QVBoxLayout()
        table_searchbar_layout = QVBoxLayout()
        search_bar = QLineEdit()
        main_layout = QHBoxLayout()
        tableWidget = QTableWidget()
        tableWidget.setRowCount(50)
        tableWidget.setColumnCount(9)
        tableWidget.setFont(QFont("Times New Roman", 12))
        table_searchbar_layout.addWidget(search_bar)
        table_searchbar_layout.addWidget(tableWidget)

        beer_style_button = QPushButton()
        beer_style_button.setText("Display All Beers of a Style")
        beer_style_button.clicked.connect(self.display_beers_of_style)
        button_layout.addWidget(beer_style_button)

        customer_purchases_button = QPushButton()
        customer_purchases_button.setText("All Customer Purchases")
        customer_purchases_button.clicked.connect(self.display_customer_purchases)
        button_layout.addWidget(customer_purchases_button)

        purchase_search_button = QPushButton()
        purchase_search_button.setText("Show Purchase Info")
        purchase_search_button.clicked.connect(self.display_purchase_info)
        button_layout.addWidget(purchase_search_button)

        last_x_purchases_button = QPushButton()
        last_x_purchases_button.setText("Fetch Last X Purchases")
        last_x_purchases_button.clicked.connect(self.display_last_x_purchases)
        button_layout.addWidget(last_x_purchases_button)

        unpurchased_preferred_button = QPushButton()
        unpurchased_preferred_button.setText("Customer's Preferred Types, Unpurchased")
        unpurchased_preferred_button.clicked.connect(self.display_unpurchased_preferred)
        button_layout.addWidget(unpurchased_preferred_button)

        unpurchased_local_button = QPushButton()
        unpurchased_local_button.setText("Customer's Preferred Types, Local and Unpurchased")
        unpurchased_local_button.clicked.connect(self.display_unpurchased_preferred_local)
        button_layout.addWidget(unpurchased_local_button)

        local_no_dislike_button = QPushButton()
        local_no_dislike_button.setText("Customer's Local Beer")
        local_no_dislike_button.clicked.connect(self.diplay_local_beer)
        button_layout.addWidget(local_no_dislike_button)

        beer_search_button = QPushButton()
        beer_search_button.setText("Search by Beer Name")
        beer_search_button.clicked.connect(self.display_beer_search)
        button_layout.addWidget(beer_search_button)

        main_layout.addLayout(button_layout)

        main_layout.addLayout(table_searchbar_layout, 2)
        self.setLayout(main_layout)

    def display_beers_of_style(self):
        self.delete_previous_data()
        data = cursor.execute('''SELECT Name, IBU, Alc_content, Brew_loc, Sale_price, Style, Stock FROM beer_stock WHERE Style=?;''', [search_bar.text()]).fetchall()
        self.create_beer_table_labels()
        self.display_info(data)
        tableWidget.resizeColumnsToContents()

    def display_customer_purchases(self):
        self.delete_previous_data()
        data = cursor.execute('''SELECT * FROM purchases WHERE CustomerID=?''', [int(search_bar.text())]).fetchall()
        self.create_purchase_table_labels()
        self.display_info(data)
        tableWidget.resizeColumnsToContents()

    def display_purchase_info(self):
        self.delete_previous_data()
        data = cursor.execute('''SELECT * FROM purchases WHERE PurchaseID=?;''', [int(search_bar.text())]).fetchall()
        self.create_purchase_table_labels()
        self.display_info(data)
        tableWidget.resizeColumnsToContents()

    def display_last_x_purchases(self):
        self.delete_previous_data()
        data = cursor.execute('''SELECT * FROM purchases;''').fetchmany(int(search_bar.text()))
        print(data)
        self.create_purchase_table_labels()
        self.display_info(data)
        tableWidget.resizeColumnsToContents()

    def display_unpurchased_preferred(self):
        self.delete_previous_data()
        data = cursor.execute('''SELECT DISTINCT Preferences FROM customer_profiles WHERE CustomerID = ?;''', [int(search_bar.text())]).fetchall()
        beer_list = self.clean_prefered_beer_list(data)
        data = cursor.execute('''SELECT DISTINCT Beer_IDs FROM purchases WHERE CustomerID = ?;''', [int(search_bar.text())]).fetchall()
        purchase_list = self.clean_prefered_purchase_list(data)
        purchase_list.append('')
        beer_list.append('')
        data = cursor.execute('''SELECT Name, IBU, Alc_content, Brew_loc, Sale_price, Style, Stock FROM beer_stock WHERE Style IN {} AND BeerID NOT IN {};'''.format(tuple(beer_list), tuple(purchase_list))).fetchall()
        self.create_beer_table_labels()
        self.display_info(data)
        tableWidget.resizeColumnsToContents()

    def display_unpurchased_preferred_local(self):
        self.delete_previous_data()
        data = cursor.execute('''SELECT DISTINCT Preferences, Shipping_addr FROM customer_profiles INNER JOIN customer_info WHERE customer_profiles.CustomerID = ? AND customer_info.CustomerID = ?;''', [search_bar.text(), search_bar.text()]).fetchall()
        beer_list = data[0][0].split(";")
        customer_state = data[0][1]
        customer_state = customer_state[customer_state.find('(') + 1:customer_state.find(')')]
        data = cursor.execute('''SELECT DISTINCT Beer_IDs FROM purchases WHERE CustomerID = ?;''', [search_bar.text()]).fetchall()
        purchase_list = self.clean_prefered_purchase_list(data)
        purchase_list.append('')
        beer_list.append('')
        data = cursor.execute('''SELECT Name, IBU, Alc_content, Brew_loc, Sale_price, Style, Stock FROM beer_stock WHERE Style IN {} AND BeerID NOT IN {} AND Brew_loc = ?;'''.format(tuple(beer_list), tuple(purchase_list)), [customer_state]).fetchall()
        self.create_beer_table_labels()
        self.display_info(data)
        tableWidget.resizeColumnsToContents()

    def diplay_local_beer(self):
        self.delete_previous_data()
        data = cursor.execute('''SELECT Name, IBU, Alc_content, Brew_loc, Sale_price, Style, Stock FROM beer_stock WHERE Brew_loc = ?;''', [search_bar.text()]).fetchall()
        self.create_beer_table_labels()
        self.display_info(data)
        tableWidget.resizeColumnsToContents()

    def display_beer_search(self):
        self.delete_previous_data()
        data = cursor.execute('''SELECT Name, IBU, Alc_content, Brew_loc, Sale_price, Style, Stock FROM beer_stock WHERE Name LIKE ?;''', ['%' + search_bar.text() + '%']).fetchall()
        self.create_beer_table_labels()
        self.display_info(data)
        tableWidget.resizeColumnsToContents()

    def clean_prefered_beer_list(self, data):
        beer_list = []
        for itemlist in data:
            beer_list = itemlist[0].split(';')
        return beer_list

    def clean_prefered_purchase_list(self, data):
        purchase_list = []
        for itemlist in data:
            temp = itemlist[0].split(';')
            for item in temp:
                if item not in purchase_list:
                    purchase_list.append(int(item))
        return purchase_list

    def delete_previous_data(self):
        tableWidget.setRowCount(0)
        tableWidget.setRowCount(50)


    def create_purchase_table_labels(self):
        purchase_labels = ["ID", "Customer", "Last 4 Card Digits", "Address", "Sale Date", "Ship Date", "Beer IDs", "Quantities", "Tracking Num"]
        column = 0
        for label in purchase_labels:
            tableWidget.setItem(0, column, QTableWidgetItem(str(label)))
            column += 1

    def create_beer_table_labels(self):
        beer_labels = ["Name", "IBU", "% Alcohol", "Brewery Location", "Price", "Style", "Stock"]
        column = 0
        for label in beer_labels:
            tableWidget.setItem(0, column, QTableWidgetItem(str(label)))
            column += 1

    def display_info(self, sql_data):
        current_row = 1
        current_column = 0
        for item in sql_data:
            for info in item:
                tableWidget.setItem(current_row, current_column, QTableWidgetItem(str(info)))
                current_column += 1
            current_column = 0
            current_row += 1


#db_generator()
app = QApplication(sys.argv)
window = Window()
window.show()
sys.exit(app.exec())

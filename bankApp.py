import sys
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QVBoxLayout, QDialog, QLabel, QLineEdit, QMessageBox
import json
import os
import hashlib
import uuid
import base64

class User:
    def __init__(self, name, passwd, balance=0):  # to take user info
        self.name = name
        self.balance = balance
        self.id = str(uuid.uuid4())

        self.crypted_passwd = self.crypted(passwd)

    def crypted(self, passwd):
        method = hashlib.sha256()  # to make sha256 object
        method.update(passwd.encode('utf-8'))  # using uft-8
        crypted = method.hexdigest()
        return crypted


class UserRepository:
    def __init__(self):
        self.users = []
        self.isLoggedIn = False
        self.currentUser = {}
        self.loadUsers()

    def loadUsers(self):
        if os.path.exists('users.json') and os.path.getsize('users.json') > 0:
            with open('users.json', 'r') as file:
                self.users = json.load(file)
        else:
            self.users = []

    def register(self, user: User):
        if not any(existing_user["name"] == user.name for existing_user in self.users):
            self.users.append(user.__dict__)
            self.savetoFile()
            print('User is created.')
        else:
            print('User with the same name already exists.Choose a different name.')

    def login(self, name, hashed_input_passwd):
        for user in self.users:
            if user["name"] == name and user["crypted_passwd"] == hashed_input_passwd:
                self.isLoggedIn = True
                self.currentUser = user
                print(f'Welcome {name}')
                break
        else:
            print('Invalid account.')

    def savetoFile(self):
        with open('users.json', 'w') as file:
            json.dump(self.users, file, indent=4)

    def delete(self, name, hashed_input_passwd):
        for user in self.users:
            if user["name"] == name and user["crypted_passwd"] == hashed_input_passwd:
                self.users.remove(user)
                self.savetoFile()
                print(f"{name} deleted successfully.")
                break
        else:
            print("Name or password is not correct. Try again.")

    def deposit(self, amount):
        if self.isLoggedIn:
            self.currentUser["balance"] += amount
            self.savetoFile()
            print(f"Deposit successful. New balance: {self.currentUser['balance']}")
        else:
            print("You need to login first.")

    def withdraw(self, amount):
        if self.isLoggedIn:
            if self.currentUser["balance"] >= amount:
                self.currentUser["balance"] -= amount
                self.savetoFile()
                print(f"Withdrawal successful. New balance: {self.currentUser['balance']}")
            else:
                print("Insufficient funds.")
        else:
            print("You need to login first.")

    def listinfo(self):
        if not self.users:
            print("No users found.")
        else:
            for user in self.users:
                print(f"\nID: {user['id']}\nName: {user['name']}\n")


class ShowUsersDialog(QDialog):
    def __init__(self, repo):
        super().__init__()

        self.repo = repo
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle('Show Users')
        layout = QVBoxLayout()
        if not self.repo.users:
            lbl_no_users = QLabel('No users found.', self)
            layout.addWidget(lbl_no_users)
        else:
            for user in self.repo.users:
                lbl_user_info = QLabel(f"ID: {user['id']}\nName: {user['name']}\n", self)
                layout.addWidget(lbl_user_info)
        btn_ok = QPushButton('OK', self)
        btn_ok.clicked.connect(self.accept)
        layout.addWidget(btn_ok)
        self.setLayout(layout)


class DeleteUserDialog(QDialog):
    def __init__(self, repo):
        super().__init__()

        self.repo = repo
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle('Delete User')

        layout = QVBoxLayout()

        self.lbl_name = QLabel('Name:', self)
        self.le_name = QLineEdit(self)
        self.lbl_passwd = QLabel('Password:', self)
        self.le_passwd = QLineEdit(self)
        self.le_passwd.setEchoMode(QLineEdit.Password)

        layout.addWidget(self.lbl_name)
        layout.addWidget(self.le_name)
        layout.addWidget(self.lbl_passwd)
        layout.addWidget(self.le_passwd)

        btn_delete = QPushButton('Delete', self)
        btn_delete.clicked.connect(self.delete_clicked)

        btn_cancel = QPushButton('Cancel', self)
        btn_cancel.clicked.connect(self.reject)

        layout.addWidget(btn_delete)
        layout.addWidget(btn_cancel)

        self.setLayout(layout)

    def delete_clicked(self):
        name = self.le_name.text()
        passwd = self.le_passwd.text()


        if self.le_name is not None and self.le_passwd is not None:
            name = self.le_name.text()
            passwd = self.le_passwd.text()

            # Hash the input password
            hashed_input_passwd = hashlib.sha256(passwd.encode('utf-8')).hexdigest()

            # Call the delete method with the hashed password
            self.repo.delete(name, hashed_input_passwd)
            QMessageBox.information(self, 'info', 'Done, See you again :,(')

            # If delete operation is successful, close the dialog
            self.accept()
        else:
            QMessageBox.warning(self, 'Warning', 'Invalid login. Please try again.')


class LoginDialog(QDialog):
    def __init__(self, repo):
        super().__init__()
        self.repo = repo
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle('Login')

        layout = QVBoxLayout()

        self.lbl_name = QLabel('Name:', self)
        self.le_name = QLineEdit(self)
        self.lbl_passwd = QLabel('Password:', self)
        self.le_passwd = QLineEdit(self)
        self.le_passwd.setEchoMode(QLineEdit.Password)

        layout.addWidget(self.lbl_name)
        layout.addWidget(self.le_name)
        layout.addWidget(self.lbl_passwd)
        layout.addWidget(self.le_passwd)

        btn_login = QPushButton('Login', self)
        btn_login.clicked.connect(self.login_clicked)

        layout.addWidget(btn_login)

        self.setLayout(layout)

    def login_clicked(self):
        name = self.le_name.text()
        passwd = self.le_passwd.text()
        hashed_input_passwd = hashlib.sha256(passwd.encode('utf-8')).hexdigest()

        self.repo.login(name, hashed_input_passwd)

        if self.repo.isLoggedIn:
            QMessageBox.information(self, 'Info', f'Welcome {name}')
            self.accept()  # Close the LoginDialog only if login is successful
        else:
            QMessageBox.warning(self, 'Warning', 'Invalid login. Please try again.')


class RegisterDialog(QDialog):
    def __init__(self, repo):
        super().__init__()

        self.repo = repo
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle('Register')

        layout = QVBoxLayout()

        self.lbl_name = QLabel('Name:', self)
        self.le_name = QLineEdit(self)
        self.lbl_passwd = QLabel('Password:', self)
        self.le_passwd = QLineEdit(self)
        self.le_passwd.setEchoMode(QLineEdit.Password)

        layout.addWidget(self.lbl_name)
        layout.addWidget(self.le_name)
        layout.addWidget(self.lbl_passwd)
        layout.addWidget(self.le_passwd)

        btn_register = QPushButton('Register', self)
        btn_register.clicked.connect(self.register_clicked)

        layout.addWidget(btn_register)

        self.setLayout(layout)

    def register_clicked(self):
        name = self.le_name.text()
        passwd = self.le_passwd.text()
        
        user = User(name, passwd)
        self.repo.register(user)

        QMessageBox.information(self, ' Information', 'Done, do not try again')
        



class TransactionDialog(QDialog):
    def __init__(self, repo):
        super().__init__()

        self.repo = repo
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle('Transaction Operations')

        layout = QVBoxLayout()

        lbl_amount = QLabel('Amount:', self)
        le_amount = QLineEdit(self)
        layout.addWidget(lbl_amount)
        layout.addWidget(le_amount)

        btn_deposit = QPushButton('Deposit', self)
        btn_withdraw = QPushButton('Withdraw', self)

        btn_deposit.clicked.connect(lambda: self.transaction_clicked(le_amount.text(), 'deposit'))
        btn_withdraw.clicked.connect(lambda: self.transaction_clicked(le_amount.text(), 'withdraw'))

        layout.addWidget(btn_deposit)
        layout.addWidget(btn_withdraw)

        # Ekran üzerinde mevcut bakiyeyi göstermek için bir QLabel ekleyelim
        self.lbl_balance = QLabel(f'Your current balance is: {self.repo.currentUser["balance"]}', self)
        layout.addWidget(self.lbl_balance)

        self.setLayout(layout)

    def transaction_clicked(self, amount, operation):
        try:
            amount = float(amount)
        except ValueError:
            QMessageBox.warning(self, 'Warning', 'Invalid amount. Please enter a valid number.')
            return
        if amount < 0:
            QMessageBox.warning(self, 'Warning', 'Please enter a positive amount.')
            return

        if operation == 'withdraw' and amount > self.repo.currentUser["balance"]:
            QMessageBox.warning(self, 'Warning', 'Insufficient funds.')
            return
        if operation == 'deposit':
            self.repo.deposit(amount)
        elif operation == 'withdraw':
            self.repo.withdraw(amount)

        # Mevcut bakiyeyi güncelleyerek ekrana göster
        self.lbl_balance.setText(f'Your current balance is: {self.repo.currentUser["balance"]}')

        # Dosyaya yapılan işlemleri kaydet
        self.repo.savetoFile()


class MainWindow(QWidget):
    def __init__(self, repo):
        super().__init__()

        self.repo = repo
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle('User Repository GUI')

        layout = QVBoxLayout()

        btn_login = QPushButton('Login', self)
        btn_login.clicked.connect(self.login_clicked)

        btn_register = QPushButton('Register', self)
        btn_register.clicked.connect(self.register_clicked)

        btn_show_users = QPushButton('Show Users', self)
        btn_show_users.clicked.connect(self.show_users_clicked)

        btn_delete_user = QPushButton('Delete User', self)
        btn_delete_user.clicked.connect(self.delete_user_clicked)

        btn_exit = QPushButton('Exit', self)
        btn_exit.clicked.connect(self.exit_clicked)

        layout.addWidget(btn_login)
        layout.addWidget(btn_register)
        layout.addWidget(btn_show_users)
        layout.addWidget(btn_delete_user)
        layout.addWidget(btn_exit)

        self.setLayout(layout)

    def login_clicked(self):
        login_dialog = LoginDialog(self.repo)
        if login_dialog.exec_() == QDialog.Accepted and self.repo.isLoggedIn:
            transaction_dialog = TransactionDialog(self.repo)
            transaction_dialog.exec_()

    def register_clicked(self):
        register_dialog = RegisterDialog(self.repo)
        if register_dialog.exec_() == QDialog.Accepted:
            transaction_dialog = TransactionDialog(self.repo)
            transaction_dialog.exec_()

    def show_users_clicked(self):
        show_users_dialog = ShowUsersDialog(self.repo)
        show_users_dialog.exec_()

    def delete_user_clicked(self):
        delete_user_dialog = DeleteUserDialog(self.repo)
        delete_user_dialog.exec_()

    def exit_clicked(self):
        sys.exit()


    def init_ui(self):
        self.setWindowTitle('Register')

        layout = QVBoxLayout()

        self.lbl_name = QLabel('Name:', self)
        self.le_name = QLineEdit(self)
        self.lbl_passwd = QLabel('Password:', self)
        self.le_passwd = QLineEdit(self)
        self.le_passwd.setEchoMode(QLineEdit.Password)

        layout.addWidget(self.lbl_name)
        layout.addWidget(self.le_name)
        layout.addWidget(self.lbl_passwd)
        layout.addWidget(self.le_passwd)

        btn_register = QPushButton('Register', self)
        btn_register.clicked.connect(self.register_clicked)

        layout.addWidget(btn_register)

        self.setLayout(layout)

    def register_clicked(self):
        name = self.le_name.text()
        passwd = self.le_passwd.text()
        
        user = User(name, passwd)
        self.repo.register(user)

        QMessageBox.information(self, ' Information', 'Done, do not try again')
        

if __name__ == '__main__':
    repo = UserRepository()
    app = QApplication(sys.argv)
    main_window = MainWindow(repo)
    main_window.show()
    sys.exit(app.exec_())

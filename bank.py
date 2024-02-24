import json
import os
import hashlib
import uuid
import base64


class User:
    def __init__(self, name, passwd, balance=0): #to take user info 
        self.name = name
        self.balance = balance
        self.id = str(uuid.uuid4())
        
        self.crypted_passwd = self.crypted(passwd)
        
    def crypted(self, passwd):
        method = hashlib.sha256() #to make sha256 object 
        method.update(passwd.encode('utf-8')) #using uft-8 
        crypted = method.hexdigest()
        return crypted     

class UserRepository: #shortly to manage user class -> login,register...
    def __init__(self):
        self.users = []
        self.isLoggedIn = False
        self.currentUser = {}
        self.loadUsers()

    def loadUsers(self): # from json to self.users list
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

    def savetoFile(self): #=> from users list to a json file
        with open('users.json', 'w') as file:
            json.dump(self.users, file, indent = 4)
            
    def delete(self, name, hashed_input_passwd):
        for user in self.users:
            if user["name"] == name and user["crypted_passwd"] == hashed_input_passwd:
                self.users.remove(user)
                self.savetoFile()
                print(f"{name} deleted successfully.")
                break
        else:
            print("Name or password is not correct.Try again.")

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



repo = UserRepository()

while True:
    secim = input('1- Register\n2- Delete User\n3- Login\n4- Show Users\n5- Exit\nChoose: ')
    if secim == '5':
        break
    else:
        if secim == '1':
            name = input('Name: ')
            passwd = input('Password: ')
            user = User(name, passwd)
            repo.register(user)
        elif secim == '2':
            name = input('Enter the username to delete: ')
            passwd = input('Enter the password: ')
            hashed_input_passwd = hashlib.sha256(passwd.encode('utf-8')).hexdigest()
            repo.delete(name,hashed_input_passwd)
        elif secim == '3':
            name = input('Name: ')
            passwd = input('Password: ')
            repo.login(name, passwd)
            if repo.isLoggedIn:
                while True:
                    bakiye_secim = input('1- Deposit\n2- Withdraw\n3- View Balance\n4- Logout\nChoose: ')
                    if bakiye_secim == '4':
                        repo.isLoggedIn = False
                        repo.currentUser = {}
                        print('Logged out successfully.')
                        break
                    elif bakiye_secim == '1':
                        amount = float(input('Enter the deposit amount: '))
                        repo.deposit(amount)
                    elif bakiye_secim == '2':
                        amount = float(input('Enter the withdrawal amount: '))
                        repo.withdraw(amount)
                    elif bakiye_secim == '3':
                        print(f"Current Balance: {repo.currentUser['balance']}")
                    else:
                        print('Invalid entry.')
        elif secim == '4':
            repo.listinfo()
        else:
            print('Invalid entry.')

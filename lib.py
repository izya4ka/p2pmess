import sqlite3
import rsa

def load_or_create_user_keys(pubkey_file, privkey_file):
    try:
        pubkey_file, privkey_file = open(pubkey_file, 'r+b'), open(privkey_file, 'r+b')
        pubkey = rsa.PublicKey.load_pkcs1(pubkey_file.read())
        privkey = rsa.PrivateKey.load_pkcs1(privkey_file.read())
    except FileNotFoundError:
        pubkey_file, privkey_file = open(pubkey_file, 'w+b'), open(privkey_file, 'w+b')
        (pubkey, privkey) = rsa.newkeys(2048)
        pubkey_file.write(pubkey.save_pkcs1())
        privkey_file.write(privkey.save_pkcs1())
    pubkey_file.close()
    privkey_file.close()
    return (pubkey, privkey)

class AddressBook():

    def __init__(self, filename):
        self.con = sqlite3.connect(filename)
        self.cur = self.con.cursor() 

        try:
            self.cur.execute("SELECT * FROM users")
        except sqlite3.OperationalError:
            self.cur.execute("CREATE TABLE users(nickname, ip, key)")

    def add_user(self, nickname, ip, key):
        for row in self.cur.execute("SELECT * FROM users"):
            if nickname == row[0]:
                raise UserAldreadyExist
            if ip == row[1]:
                raise IPAlreadyExist
        self.cur.execute("INSERT INTO users (nickname, ip, key) VALUES (?, ?, ?)", (nickname, ip, key))
        self.con.commit()

    def edit_user(self, nickname_before, nickname, ip, key):
        self.cur.execute("UPDATE users SET nickname = ?, ip = ?, key = ? WHERE nickname = ?", (nickname, ip, key, nickname_before))
        self.con.commit()

    def get_users(self):
        return self.cur.execute("SELECT nickname FROM users").fetchall()
    
    def get_ip(self, nickname):
        return self.cur.execute("SELECT ip FROM users WHERE nickname = :nickname", {'nickname': nickname}).fetchone()

    def get_full_user_data(self, nickname):
        return self.cur.execute("SELECT * FROM users WHERE nickname = :nickname", {'nickname': nickname}).fetchall()
        
class KeyAlreadyExist(Exception):
    def __init__(self, message="Key is already in addressbook!"):
        self.message = message
        super().__init__(self.message)

class UserAldreadyExist(Exception):
    def __init__(self, message="User already exist!"):
        self.message = message
        super().__init__(self.message)

class IPAlreadyExist(Exception):
    def __init__(self, message="IP already exist!"):
        self.message = message
        super().__init__(self.message)

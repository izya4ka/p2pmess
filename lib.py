import sqlite3
import rsa
import re


def send_message(socket, msg, host, key):
    if key == "@selfkey@":
        message = {"encrypted": "key", "msg": msg}
    elif key:
        message = {"encrypted": True, "msg": rsa.encrypt(msg.encode('utf-8'), key)}
    else:
        message = {"encrypted": False, "msg": msg}
    socket.sendto(str(message).encode('utf-8'), host)


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


def validate_key(key):
    try:
        rsa.PublicKey.load_pkcs1(key)
    except:
        return False
    return True


class AddressBook:

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
        if validate_key(key) or key == '':
            if re.match(
                    r"^(((2[0-5]{2})|(1[0-9]{2}|([1-9]\d)|\d))\.?){4}:((655[0-3][0-6])|(65[0-4]\d{2})|(6[0-4]\d{3})|([1-5]\d{4})|([1-9]\d{0,3}))$",
                    ip):
                self.cur.execute("INSERT INTO users (nickname, ip, key) VALUES (?, ?, ?)", (nickname, ip, key))
                self.con.commit()
            else:
                raise IPNotValid
        else:
            raise KeyNotValid

    def edit_user(self, nickname_before, nickname, ip, key):
        self.cur.execute("UPDATE users SET nickname = ?, ip = ?, key = ? WHERE nickname = ?",
                         (nickname, ip, key, nickname_before))
        self.con.commit()

    def get_users(self):
        return self.cur.execute("SELECT nickname FROM users").fetchall()

    def get_ip(self, nickname):
        return self.cur.execute("SELECT ip FROM users WHERE nickname = :nickname", {'nickname': nickname}).fetchone()

    def get_key(self, nickname):
        return self.cur.execute("SELECT key FROM users WHERE nickname = :nickname", {'nickname': nickname}).fetchone()

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


class KeyNotValid(Exception):
    def __init__(self, message="Key not valid!"):
        self.message = message
        super().__init__(self.message)


class IPNotValid(Exception):
    def __init__(self, message="IP not valid!"):
        self.message = message
        super().__init__(self.message)

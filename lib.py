# The GPLv3 License (GPLv3)

# Copyright (c) 2022 Andreev Bogdan

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import sqlite3
import rsa

def load_or_create_user_keys(pubkey_file, privkey_file):
    with open(pubkey_file, "r+b") as pubkey_file:
        with open(privkey_file, "r+b") as privkey_file:
            try:
                pubkey = rsa.PublicKey.load_pkcs1(pubkey_file.read())
                privkey = rsa.PrivateKey.load_pkcs1(privkey_file.read())
            except:
                (pubkey, privkey) = rsa.newkeys(2048)
                pubkey_file.write(pubkey.save_pkcs1())
                privkey_file.write(privkey.save_pkcs1())
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
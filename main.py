#!/bin/python3

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

import socket
from tkinter import *
from tkinter import ttk
from lib import load_or_create_user_keys
from lib import AddressBook
import rsa
import sys

# Get nickname of target and if nickname not given -> exit
args = sys.argv
if len(args) == 1:
    print("No arguments specified")
    sys.exit()
elif len(args) > 2:
    print("Too many arguments")
    sys.exit()
else:
    nickname = args[1]

# Initialize addressbook
addressbook = AddressBook('addressbook.db')
host = addressbook.get_ip(nickname)[0].split(":")
host[1] = int(host[1])
host = tuple(host)
# Socket for receiving messages
s_receive = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s_receive.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
s_receive.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
s_receive.bind(('0.0.0.0', 4444))

# Socket for sending messages
s_send = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s_send.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST,1)

# Initialize keys
keys = load_or_create_user_keys('pubkey', 'privkey')

# Initialize UI
tk = Tk()
tk.title('P2P-chat')
tk.geometry('700x460')
tk.columnconfigure(0, weight=1)
tk.rowconfigure(0, weight=1)

main_frame = ttk.Frame(tk, padding=10)
main_frame.grid(column=0, row=0, sticky=(N, W, E, S))
main_frame.columnconfigure(0, weight=1)
main_frame.columnconfigure(1, weight=2)
main_frame.columnconfigure(2, weight=1)
main_frame.columnconfigure(3, weight=1)
main_frame.columnconfigure(4, weight=1)
main_frame.rowconfigure(1, weight=1)

text = StringVar()

log = Text(main_frame)
log.grid(column=0, row=0, columnspan=3)
log.tag_config('your_messages', foreground='#6D9966')

msg_label = Label(main_frame, text='Text')
msg_label.grid(column=0, row=1)

msg = Entry(main_frame, textvariable=text)
msg.grid(column=0, row=2)

current_user = Label(main_frame, text="Current user: " + nickname)
current_user.grid(column=1, row=1)

encrypt = Checkbutton(main_frame, text="Encrypt")
encrypt.grid(column=2, row=1)

# Send message to target
def sendproc(event, key=None, encrypt=None):
    if not key:
        log.insert(END, "You: " + text.get() + "\n", "your_messages")
        send_message_encoded = text.get().encode('utf-8')
        s_send.sendto(send_message_encoded, host)
    else:
        s_send.sendto(keys[0].save_pkcs1() + b"\n", host)
    msg.delete(0, 'end')


send_key = Button(main_frame, text='Send key', command=lambda: sendproc(event=None, key=True))
send_key.grid(column=2, row=2)

msg.bind('<Return>', sendproc)
msg.focus_set()

# Infinity loop for receiving messages
def loopproc():
    log.see(END)
    s_receive.setblocking(False)
    try:
        message = s_receive.recv(1024)
        log.insert(END, "User: " + message.decode("utf-8") +'\n')
    finally:
        tk.after(1, loopproc)
        return

tk.after(1, loopproc)
tk.mainloop()
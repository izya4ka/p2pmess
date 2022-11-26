import ast
import platform
import socket
import sys
from tkinter import *
from tkinter import ttk
from tkinter.messagebox import showerror

import rsa

from lib import AddressBook
from lib import load_or_create_user_keys
from lib import send_message

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

try:
    user_public_key = rsa.PublicKey.load_pkcs1(addressbook.get_key(nickname)[0])
except:
    user_public_key = None
# Socket for receiving messages
s_receive = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s_receive.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
s_receive.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
s_receive.bind(('0.0.0.0', 4444))

# Socket for sending messages
s_send = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s_send.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

# Initialize keys
keys = load_or_create_user_keys('pubkey', 'privkey')

# Initialize UI
tk = Tk()
if not (platform.system() == "Windows"):
    tk.attributes('-type', 'dialog')
tk.title('P2P-chat')
tk.geometry('700x460')
tk.columnconfigure(0, weight=1)
tk.rowconfigure(0, weight=1)

main_frame = ttk.Frame(tk, padding=10)
# noinspection PyTypeChecker
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


def encrypt_on_change():
    if (enabled.get() == 1) and (not user_public_key):
        showerror("Error", "Key is empty! Message that was sent will be not encrypted!")


enabled = IntVar()
encrypt = Checkbutton(main_frame, text="Encrypt", variable=enabled, command=encrypt_on_change)
encrypt.grid(column=2, row=1)


# Send message to target
def sendproc(event, key=None):
    if not key:
        log.insert(END, "You: " + text.get() + "\n", "your_messages")
        send_message(s_send, text.get(), host, user_public_key if enabled.get() else None)
    else:
        send_message(s_send, keys[0].save_pkcs1().decode('utf-8'), host, "@selfkey@")
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
        message = s_receive.recvfrom(1024)
        host_received = message[1][0]
        message_dicted = ast.literal_eval(message[0].decode("utf-8"))
        enc = " (unencrypted) " if message_dicted["encrypted"] is False else " (encrypted) "
        if host_received == host[0]:
            if message_dicted["encrypted"] == "key":
                print(message_dicted["msg"])
                log.insert(END, "received key from " + nickname + "\n" + message_dicted["msg"] + "\n")
            elif not(message_dicted["encrypted"]):
                log.insert(END, nickname + enc + ": " + message_dicted["msg"] + '\n')
            elif message_dicted["encrypted"]:
                log.insert(END,
                           nickname + enc + ": " + rsa.decrypt(message_dicted["msg"], keys[1]).decode('utf-8') + '\n')
    finally:
        tk.after(1, loopproc)
        return


tk.after(1, loopproc)
tk.mainloop()

#!/bin/python3

import os
from tkinter import *
from tkinter import ttk
from tkinter import messagebox
from lib import AddressBook
from lib import KeyNotValid
from lib import IPNotValid
import subprocess

addressbook = AddressBook("addressbook.db")

tk = Tk()
tk.attributes('-type', 'dialog')
tk.columnconfigure(0, weight=1)
tk.rowconfigure(0, weight=1)
tk.title('P2P-chat')
tk.geometry('300x300')

main_frame = ttk.Frame(tk, padding=10)
main_frame.grid(column=0, row=0, sticky=(N, W, E, S))
main_frame.columnconfigure(0, weight=1)
main_frame.rowconfigure(0, weight=1)

buttons_frame = ttk.Frame(main_frame, padding=5)
buttons_frame.grid(column=1, row=0)

choices = addressbook.get_users()
choicesvar = StringVar(value=choices)
users = Listbox(main_frame, listvariable=choicesvar)
users.grid(column=0, row=0, rowspan=2)

def user_dialog(choicesvar, edit=False, user=None):
    dialog = Toplevel(main_frame)
    dialog.attributes('-type', 'dialog')
    dialog.columnconfigure(0, weight=1)
    dialog.rowconfigure(0, weight=1)
    dialog.grid()

    button_frame = ttk.Frame(dialog, padding=5)
    button_frame.grid(column=0, row=1)

    entry_frame = ttk.Frame(dialog, padding=5)
    entry_frame.grid(column=0, row=0)

    def dismiss(dialog=dialog):
        dialog.grab_release()
        dialog.destroy()

    def user_edit_or_add(nickname, ip, key, choicesvar, edit=False, nickname_before=None):
        print(key)
        try:
            if not edit:
                    addressbook.add_user(nickname, ip, key)
                    choicesvar.set(addressbook.get_users())
                    dismiss()
            else:
                addressbook.edit_user(nickname_before, nickname, ip, key)
        except KeyNotValid:
            messagebox.showerror(title="Error", message="Key not valid!")
        except IPNotValid:
            messagebox.showerror(title="Error", message="IP not valid!")

    cancel = Button(button_frame, text="Close", command=dismiss)
    cancel.grid(column=1, row=6, sticky=W)
    dialog.protocol("WM_DELETE_WINDOW", dismiss)

    nickname_var = StringVar()
    ip_var = StringVar()

    key = Text(entry_frame)

    if not edit:
        ok = Button(button_frame, text="Add", command=lambda: user_edit_or_add(nickname_var.get(), ip_var.get(), key.get(1.0, 'end-1c'), choicesvar))
    else:
        full_user_data = addressbook.get_full_user_data(user)[0]
        nickname_var.set(full_user_data[0])
        ip_var.set(full_user_data[1])
        key.insert(1.0, full_user_data[2])
        ok = Button(button_frame, text="Save", command=lambda: user_edit_or_add(nickname_var.get(), ip_var.get(), key.get(1.0, 'end-1c'), choicesvar, edit=True, nickname_before=user))
    ok.grid(column=0, row=6)
    
    nickname_label = Label(entry_frame, text="Nickname")
    nickname_label.grid(column=0, row=0, columnspan=2)
    nickname = Entry(entry_frame, textvariable=nickname_var)
    nickname.grid(column=0, row=1, columnspan=2)

    ip_label = Label(entry_frame, text="IP Address")
    ip_label.grid(column=0, row=2, columnspan=2)
    ip = Entry(entry_frame, textvariable=ip_var)
    ip.grid(column=0, row=3, columnspan=2)

    key_label = Label(entry_frame, text="Key")
    key_label.grid(column=0, row=4, columnspan=2)
    key.grid(column=0, row=5, columnspan=2)

add_user_button = Button(buttons_frame, text="Add user...", command=lambda: user_dialog(choicesvar))
add_user_button.grid(column=1, row=0)

edit_user_button = Button(buttons_frame, text="Edit user...", command=lambda: user_dialog(choicesvar, edit=True, user=(choices[users.curselection()[0]][0])))
edit_user_button.grid(column=1, row=1, sticky=N)

def start_main(nickname):
    subprocess.Popen(["python3", "main.py", nickname])

users.bind('<Return>', lambda event: start_main(choices[users.curselection()[0]][0]))

tk.mainloop()

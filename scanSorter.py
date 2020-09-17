
'''
import tkinter as tk
import os
from tkinter import filedialog
from tkinter import *

# WINDOW CREATION
win = tk.Tk()
geo = win.geometry
geo("400x400+400+400")
win['bg'] = 'orange'

# get the list of files
folder = filedialog.askdirectory(initialdir="/", title="Select a Folder")
flist = os.listdir(folder)

lbox = tk.Listbox(win)
lbox.pack()

# THE ITEMS INSERTED WITH A LOOP
for item in flist:
    lbox.insert(tk.END, item)


def showcontent(event):
    x = lbox.curselection()[0]
    file = lbox.get(x)
    with open(file, 'r', encoding='utf-8') as file:
        file = file.read()
    text.delete('1.0', tk.END)
    text.insert(tk.END, file)


text = tk.Text(win, bg='cyan')
text.pack()
# BINDING OF LISTBOX lbox
lbox.bind("<<ListboxSelect>>", showcontent)
# BUTTON

win.mainloop()
'''


import tkinter as tk
import os
import sys
from tkinter import filedialog
from tkinter import *

from PIL import Image
from PIL import ImageTk

# WINDOW CREATION
win = tk.Tk()
win.resizable(width=True, height=True)
win['bg'] = 'orange'

lbox = tk.Listbox(win)
lbox.grid(row=0, column=1)

panel = tk.Canvas(win)
panel.grid(row=0, column=0)

def getFolder():
    lbox.delete(0, 'end')
    folder = filedialog.askdirectory(initialdir="/", title="Select a Folder")
    # get the list of files
    flist = os.listdir(folder)
    print(flist)

    # THE ITEMS INSERTED WITH A LOOP
    fileTypes = (".tif", ".png")
    for item in flist:
        if item.endswith(fileTypes):
            lbox.insert(tk.END, item)
        else:
            continue
    def showcontent(x):
        x = lbox.curselection()[0]
        file = lbox.get(x)
        file = os.path.join(folder, file)
        print(file)
        img = ImageTk.PhotoImage(Image.open(file))
        panel.image = img
        panel.create_image(20, 20, anchor=NW, image=img)


    lbox.bind("<<ListboxSelect>>", showcontent)

button = tk.Button(win, text="Select Folder")
button['command'] = getFolder
button.grid(row=1)

def closeSession():
    win.destroy()

close = tk.Button(win, text="Close")
close['command'] = closeSession
close.grid(column=2, row=1)



'''
def showcontent(event, audio=0):
    x = lbox.curselection()[0]
    file = lbox.get(x)
    file = os.path.join(folder, file)
    with open(file, 'r', encoding='utf-8') as file:
        file = file.read()
    text.delete('1.0', tk.END)
    text.insert(tk.END, file)
'''

# BINDING OF LISTBOX lbox
# lbox.bind("<<ListboxSelect>>", showcontent)
# BUTTON

win.mainloop()

import tkinter as tk
import os
import sys
from tkinter import filedialog

from PIL import Image
from PIL import ImageTk

class SortingGui(tk.Frame):
    def __init__(self, master=None):
        super().__init__(master)
        self.master = master
        self.grid(column=9)
        self.create_widgets()

    def create_widgets(self):
        self.fileBox = tk.Listbox(self, exportselection=False)
        self.fileBox.bind("<<ListboxSelect>>", self.showContent)
        self.fileBox.grid(row = 1, column=2)

        self.folderBox = tk.Listbox(self, exportselection=False)
        self.folderBox.bind("<<ListboxSelect>>", self.currentFolder)
        self.folderBox.grid(row=2, column=2)

        self.imageCanvas = tk.Canvas( bg = "white")
        self.imageCanvas.grid(row=0, column=0)

        self.moveCurrentButton = tk.Button(self, text='Move to Current Folder',
                                           command = self.moveToCurrent, underline=0)
        self.moveCurrentButton.grid(row=4, column=0)

        self.newFolder = tk.Button(self, text='New Folder', command = self.createNewFolder, underline = 0)
        self.newFolder.grid(row = 4, column = 1)

        self.undoLastMove = tk.Button(self, text='Undo Move', command = self.undoMove,
                                      underline=0)
        self.undoLastMove.grid(row = 5, column = 1)

        self.changeNewspaperTitle = tk.Button(self, text = 'Change Title', command = self.changeTitle,
                                              underline = 7)
        self.changeNewspaperTitle.grid(row=4, column = 2)

        self.changeNewspaperDate = tk.Button(self, text = 'Change Date', command = self.changeDate,
                                             underline=7)
        self.changeNewspaperDate.grid(row = 5, column = 2)

        self.selectFolder = tk.Button(self, text="Select Reel", command=self.getFolder,
                                      underline=0)
        self.selectFolder.grid(row=4, column=3)

        self.close = tk.Button(self, text="Exit", command=self.master.destroy, underline=1)
        self.close.grid(row=5, column=3)

    def getFolder(self):
        self.fileBox.delete(0, 'end')
        self.folder = filedialog.askdirectory(initialdir="/", title="Select a Folder")
        # get the list of files
        flist = os.listdir(self.folder)

        # THE ITEMS INSERTED WITH A LOOP
        fileTypes = (".tif", ".png")
        for item in flist:
            isFolder = os.path.join(self.folder, item)
            isdir = os.path.isdir(isFolder)
            if item.endswith(fileTypes):
                self.fileBox.insert(tk.END, item)
            elif isdir == True:
                self.folderBox.insert(tk.END, item)
            else:
                continue

        print(flist)


    def showContent(self, event):
        widget = event.widget
        selection = widget.curselection()
        file = widget.get(selection[0])
        folder = self.folder
        file = os.path.join(self.folder, file)
        print(file)
        img = ImageTk.PhotoImage(Image.open(file))
        self.imageCanvas.image = img
        self.imageCanvas.create_image(20, 20, image=img)

    def currentFolder(self, event):
        widget = event.widget
        selection = widget.curselection()
        file = widget.get(selection[0])
        folder = self.folder
        print(folder)

    def moveToCurrent(self):
        x = self.folderBox.curselection()
        y = self.fileBox.curselection()
        px = self.folderBox.get(x[0])
        py = self.fileBox.get(y[0])
        print(px)
        print(py)
        #probably need to use os.path connection

    def createNewFolder(self):
        print('New Folder')

    def undoMove(self):
        print('Undo')

    def changeTitle(self):
        print('Change Title')

    def changeDate(self):
        print('Change Date')


root = tk.Tk()
app = SortingGui(master=root)
app.mainloop()

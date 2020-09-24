import tkinter as tk
import os
import sys
from tkinter import filedialog, Radiobutton, StringVar

from PIL import Image
from PIL import ImageTk

class SortingGui(tk.Frame):
    def __init__(self, master=None):
        super().__init__(master)
        self.master = master
        self.grid(column=9)
        self.create_widgets()

    def create_widgets(self):

        #popup dialog for newspaper information
        self.infoField = tk.Label(self, text="Enter Newspaper Information")

        newspaperTitle = tk.StringVar()
        self.newspaperTitle = tk.StringVar()
        self.titleEntry = tk.Entry(self, textvariable=newspaperTitle, text="Newspaper Title:")

        # date pickerwill go here
        issueDate = tk.StringVar()

        published = tk.StringVar()
        self.daily = Radiobutton(self, text="Daily", variable=published, value=1)
        self.weekly = Radiobutton(self, text="Weekly", variable=published, value=2)
        self.montly = Radiobutton(self, text="Monthly", variable=published, value=3)

        #application window itself

        self.fileBox = tk.Listbox(self, exportselection=False)
        self.fileBox.bind("<<ListboxSelect>>", self.showContent)
        self.fileBox.grid(row = 1, column=2)

        self.folderBox = tk.Listbox(self, exportselection=False)
        self.folderBox.bind("<<ListboxSelect>>", self.getCurrentFolder)
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

    def getNewspaperInfo(self):
        # popup dialog to populate the variables
        print('')

    def getFolder(self):
        self.fileBox.delete(0, 'end')
        self.folder = filedialog.askdirectory(initialdir="/", title="Select a Folder")
        # get the list of files
        flist = os.listdir(self.folder)

        os.chdir(self.folder)
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

    def getCurrentFolder(self, event):
        widget = event.widget
        selection = widget.curselection()
        currentFolder = widget.get(selection[0])
        directory = self.folder
        currentFolder = os.path.join(directory, currentFolder)
        print(currentFolder)


    def createNewFolder(self):
        # createNewFolder needs to create a new folder naming it by changing the published variable
        # depending on what they chose for the radiobutton
        newFolder = "testing2" #str(newspaperTitle) + ',' + str(issueDate) # may also need to be
                                                               # month + day + year
                                                               # depending on how we format things
                                                               # with the calendar
        newFolder = os.path.join(self.folder, newFolder)
        print(newFolder)
        if not os.path.exists(newFolder):
            os.makedirs(newFolder)
            os.chdir(newFolder)
            # needs to then refresh the listbox
            # and change the selection to the new folder
            # will this require calling the getCurrentFolder function?
        else:
            os.chdir(newFolder)

            # needs to select the folder in the listbox

    def moveToCurrent(self):
        viewedFile = self.fileBox.curselection()
        currentFolder = self.folderBox.curselection()
        # or would we invoke the getCurrentFolder function somehow???


        #probably need to use os.path connection
        # need to save this movement to a variable each time so that we can tell
        # the system to move specific file from current folder to previous folder
        # for the undo button

        '''
        # this is the test code for the current selection mechanism
        x = self.folderBox.curselection()
        y = self.fileBox.curselection()
        #px = self.folderBox.get(x[0])
        py = self.fileBox.get(y[0])
        #print(px)
        print(py)
        '''




    def undoMove(self):
        print('Undo')

    def changeTitle(self):
        # self.newspaperTitle = what's in the fucking box!?
        print('Change Title')

    def changeDate(self):
        print('Change Date')


root = tk.Tk()
app = SortingGui(master=root)
app.mainloop()

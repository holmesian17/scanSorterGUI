import tkinter as tk
import os
import sys
from tkinter import filedialog, Radiobutton, StringVar
import random

# import datetime
# import calendar
# import tkcalendar

from PIL import Image
from PIL import ImageTk




class SortingGui(tk.Frame):
    def __init__(self, master=None):
        super().__init__(master)
        self.master = master
        self.grid(column=9)
        self.create_widgets()

    def create_widgets(self):

        # popup dialog for newspaper information
        self.infoField = tk.Label(self, text="Enter Newspaper Information")

        self.newspaperTitle = tk.StringVar()
        # self.titleEntry = tk.Entry(self, textvariable=newspaperTitle, text="Newspaper Title:")

        self.issueDate = tk.StringVar()

        self.fileLabel = tk.Label(self, text="Files", font=("Helvetica", 16))
        self.fileLabel.grid(row=0, column=5)

        self.fileBox = tk.Listbox(self, exportselection=False, width=50)
        self.fileBox.bind("<<ListboxSelect>>", self.showContent)
        self.fileBox.grid(row=1, column=5, padx=30, rowspan=2)

        self.folderLabel = tk.Label(self, text="Folders", font=("Helvetica", 16))
        self.folderLabel.grid(row=3, column=5, padx=30)

        self.folderBox = tk.Listbox(self, exportselection=False, width=50, selectmode="single")
        self.folderBox.bind("<<ListboxSelect>>", self.getCurrentFolder)
        self.folderBox.grid(row=4, column=5)

        self.moveCurrentButton = tk.Button(self, text='Move to Current Folder',
                                           command=self.moveToCurrent, underline=0)
        # self.bind('Control-m',self.moveToCurrent)
        self.moveCurrentButton.grid(row=4, column=2, pady=5, ipadx=20, ipady=20)

        self.markDupe = tk.Button(self, text='Remove Duplicate', command=self.removeDupe, underline=7)
        self.markDupe.grid(row=5, column=4, pady=5, ipadx=20, ipady=20)

        # self.flagImageForReScan = tk.Button(self, text='Flag this photo for rescanning', underline=0)
        # self.flagImageForReScan.grid(row=5, column=0)

        self.createFolder = tk.Button(self, text='New Folder', command=self.createNewFolder, underline=0)
        self.createFolder.grid(row=2, column=2, pady=5, ipadx=20, ipady=20)
        '''
        self.undoLastMove = tk.Button(self, text='Undo Move', command=self.undoMove,
                                      underline=0)
        self.undoLastMove.grid(row=5, column=2)
        '''
        self.selectFolder = tk.Button(self, text="Select Reel", command=self.getFolder,
                                      underline=0)
        self.selectFolder.grid(row=5, column=5, pady=5, ipadx=20, ipady=20)

        self.close = tk.Button(self, text="Exit", command=self.master.destroy, underline=1)
        self.close.grid(row=5, column=6, pady=5, ipadx=20, ipady=20)

        self.imageCanvas = tk.Canvas(self.master, highlightthickness=0, width=600, height=800)
        self.imageCanvas.grid(row=0, column=0, sticky='nswe', columnspan=2, rowspan=10)
        self.imageCanvas.update()  # wait till canvas is created

        self.imageCanvas.bind('<ButtonPress-1>', self.move_from)
        self.imageCanvas.bind('<B1-Motion>', self.move_to)
        self.imageCanvas.bind('<MouseWheel>', self.wheel)  # with Windows and MacOS, but not Linux

    def move_from(self, event):
        ''' Remember previous coordinates for scrolling with the mouse '''
        self.imageCanvas.scan_mark(event.x, event.y)

    def move_to(self, event):
        ''' Drag (move) canvas to the new position '''
        self.imageCanvas.scan_dragto(event.x, event.y, gain=1)
        self.show_image()  # redraw the image

    def wheel(self, event):
        ''' Zoom with mouse wheel '''
        x = self.imageCanvas.canvasx(event.x)
        y = self.imageCanvas.canvasy(event.y)
        bbox = self.imageCanvas.bbox(self.container)  # get image area
        if bbox[0] < x < bbox[2] and bbox[1] < y < bbox[3]:
            pass  # Ok! Inside the image
        else:
            return  # zoom only inside image area
        scale = 1.0
        # Respond to Linux (event.num) or Windows (event.delta) wheel event
        if event.num == 5 or event.delta == -120:  # scroll down
            i = min(self.width, self.height)
            if int(i * self.imscale) < 30: return  # image is less than 30 pixels
            self.imscale /= self.delta
            scale /= self.delta
        if event.num == 4 or event.delta == 120:  # scroll up
            i = min(self.imageCanvas.winfo_width(), self.imageCanvas.winfo_height())
            if i < self.imscale: return  # 1 pixel is bigger than the visible area
            self.imscale *= self.delta
            scale *= self.delta
        self.imageCanvas.scale('all', x, y, scale, scale)  # rescale all canvas objects
        self.show_image()

    def show_image(self, event=None):
        ''' Show image on the Canvas '''
        bbox1 = self.imageCanvas.bbox(self.container)  # get image area
        # Remove 1 pixel shift at the sides of the bbox1
        bbox1 = (bbox1[0] + 1, bbox1[1] + 1, bbox1[2] - 1, bbox1[3] - 1)
        bbox2 = (self.imageCanvas.canvasx(0),  # get visible area of the canvas
                 self.imageCanvas.canvasy(0),
                 self.imageCanvas.canvasx(self.imageCanvas.winfo_width()),
                 self.imageCanvas.canvasy(self.imageCanvas.winfo_height()))
        bbox = [min(bbox1[0], bbox2[0]), min(bbox1[1], bbox2[1]),  # get scroll region box
                max(bbox1[2], bbox2[2]), max(bbox1[3], bbox2[3])]
        if bbox[0] == bbox2[0] and bbox[2] == bbox2[2]:  # whole image in the visible area
            bbox[0] = bbox1[0]
            bbox[2] = bbox1[2]
        if bbox[1] == bbox2[1] and bbox[3] == bbox2[3]:  # whole image in the visible area
            bbox[1] = bbox1[1]
            bbox[3] = bbox1[3]
        self.imageCanvas.configure(scrollregion=bbox)  # set scroll region
        x1 = max(bbox2[0] - bbox1[0], 0)  # get coordinates (x1,y1,x2,y2) of the image tile
        y1 = max(bbox2[1] - bbox1[1], 0)
        x2 = min(bbox2[2], bbox1[2]) - bbox1[0]
        y2 = min(bbox2[3], bbox1[3]) - bbox1[1]
        if int(x2 - x1) > 0 and int(y2 - y1) > 0:  # show image if it in the visible area
            x = min(int(x2 / self.imscale), self.width)  # sometimes it is larger on 1 pixel...
            y = min(int(y2 / self.imscale), self.height)  # ...and sometimes not
            image = self.image.crop((int(x1 / self.imscale), int(y1 / self.imscale), x, y))
            imagetk = ImageTk.PhotoImage(image.resize((int(x2 - x1), int(y2 - y1))))
            imageid = self.imageCanvas.create_image(max(bbox2[0], bbox1[0]), max(bbox2[1], bbox1[1]),
                                                    anchor='nw', image=imagetk)
            self.imageCanvas.lower(imageid)  # set image into background
            self.imageCanvas.imagetk = imagetk  # keep an extra reference to prevent garbage-collectio

    def reelSelect(self):
        global mainFolder
        self.fileBox.delete(0, 'end')
        self.mainFolder = filedialog.askdirectory(initialdir="/", title="Select a Folder")

    def getFolder(self):
        # self.fileBox.delete(0, 'end')
        # self.folder = filedialog.askdirectory(initialdir="/", title="Select a Folder")
        # get the list of files
        global mainFolder
        self.reelSelect()
        flist = os.listdir(self.mainFolder)

        os.chdir(self.mainFolder)
        # THE ITEMS INSERTED WITH A LOOP
        fileTypes = (".tif", ".png")
        for item in flist:
            isFolder = os.path.join(self.mainFolder, item)
            isdir = os.path.isdir(isFolder)
            if item.endswith(fileTypes):
                self.fileBox.insert(tk.END, item)
            elif isdir == True:
                self.folderBox.insert(tk.END, item)
            else:
                continue
        self.fileBox.select_set(0)  # This only sets focus on the first item.
        self.fileBox.event_generate("<<ListboxSelect>>")
        print(flist)

    def populateListBox(self):
        flist = os.listdir(self.folder)

        os.chdir(self.folder)
        # THE ITEMS INSERTED WITH A LOOP
        isFolder = os.path.join(self.folder, self.newFolder)
        self.folderBox.insert(tk.END, item)
        print(flist)

    def showContent(self, event):
        widget = event.widget
        selection = widget.curselection()
        file = widget.get(selection[0])
        folder = self.mainFolder
        file = os.path.join(folder, file)
        print(file)
        # img = ImageTk.PhotoImage(Image.open(file))
        # self.imageCanvas.image = img
        # self.imageCanvas.create_image(20, 20, image=img)
        self.image = Image.open(file)  # open image
        self.width, self.height = self.image.size
        self.imscale = 0.5  # scale for the canvaas image
        self.delta = 1.3  # zoom magnitude
        # Put image into container rectangle and use it to set proper coordinates to the image
        self.container = self.imageCanvas.create_rectangle(0, 0, self.width, self.height, width=0)
        # Plot some optional random rectangles for the test purposes
        '''
        minsize, maxsize, number = 5, 20, 10
        for n in range(number):
            x0 = random.randint(0, self.width - maxsize)
            y0 = random.randint(0, self.height - maxsize)
            x1 = x0 + random.randint(minsize, maxsize)
            y1 = y0 + random.randint(minsize, maxsize)
            color = ('red', 'orange', 'yellow', 'green', 'blue')[random.randint(0, 4)]
            self.imageCanvas.create_rectangle(x0, y0, x1, y1, fill=color, activefill='black')
         '''
        self.show_image()

    def getCurrentFolder(self, event):
        global currentFolder

        widget = event.widget
        selection = widget.curselection()
        currentFolder = widget.get(selection[0])
        directory = self.mainFolder
        currentFolder = os.path.join(directory, currentFolder)
        print(currentFolder)
        # root.after(100, self.getCurrentFolder())

    def createNewFolder(self):
        global mainFolder

        folderWindow = tk.Toplevel(app)

        folderWindow.title("New Folder")
        folderWindow.geometry("400x100")

        folderName = tk.StringVar(self)

        def folderSubmit():
            name=folderName.get()
            print(name)

            folder = self.mainFolder
            print(folder + " folder")
            newFolder = os.path.join(folder, str(name))
            print(newFolder)
            if not os.path.exists(newFolder):
                flist = os.listdir(folder)

                os.makedirs(newFolder)

                os.chdir(newFolder)
                # THE ITEMS INSERTED WITH A LOOP
                self.folderBox.insert(tk.END, name)
                self.folderBox.selection_clear("end")
                self.folderBox.selection_set("end")
                self.folderBox.see("end")

                print(flist)

                os.chdir(newFolder)
                # needs to then refresh the listbox
                # and change the selection to the new folder
                # will this require calling the getCurrentFolder function?
                print("created")


            else:
                os.chdir(newFolder)
                print("changed")
                print(os.getcwd())

            folderWindow.destroy()

        folderLabel = tk.Label(folderWindow, text='Folder name', font=('calibre', 14, 'bold'))

        folderEntry = tk.Entry(folderWindow, textvariable=folderName, font=('calibre', 20, 'normal'))

        folderSubmit = tk.Button(folderWindow, text='Submit',
                                command=folderSubmit, height=1)
        folderEntry.grid(row=1, column=0, sticky='nswe')
        folderLabel.grid(row=0, column=0, sticky='nswe')
        folderSubmit.grid(row=2, column=0, sticky='nswe')
        #self.newFolder = self.issueDate.get()
        #newFolder = self.newspaperTitle + ", " + self.issueDate

        # print(newFolder + 'test')

        #print(issueDate.get())


            # needs to select the folder in the listbox

    def moveToCurrent(self):
        global currentFolder
        global mainFolder

        x = self.folderBox.curselection()
        y = self.fileBox.curselection()
        px = self.folderBox.get(x[0])
        folder = currentFolder
        py = self.fileBox.get(y[0])
        filePath = os.path.join(self.mainFolder, py)
        selectedFolder = px
        #folderPath = os.path.join(folder, px)
        movedFilePath = os.path.join(folder, py)

        print(px)
        print(py)
        #print(folderPath)
        print(filePath)
        print(movedFilePath)
        os.rename(filePath, movedFilePath)
        #shutil.move(filePath, movedFilePath)
        #os.replace(filePath, movedFilePath)
        self.fileBox.delete(self.fileBox.curselection())
        self.fileBox.select_set(0)  # This only sets focus on the first item.
        self.fileBox.event_generate("<<ListboxSelect>>")
        #### self.folderBox.insert(tk.END, name)

        '''
        print(selectedFolder)
        print(folder)
        print(file)
        print(movedFolderPath)
        '''
    '''
    def undoMove(self):
        print(self.newspaperTitle.get())
        # os.rename(self.movedFilePath, self.filePath)
    '''
    def removeDupe(self):
        global mainFolder

        y = self.fileBox.curselection()
        py = self.fileBox.get(y[0])
        filePath = os.path.join(self.mainFolder, py)
        folder = self.mainFolder
        dupeFolder = os.path.join(self.mainFolder, "Duplicates")
        movedFilePath = os.path.join(dupeFolder, py)

        if not os.path.exists(dupeFolder):
            flist = os.listdir(folder)

            os.makedirs(dupeFolder)

            os.chdir(dupeFolder)
            # THE ITEMS INSERTED WITH A LOOP
            self.folderBox.insert(tk.END, "Duplicates")
            self.folderBox.selection_clear("end")
            self.folderBox.selection_set("end")
            self.folderBox.see("end")

            os.rename(filePath, movedFilePath)

            self.fileBox.delete(self.fileBox.curselection())
            self.fileBox.select_set(0)  # This only sets focus on the first item.
            self.fileBox.event_generate("<<ListboxSelect>>")
            #os.chdir(newFolder)
            # needs to then refresh the listbox
            # and change the selection to the new folder
            # will this require calling the getCurrentFolder function?
            print("created")

        else:
            os.chdir(dupeFolder)

            os.rename(filePath, movedFilePath)

            self.fileBox.delete(self.fileBox.curselection())
            self.fileBox.select_set(0)  # This only sets focus on the first item.
            self.fileBox.event_generate("<<ListboxSelect>>")
            print("changed")

            #print(os.getcwd())

    def titleSubmit(self):
        title = self.newspaperTitle.get()

        print(title)


root = tk.Tk()
root.geometry("1400x900")
app = SortingGui(master=root)

app.mainloop()

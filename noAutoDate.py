import tkinter as tk
import os
import sys
from tkinter import filedialog, Radiobutton, StringVar
import random

import datetime
import calendar
import tkcalendar

from PIL import Image
from PIL import ImageTk

global newspaperTitle
global issueDate
global currentFolderName
global published
global daily
global weekly
global monthly


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

        # date pickerwill go here
        self.issueDate = tk.StringVar()

        # self.published = tk.StringVar()

        # self.daily = Radiobutton(self, text="Daily", variable=published, value=1)
        # self.weekly = Radiobutton(self, text="Weekly", variable=published, value=2)
        # self.montly = Radiobutton(self, text="Monthly", variable=published, value=3)

        # application window itself

        self.fileLabel = tk.Label(self, text="Files")
        self.fileLabel.grid(row=0, column=5)

        self.fileBox = tk.Listbox(self, exportselection=False, width=50)
        self.fileBox.bind("<<ListboxSelect>>", self.showContent)
        self.fileBox.grid(row=1, column=5)

        self.folderLabel = tk.Label(self, text="Folders")
        self.folderLabel.grid(row=2, column=5)

        self.folderBox = tk.Listbox(self, exportselection=False, width=50)
        self.folderBox.bind("<<ListboxSelect>>", self.getCurrentFolder)
        self.folderBox.grid(row=3, column=5)

        self.moveCurrentButton = tk.Button(self, text='Move to Current Folder',
                                           command=self.moveToCurrent, underline=0)
        self.moveCurrentButton.grid(row=4, column=0)

        '''
        titleAndDate = StringVar()
        self.currentIssueFolder = tk.Label(self, textvariable=titleAndDate)
        titleAndDate.set(str(self.newspaperTitle) + ', ' + str(self.issueDate))
        self.currentIssueFolder.grid(row=5, column=0)
        '''
        self.newFolder = tk.Button(self, text='New Folder', command=self.createNewFolder, underline=0)
        self.newFolder.grid(row=4, column=2)

        self.undoLastMove = tk.Button(self, text='Undo Move', command=self.undoMove,
                                      underline=0)
        self.undoLastMove.grid(row=5, column=2)

        self.changeNewspaperTitle = tk.Button(self, text='Change Title', command=self.titleEntry,
                                              underline=7)
        self.changeNewspaperTitle.grid(row=4, column=3)
        '''
        self.comboSet = tk.Button(self, text='Set Title and Issue', command=self.comboEntry,
                                              underline=7)
        self.comboSet.grid(row=0, column=0)

        self.changeNewspaperDate = tk.Button(self, text = 'Change Date', command = self.changeDate,
                                             underline=7)
        self.changeNewspaperDate.grid(row = 5, column = 3)

        self.changeRepeatingButton = tk.Button(self, text = 'Change Repeating', command = self.changeRepeating,
                                                 underline=7)
        self.changeRepeatingButton.grid(row=6, column=3)
        '''
        self.selectFolder = tk.Button(self, text="Select Reel", command=self.getFolder,
                                      underline=0)
        self.selectFolder.grid(row=4, column=5)

        self.close = tk.Button(self, text="Exit", command=self.master.destroy, underline=1)
        self.close.grid(row=5, column=5)

        self.imageCanvas = tk.Canvas(self.master, highlightthickness=0, width=800, height=800)
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
        # img = ImageTk.PhotoImage(Image.open(file))
        # self.imageCanvas.image = img
        # self.imageCanvas.create_image(20, 20, image=img)
        self.image = Image.open(file)  # open image
        self.width, self.height = self.image.size
        self.imscale = 1.0  # scale for the canvaas image
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
        widget = event.widget
        selection = widget.curselection()
        currentFolder = widget.get(selection[0])
        directory = self.folder
        currentFolder = os.path.join(directory, currentFolder)
        print(currentFolder)

    def issueSubmit(self):
        issue = self.issueDate.get()

        print(issue)

    def createNewFolder(self):
        '''
        def add_months(sourcedate, months):
            month = sourcedate.month - 1 + months
            year = sourcedate.year + month // 12
            month = month % 12 + 1
            day = min(sourcedate.day, calendar.monthrange(year, month)[1])
            return datetime.date(year, month, day)

        # createNewFolder needs to create a new folder naming it by changing the published variable
        # depending on what they chose for the radiobutton
        if self.daily = True: # or whatever value indicates this is the case
            upADay = datetime.timedelta(days=1)
            self.issueDate = self.issueDate + upADay
            newFolder = self.newspaperTitle.get() + ', ' + self.issueDate.get() # may also need to be
                                                               # month + day + year
                                                               # depending on how we format things
                                                               # with the calendar
        elif self.weekly = True:
            upAWeek = datetime.timedelta(days=7)
            self.issueDate = self.issueDate + upAWeek
            newFolder = self.newspaperTitle.get() + ', ' + self.issueDate.get()  # may also need to be
            # month + day + year
            # depending on how we format things
            # with the calendar

        elif self.monthly = True:
            issueDate = add_months(issueDate, 1)

        elif self.monthly
        '''
        issueWindow = tk.Toplevel(app)

        issueWindow.title("Change Newspaper Date")
        issueWindow.geometry("600x300")

        self.issueDate = tk.StringVar()

        issueLabel = tk.Label(issueWindow, text='Issue Date',
                              font=('calibre',
                                    10, 'bold'))
        issueLabel.grid()

        issueEntry = tk.Entry(issueWindow, textvariable=self.issueDate, font=('calibre', 10, 'normal'))
        issueEntry.grid()

        issueSubmit = tk.Button(issueWindow, text='Submit',
                                command=self.issueSubmit)
        issueSubmit.grid()

        newFolder = self.newspaperTitle + ", " + self.issueDate

        print(newFolder)

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
        currentOpenFolder = self.folderBox.curselection()
        # or would we invoke the getCurrentFolder function somehow???

        # probably need to use os.path connection
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
        print(self.newspaperTitle.get())

    '''
    def comboSubmit(self):
        title = self.newspaperTitle.get()
        issue = self.issueDate.get()

        print(title + ", " + issue)

    def comboEntry(self):
        comboWindow = tk.Toplevel(app)

        comboWindow.title("Enter Newspaper Information")
        comboWindow.geometry("600x300")

        self.newspaperTitle = tk.StringVar()
        self.issueDate = tk.StringVar()

        self.published = tk.StringVar()
        self.daily = Radiobutton(self, text="Daily", variable=published, value=1)
        self.weekly = Radiobutton(self, text="Weekly", variable=published, value=2)
        self.montly = Radiobutton(self, text="Monthly", variable=published, value=3)

        titleLabel = tk.Label(comboWindow, text='Title',
                              font=('calibre',
                                    10, 'bold'))

        issueLabel = tk.Label(comboWindow, text='Issue Date',
                              font=('calibre',
                                    10, 'bold'))

        titleEntry = tk.Entry(comboWindow,
                              textvariable=self.newspaperTitle, font=('calibre', 10, 'normal'))

        issueEntry = tk.Entry(comboWindow,
                              textvariable=self.issueDate, font=('calibre', 10, 'normal'))
        titleLabel.grid(column=0, row=0)
        titleEntry.grid(column=1, row=0)
        issueLabel.grid(column=0, row=1)
        issueEntry.grid(column=1, row=1)

        comboSubmit = tk.Button(comboWindow, text='Submit',
                                command=self.comboSubmit)
        comboSubmit.grid(column=0, row=2)
    '''

    def titleSubmit(self):
        title = self.newspaperTitle.get()

        print(title)

        titleWindow.destroy()

        # title.set("")

    def titleEntry(self):
        titleWindow = tk.Toplevel(app)

        titleWindow.title("Enter Newspaper Title")
        titleWindow.geometry("600x300")

        self.newspaperTitle = tk.StringVar()

        titleLabel = tk.Label(titleWindow, text='Title',
                              font=('calibre',
                                    10, 'bold'))
        titleLabel.grid()
        titleEntry = tk.Entry(titleWindow,
                              textvariable=self.newspaperTitle, font=('calibre', 10, 'normal'))
        titleEntry.grid()
        titleSubmit = tk.Button(titleWindow, text='Submit',
                                command=self.titleSubmit)
        titleSubmit.grid()


'''
    def issueSubmit(self):
        issue = self.issueDate.get()

        print(issue)

        issueWindow.destroy()
        #title.set("")

    def changeDate(self):
        issueWindow = tk.Toplevel(app)

        issueWindow.title("Change Newspaper Date")
        issueWindow.geometry("600x300")

        self.issueDate = tk.StringVar()

        issueLabel = tk.Label(issueWindow, text='Title',
                              font=('calibre',
                                    10, 'bold'))
        issueLabel.grid()

        issueEntry = tk.Entry(issueWindow, textvariable=self.issueDate, font=('calibre', 10, 'normal'))
        issueEntry.grid()

        issueSubmit = tk.Button(issueWindow, text='Submit',
                                command=self.issueSubmit)
        issueSubmit.grid()
        '''
'''
    def publishedSubmit(self):
        published = self.published.get()

        print(published)

    def changeRepeating(self):
        publishedWindow = tk.Toplevel(app)
        publishedWindow.title("Change Recurrance")
        publishedWindow.geometry("600x300")

        self.published = tk.StringVar()

        publishedLabel = tk.Label(publishedWindow, text="Recurs", font=('calibre',
                                    10, 'bold'))
        publishedLabel.grid()

        daily = Radiobutton(self, text="Daily", variable=self.published, value=1)
        weekly = Radiobutton(self, text="Weekly", variable=self.published, value=2)
        montly = Radiobutton(self, text="Monthly", variable=self.published, value=3)

        daily.grid(row=1, column=0)
        weekly.grid(row=1, column=1)
        monthly.grid(row=1, column=2)

        publishedEntry = tk.Entry(publishedWindow,
                              textvariable=self.published, font=('calibre', 10, 'normal'))
        publishedEntry.grid()

        publishedSubmit = tk.Button(publishedWindow, text='Submit',
                                command=self.publishedSubmit())
        publishedSubmit.grid()
    '''
root = tk.Tk()
root.geometry("1400x900")
app = SortingGui(master=root)

app.mainloop()
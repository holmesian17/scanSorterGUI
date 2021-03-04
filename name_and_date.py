import tkinter as tk
import os
from tkinter import filedialog
from tkcalendar import Calendar

from PIL import Image
from PIL import ImageTk


class sorting_gui(tk.Frame):
    def __init__(self, master=None):
        super().__init__(master)
        self.master = master
        self.grid(column=9)
        self.create_widgets()

    def create_widgets(self):

        # popup dialog for newspaper information
        self.info_field = tk.Label(self, text="Enter Newspaper Information")

        self.newspaper_title = tk.Button(self, text='Change Title', command=self.title_box, underline=0)
        self.newspaper_title.grid(row=3, column=2, pady=5, ipadx=20, ipady=20)

        self.issue_date = tk.StringVar()

        self.file_label = tk.Label(self, text="Files", font=("Helvetica", 16))
        self.file_label.grid(row=0, column=5)

        self.file_box = tk.Listbox(self, exportselection=False, width=50)
        self.file_box.bind("<<ListboxSelect>>", self.show_content)
        self.file_box.grid(row=1, column=5, padx=30, rowspan=2)

        self.folder_label = tk.Label(self, text="Folders", font=("Helvetica", 16))
        self.folder_label.grid(row=3, column=5, padx=30)

        self.folder_box = tk.Listbox(self, exportselection=False, width=50, selectmode="single")
        self.folder_box.bind("<<ListboxSelect>>", self.get_current_folder)
        self.folder_box.grid(row=4, column=5)

        self.move_current_button = tk.Button(self, text='Move to Current Folder',
                                           command=self.move_to_current, underline=0)
        # self.bind('Control-m',self.move_to_current)
        self.move_current_button.grid(row=4, column=2, pady=5, ipadx=20, ipady=20)

        self.mark_dupe = tk.Button(self, text='Remove Duplicate', command=self.remove_dupe, underline=7)
        self.mark_dupe.grid(row=5, column=4, pady=5, ipadx=20, ipady=20)

        # self.flagImageForReScan = tk.Button(self, text='Flag this photo for rescanning', underline=0)
        # self.flagImageForReScan.grid(row=5, column=0)

        self.create_folder = tk.Button(self, text='New Folder', command=self.create_new_folder, underline=0)
        self.create_folder.grid(row=2, column=2, pady=5, ipadx=20, ipady=20)

        self.undo_last_move = tk.Button(self, text='Undo Move', command=self.undo_move,
                                      underline=0)
        self.undo_last_move.grid(row=5, column=2, pady=5, ipadx=20, ipady=20)

        self.select_folder = tk.Button(self, text="Select Reel", command=self.get_folder,
                                      underline=0)
        self.select_folder.grid(row=5, column=5, pady=5, ipadx=20, ipady=20)

        self.close = tk.Button(self, text="Exit", command=self.master.destroy, underline=1)
        self.close.grid(row=5, column=6, pady=5, ipadx=20, ipady=20)

        self.image_canvas = tk.Canvas(self.master, highlightthickness=0, width=600, height=800)
        self.image_canvas.grid(row=0, column=0, sticky='nswe', columnspan=2, rowspan=10)
        self.image_canvas.update()  # wait till canvas is created

        self.image_canvas.bind('<ButtonPress-1>', self.move_from)
        self.image_canvas.bind('<B1-Motion>', self.move_to)
        self.image_canvas.bind('<MouseWheel>', self.wheel)  # with Windows and MacOS, but not Linux

    def move_from(self, event):
        """ Remember previous coordinates for scrolling with the mouse """
        self.image_canvas.scan_mark(event.x, event.y)

    def move_to(self, event):
        """ Drag (move) canvas to the new position """
        self.image_canvas.scan_dragto(event.x, event.y, gain=1)
        self.show_image()  # redraw the image

    def wheel(self, event):
        """ Zoom with mouse wheel """
        x = self.image_canvas.canvasx(event.x)
        y = self.image_canvas.canvasy(event.y)
        bbox = self.image_canvas.bbox(self.container)  # get image area
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
            i = min(self.image_canvas.winfo_width(), self.image_canvas.winfo_height())
            if i < self.imscale: return  # 1 pixel is bigger than the visible area
            self.imscale *= self.delta
            scale *= self.delta
        self.image_canvas.scale('all', x, y, scale, scale)  # rescale all canvas objects
        self.show_image()

    def show_image(self):
        """ Show image on the Canvas """
        bbox1 = self.image_canvas.bbox(self.container)  # get image area
        # Remove 1 pixel shift at the sides of the bbox1
        bbox1 = (bbox1[0] + 1, bbox1[1] + 1, bbox1[2] - 1, bbox1[3] - 1)
        bbox2 = (self.image_canvas.canvasx(0),  # get visible area of the canvas
                 self.image_canvas.canvasy(0),
                 self.image_canvas.canvasx(self.image_canvas.winfo_width()),
                 self.image_canvas.canvasy(self.image_canvas.winfo_height()))
        bbox = [min(bbox1[0], bbox2[0]), min(bbox1[1], bbox2[1]),  # get scroll region box
                max(bbox1[2], bbox2[2]), max(bbox1[3], bbox2[3])]
        if bbox[0] == bbox2[0] and bbox[2] == bbox2[2]:  # whole image in the visible area
            bbox[0] = bbox1[0]
            bbox[2] = bbox1[2]
        if bbox[1] == bbox2[1] and bbox[3] == bbox2[3]:  # whole image in the visible area
            bbox[1] = bbox1[1]
            bbox[3] = bbox1[3]
        self.image_canvas.configure(scrollregion=bbox)  # set scroll region
        x1 = max(bbox2[0] - bbox1[0], 0)  # get coordinates (x1,y1,x2,y2) of the image tile
        y1 = max(bbox2[1] - bbox1[1], 0)
        x2 = min(bbox2[2], bbox1[2]) - bbox1[0]
        y2 = min(bbox2[3], bbox1[3]) - bbox1[1]
        if int(x2 - x1) > 0 and int(y2 - y1) > 0:  # show image if it in the visible area
            x = min(int(x2 / self.imscale), self.width)  # sometimes it is larger on 1 pixel...
            y = min(int(y2 / self.imscale), self.height)  # ...and sometimes not
            image = self.image.crop((int(x1 / self.imscale), int(y1 / self.imscale), x, y))
            imagetk = ImageTk.PhotoImage(image.resize((int(x2 - x1), int(y2 - y1))))
            imageid = self.image_canvas.create_image(max(bbox2[0], bbox1[0]), max(bbox2[1], bbox1[1]),
                                                    anchor='nw', image=imagetk)
            self.image_canvas.lower(imageid)  # set image into background
            self.image_canvas.imagetk = imagetk  # keep an extra reference to prevent garbage-collectio

    def reel_select(self):
        global main_folder
        self.file_box.delete(0, 'end')
        self.main_folder = filedialog.askdirectory(initialdir="/", title="Select a Folder")

    def get_folder(self):
        # self.file_box.delete(0, 'end')
        # self.folder = filedialog.askdirectory(initialdir="/", title="Select a Folder")
        # get the list of files
        global main_folder
        self.reel_select()
        flist = os.listdir(self.main_folder)

        os.chdir(self.main_folder)
        # THE ITEMS INSERTED WITH A LOOP
        fileTypes = (".tif", ".png")
        for item in flist:
            is_folder = os.path.join(self.main_folder, item)
            isdir = os.path.isdir(is_folder)
            if item.endswith(fileTypes):
                self.file_box.insert(tk.END, item)
            elif isdir == True:
                self.folder_box.insert(tk.END, item)
            else:
                continue
        self.file_box.select_set(0)  # This only sets focus on the first item.
        self.file_box.event_generate("<<ListboxSelect>>")
        #print(flist)

    def populate_list_box(self):
        flist = os.listdir(self.folder)

        os.chdir(self.folder)
        # THE ITEMS INSERTED WITH A LOOP
        is_folder = os.path.join(self.folder, self.new_folder)
        self.folder_box.insert(tk.END, item)
        #print(flist)

    def show_content(self, event):
        widget = event.widget
        selection = widget.curselection()
        file = widget.get(selection[0])
        folder = self.main_folder
        file = os.path.join(folder, file)
        #print(file)
        # img = ImageTk.PhotoImage(Image.open(file))
        # self.image_canvas.image = img
        # self.image_canvas.create_image(20, 20, image=img)
        self.image = Image.open(file)  # open image
        self.width, self.height = self.image.size
        self.imscale = 0.5  # scale for the canvaas image
        self.delta = 1.3  # zoom magnitude
        # Put image into container rectangle and use it to set proper coordinates to the image
        self.container = self.image_canvas.create_rectangle(0, 0, self.width, self.height, width=0)
        # Plot some optional random rectangles for the test purposes
        '''
        minsize, maxsize, number = 5, 20, 10
        for n in range(number):
            x0 = random.randint(0, self.width - maxsize)
            y0 = random.randint(0, self.height - maxsize)
            x1 = x0 + random.randint(minsize, maxsize)
            y1 = y0 + random.randint(minsize, maxsize)
            color = ('red', 'orange', 'yellow', 'green', 'blue')[random.randint(0, 4)]
            self.image_canvas.create_rectangle(x0, y0, x1, y1, fill=color, activefill='black')
         '''
        self.show_image()

    def get_current_folder(self, event):
        global current_folder

        widget = event.widget
        selection = widget.curselection()
        current_folder = widget.get(selection[0])
        #print(current_folder + " current_folder in gCF")
        directory = self.main_folder
        current_folder = os.path.join(directory, current_folder)
        #print(current_folder)
        # root.after(100, self.get_current_folder())

    def title_box(self):
        global newspaper_title
        global title

        title_window = tk.Toplevel(app)

        title_window.title("Change Title")
        title_window.geometry("400x100")

        newspaper_title = tk.StringVar(self)

        def title_submit():
            title = newspaper_title.get()
            print(title)
            title_window.destroy()

        title_label = tk.Label(title_window, text='Newspaper name', font=('calibre', 14, 'bold'))

        title_entry = tk.Entry(title_window, textvariable=newspaper_title, font=('calibre', 20, 'normal'))

        title_submit = tk.Button(title_window, text='Submit',
                                  command=title_submit, height=1)

        title_entry.grid(row=1, column=0, sticky='nswe')
        title_label.grid(row=0, column=0, sticky='nswe')
        title_submit.grid(row=2, column=0, sticky='nswe')

        print("varb", newspaper_title.get())

    def create_new_folder(self):
        global main_folder
        global current_folder

        folder_window = tk.Toplevel(app)

        folder_window.title("New Folder")
        folder_window.geometry("400x100")

        folder_name = tk.StringVar(self)

        def folder_submit():
            name = folder_name.get()
            #print(name)

            folder = self.main_folder
            #(folder + " folder")
            new_folder = os.path.join(folder, str(name))
            current_folder = new_folder
            #print(new_folder)
            if not os.path.exists(new_folder):
                flist = os.listdir(folder)

                os.makedirs(new_folder)

                os.chdir(new_folder)
                # THE ITEMS INSERTED WITH A LOOP
                self.folder_box.insert("end", name)
                self.folder_box.selection_clear(0, "end")
                self.folder_box.selection_set("end")

                self.folder_box.see("end")
                self.folder_box.activate("end")

                self.folder_box.event_generate("<<ListboxSelect>>")


                #print(flist)

                #os.chdir(new_folder)
                # needs to then refresh the listbox
                # and change the selection to the new folder
                # will this require calling the get_current_folder function?
                #print("created")


            else:
                os.chdir(new_folder)
                #print("changed")
                #print(os.getcwd())

            folder_window.destroy()

        folder_label = tk.Label(folder_window, text='Folder name', font=('calibre', 14, 'bold'))

        folder_entry = tk.Entry(folder_window, textvariable=folder_name, font=('calibre', 20, 'normal'))

        folder_submit = tk.Button(folder_window, text='Submit',
                                 command=folder_submit, height=1)
        folder_entry.grid(row=1, column=0, sticky='nswe')
        folder_label.grid(row=0, column=0, sticky='nswe')
        folder_submit.grid(row=2, column=0, sticky='nswe')

        # self.new_folder = self.issue_date.get()
        # new_folder = self.newspaper_title + ", " + self.issue_date

        # print(new_folder + 'test')

        # print(issue_date.get())

        # needs to select the folder in the listbox

    def move_to_current(self):
        global current_folder
        global main_folder

        global file_path
        global moved_file_path

        x = self.folder_box.curselection()
        y = self.file_box.curselection()
        px = self.folder_box.get(x[0])
        folder = current_folder
        py = self.file_box.get(y[0])
        file_path = os.path.join(self.main_folder, py)
        # folderPath = os.path.join(folder, px)
        moved_file_path = os.path.join(folder, py)

        #print(px)
        #print(py)
        # print(folderPath)
        #print(file_path)
        #print(moved_file_path)
        os.rename(file_path, moved_file_path)
        # shutil.move(file_path, moved_file_path)
        # os.replace(file_path, moved_file_path)
        self.file_box.delete(self.file_box.curselection())
        self.file_box.select_set(0)  # This only sets focus on the first item.
        self.file_box.event_generate("<<ListboxSelect>>")
        #### self.folder_box.insert(tk.END, name)

        '''
        print(selectedFolder)
        print(folder)
        print(file)
        print(movedFolderPath)
        '''


    def undo_move(self):
        global main_folder
        global file_path

        os.rename(moved_file_path, file_path)
        addBack = os.path.split(file_path)
        self.file_box.insert(0, addBack[1])
        self.file_box.delete(self.file_box.curselection())
        self.file_box.select_set(0)
        self.file_box.event_generate("<<ListboxSelect>>")


    def remove_dupe(self):
        global main_folder

        y = self.file_box.curselection()
        py = self.file_box.get(y[0])
        file_path = os.path.join(self.main_folder, py)
        folder = self.main_folder
        dupe_folder = os.path.join(self.main_folder, "Duplicates")
        moved_file_path = os.path.join(dupe_folder, py)

        if not os.path.exists(dupe_folder):
            flist = os.listdir(folder)

            os.makedirs(dupe_folder)

            os.chdir(dupe_folder)
            # THE ITEMS INSERTED WITH A LOOP
            self.folder_box.insert("end", "Duplicates")
            self.folder_box.selection_clear(0, "end")
            self.folder_box.selection_set("end")

            # self.folder_box.activate("end")
            self.folder_box.see("end")

            os.rename(file_path, moved_file_path)

            self.file_box.delete(self.file_box.curselection())
            self.file_box.select_set(0)  # This only sets focus on the first item.
            self.file_box.event_generate("<<ListboxSelect>>")
            # os.chdir(new_folder)
            # needs to then refresh the listbox
            # and change the selection to the new folder
            # will this require calling the get_current_folder function?
            #print("created")

        else:
            os.chdir(dupe_folder)

            os.rename(file_path, moved_file_path)

            self.file_box.delete(self.file_box.curselection())
            self.file_box.select_set(0)  # This only sets focus on the first item.
            self.file_box.event_generate("<<ListboxSelect>>")
            #print("changed")

            # print(os.getcwd())

    def date_select(self):
        pass


# newspaper title: enter newspaper title
# folder name format

# choose how often: daily, weekly
# iterate to next date on new folder creation


root = tk.Tk()
root.geometry("1400x900")
app = sorting_gui(master=root)

app.mainloop()

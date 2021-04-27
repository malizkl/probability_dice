from tkinter import *
from bs4 import BeautifulSoup
import requests
import random

class GUI(Frame):
    def __init__(self,parent):
        Frame.__init__(self, parent)
        self.initUI()
        self.run = 0
        self.colors = ['dodger blue','pale turquoise', 'dark turquoise','medium turquoise','turquoise','cyan', 'cadet blue','medium aquamarine','aquamarine','LemonChiffon4', 'cornsilk2', 'cornsilk4','honeydew2','dark orchid','dark violet','blue violet','purple']
        self.selectedlesson = []
        self.activelessons = {}
        self.listboxitems = []

    def fetch_courses(self):
        if self.run == 1:
            pass
        else:
            try:
                self.statuslabel.configure(text="Status: Fetched", bg="#337DFF", font="Windsor 10 bold")
                self.run = 1
                puredata = []
                self.courselist = []
                webpage = requests.get("https://www.sehir.edu.tr/tr/duyurular/2019_2020_akademik_yili_bahar_donemi_ders_programi")
                contents = webpage.content
                soup = BeautifulSoup(contents, 'html.parser')
                # we parse the data from the website and find all relative terms using class and MSO, since we only need the 1st 3rd and 4th element i use
                # if statements to filter them and pour them into their respective variables.
                for text in soup.find_all("p",attrs={"class": "MsoNormal"}):
                    puredata.append(text.get_text())
                del puredata[0:6]
                var1 = 0
                for element in puredata:
                    var1+=1
                    if var1 == 1:
                        lessonname = element
                    elif var1 == 3:
                        lessonday = element
                    elif var1 == 4:
                        lessonhour = element
                        if lessonhour == " ":
                            continue
                        else:
                            #i create my course objects here and insert them into a 2 lists one being courselist which will help me find the data i am looking for and a listbox items so i can use it to
                            #filter listbox items
                            self.courselist.append(Course(lessonname, lessonday, lessonhour))
                            self.courseslistbox.insert("end", lessonname + " " + lessonday + " " + lessonhour)
                            self.listboxitems.append(lessonname)
                    if var1 == 6:
                        var1 = 0  #since the elements repeat every 6 times we set the variable to 0 everytime we hit 6th element
            except:
                pass
    def update_list(self,*args):
        search_term = self.search_var.get()  # i get the string var from the gui below which allows me to detect changes in the entry widget
        self.courseslistbox.delete(0, END)
        for item in self.listboxitems:
            if search_term.lower() in item.lower():     #i delete and re insert according to the strings entered
                for course in self.courselist:
                    if course.name == item:
                        self.courseslistbox.insert(END, course.name + " " + course.day + " " + course.time)

    def row_column_find(self,time,day):
        self.statuslabel.configure(text="Status: Fetched", bg="#337DFF",font="Windsor 10 bold")
        for widget in self.widgetdic.values():      #if there is an error i put X in the end of the status label, this code detects that and if there is an error does no run the code below
            if widget.color == "X":
                pass
            else:
                widget.widget.configure(bg=widget.color)
        self.selectedlesson.clear() #i use my selected lesson list for my red and yellow boxes. whenever something is selected they are put in this list it gets cleaned whenever i click on another entry
        time_indexes = []
        time=time.split()
        day=day.split()
        day_indexes = []
        hour_count = 0
        for i in range(len(time)): # i parse the time data into a usable form so i can find the indexes from my time lists.
            time_indexes.append([])
            index = 0
            hour_count+=1
            cur_time = time[i]
            starting_time = cur_time[0] + cur_time[1] + cur_time[2] + cur_time[3] + cur_time[4]
            ending_time = cur_time[-5] + cur_time[-4] + cur_time[-3] + cur_time[-2] + cur_time[-1]
            for coursetime in self.rowlist:     #find the indexes of the time data being taken from the course
                index+=1
                coursetime = coursetime.split()
                if coursetime[0] == "X":
                    continue
                if starting_time == coursetime[0]:
                    time_indexes[hour_count-1].append(index)
                if ending_time == coursetime[2]:
                    time_indexes[hour_count-1].append(index)
                    break
        for b in range(len(day)):       #find the indexes of the day data being taken from the course
            index = 0
            for courseday in self.columlist:
                index+=1
                cur_day=day[b]
                if courseday == "X":
                    continue
                if cur_day == courseday:
                    day_indexes.append(index)
                    break
        for i in range(hour_count):         #if there are more days than ours that means times are being re used which means we have to re use the times in different days
            if len(day_indexes) > len(time_indexes):
                time_indexes[i].append(day_indexes[0])
            else:
                time_indexes[i].append(day_indexes[i])
        for list in time_indexes:
            row = list[0]
            for i in range((list[1])+1 - list[0]):      #repeats this code for the amount of cells i have to change
                widget_adress = "col" + str(list[2]) + "row" + str(row)
                if self.widgetdic[widget_adress].widget.cget("text") == "":
                    self.widgetdic[widget_adress].widget.configure(bg="yellow")
                if self.widgetdic[widget_adress].widget.cget("text") != "":
                    self.widgetdic[widget_adress].widget.configure(bg="red")
                    self.statuslabel.configure(text="Overlap with other courses X",bg="red")
                self.selectedlesson.append(widget_adress)       #we update the selected lessons here so we can know which cells are being highlighted
                row += 1
        return self.selectedlesson  #since i need to use this data in another function, i return the data which makes the code more compact



    def check_availability(self):
        try:
            selection = self.courseslistbox.get(self.courseslistbox.curselection())
            selection = selection.split()
            if selection[2] in self.columlist:
                selection = selection[0] + " " + selection[1]           #gets selection data from the currently clicked listbox
            else:
                selection = selection[0] + " " + selection[1] + " " + selection[2]
            for course in self.courselist:
                if course.name == selection:            #compares selection data to the courselist data and uses the course data to run our cell finding function
                    for adress in self.selectedlesson:
                        self.widgetdic[adress].widget.configure(bg="green")
                    self.row_column_find(course.time,course.day)
                    return course
        except:
            pass
    def add_course(self):
        if self.statuslabel.cget("text")[-1] == "X": #if there is an error in the status label then this line of code will not work
            pass
        else:
            rand_color=random.choice(self.colors)      #we pick a random color and remove it from our color list, i also run availability and get cell data from our functions above so i know which cells to edit
            self.colors.remove(rand_color)
            course=self.check_availability()
            for adress in self.selectedlesson:      #i change the cell data to the randomly picked color and assign course objects and cell objects in a active lessons dictionary to figure out which lessons are active
               self.widgetdic[adress].widget.configure(bg=rand_color)
               self.widgetdic[adress].widget.configure(text=course.name)
               self.widgetdic[adress].color = rand_color
               self.widgetdic[adress].course = course
            self.activelessons[course] = []
            for adress in self.selectedlesson:                      #creates the active lesson dictionary so we know which lessons and cells are active so we can iterate through them
                self.activelessons[course].append(self.widgetdic[adress])
            self.selectedlesson.clear()             #we clear selected lesson after adding so we dont get any bugs
            selection = self.courseslistbox.get(self.courseslistbox.curselection())
            selection = selection.split()  # we get selection data from the listbox
            if selection[2] in self.columlist:
                selection = selection[0] + " " + selection[1]
            else:
                selection = selection[0] + " " + selection[1] + " " + selection[2]
            self.listboxitems.remove(selection)
            self.listboxselected.insert("end", self.courseslistbox.get(self.courseslistbox.curselection()))
            self.courseslistbox.delete(self.courseslistbox.curselection())

    def del_course(self):
        try:
            selection = self.listboxselected.get(self.listboxselected.curselection())
            selection = selection.split()                #we get selection data from the listbox
            if selection[2] in self.columlist:
                selection = selection[0] + " " + selection[1]
            else:
                selection = selection[0] + " " + selection[1] + " " + selection[2]
            for course in self.activelessons:               #we iterate through the data of active lessons and find its cell data so we can reset them
                if course.name == selection:
                    for cell in self.activelessons[course]:
                        cell.widget.configure(bg="green")
                        cell.widget.configure(text="")
                        if cell.color not in self.colors:       #if the rand color we picked (which was removed when we picked it) is not there it replaces it
                            self.colors.append(cell.color)
                        cell.color = "X"
                        cell.course = "X"
                    self.listboxitems.append(selection)
                    self.courseslistbox.insert("end", self.listboxselected.get(self.listboxselected.curselection()))       #removes item from listbox
                    self.listboxselected.delete(self.listboxselected.curselection())
        except:
            pass

    def initUI(self):  # GUI START
        self.mainlabel = Label(self, text="SEHIR COURSE PLANNER", fg="white", font="Windsor 24 bold", bg="#337DFF")
        self.mainlabel.pack(fill=X)

        self.urlframe = Frame(self)
        self.urlframe.pack(pady=10)
        self.urllabel = Label(self.urlframe, text="Course Offerings URL: ",font="Windsor 12 bold")
        self.urllabel.grid(row=0,column=0)
        self.urltextbox = Text(self.urlframe, height=1, width=120)
        self.urltextbox.grid(row=0,column=1)
        self.urltextbox.insert('1.0', 'https://www.sehir.edu.tr/tr/duyurular/2019_2020_akademik_yili_bahar_donemi_ders_programi')
        self.urlbutton = Button(self.urlframe, text="Fetch Courses",font="Windsor 12", command=self.fetch_courses)  # set the button to search
        self.urlbutton.grid(row=0,column=2,padx=50)

        self.coursesframe = Frame(self,borderwidth=2, relief=GROOVE)
        self.coursesframe.pack()

        self.filterframe = Frame(self.coursesframe)
        self.filterframe.grid(pady=5,padx=10)
        self.filterframetop = Frame(self.filterframe)
        self.filterframetop.pack()
        self.filterlabel = Label(self.filterframetop,text="Filter: ",font="Windsor 12 bold")
        self.filterlabel.grid(row=0,column=0)
        self.search_var = StringVar()
        self.search_var.trace("w", self.update_list)
        self.urltextbox = Entry(self.filterframetop,width=40,textvariable=self.search_var)
        self.urltextbox.grid(row=0,column=1)
        self.filterframebottom = Frame(self.filterframe)
        self.filterframebottom.pack()
        self.scrollbar = Scrollbar(self.filterframebottom)
        self.scrollbar.pack(side=RIGHT,fill=Y)
        self.courseslistbox = Listbox(self.filterframebottom,width=80,height=4,yscrollcommand = self.scrollbar.set)
        self.courseslistbox.bind("<<ListboxSelect>>",lambda x: self.check_availability())
        self.courseslistbox.pack()
        self.scrollbar.config(command=self.courseslistbox.yview)

        self.addremoveframe = Frame(self.coursesframe)
        self.addremoveframe.grid(row=0,column=1)
        self.addbutton = Button(self.addremoveframe,text="Add",font="Windsor 8 bold", command= self.add_course)
        self.addbutton.grid(row=0,column=0,pady=5)
        self.removebutton = Button(self.addremoveframe, text="Remove",font="Windsor 8 bold", command=self.del_course)
        self.removebutton.grid(row=1,column=0)

        self.selectedcoursesframe = Frame(self.coursesframe)
        self.selectedcoursesframe.grid(row=0,column=2,padx= 10)
        self.courseslabel = Label(self.selectedcoursesframe,text="Selected Courses",font="Windsor 12 bold")
        self.courseslabel.pack()
        self.scrollbar2 = Scrollbar(self.selectedcoursesframe)
        self.scrollbar2.pack(side=RIGHT, fill=Y)
        self.listboxselected = Listbox(self.selectedcoursesframe,height=4, width= 80,yscrollcommand = self.scrollbar2.set)
        self.listboxselected.pack()
        self.scrollbar2.config(command=self.listboxselected.yview)

        self.cellframe = Frame(self)
        self.cellframe.pack(fill=BOTH,pady=20,padx=100)
        curcolumn = 0
        currow = 0
        self.widgetdic = {}
        self.columlist = ["X", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]    #these lists will help me parse time data and allow me to find the time because each cell is not given
        self.rowlist = ["X", "09:00 - 09:30", "09:30 - 10:00", "10:00 - 10:30", "10:30 - 11:00", "11:00 - 11:30","11:30 - 12:00", "12:00 - 12:30", "12:30 - 13:00", "13:00 - 13:30", "13:30 - 14:00", "14:00 - 14:30","14:30 - 15:00", "15:00 - 15:30", "15:30 - 16:00", "16:00 - 16:30", "16:30 - 17:00","17:00 - 17:30", "17:30 - 18:00", "18:00 - 18:30", "18:30 - 19:00", "19:00 - 19:30","19:30 - 20:00","20:00 - 20:30", "20:30 - 21:00", "21:00 - 21:30", "21:30 - 22:00", ]
        for column in self.columlist:
            curcolumn += 1      #i pack around 260 cell widgets here and create cell objects and store them in widget dictionary with their relative cell objects.
            for row in self.rowlist:
                currow += 1
                adress = "col"+str(curcolumn)+"row"+str(currow)
                self.current_label = Label(self.cellframe, bg="green", width=20)
                self.current_label.grid(row=currow, column=curcolumn,padx=2,pady=2)
                if curcolumn == 1:
                    cellobject = Cell("X","X","X",self.current_label,"X")
                    self.current_label.config(text=row,bg="#337DFF",font="Windsor 9 bold")
                    self.widgetdic[adress] = cellobject
                if currow == 1:
                    cellobject = Cell("X","X","X",self.current_label,"X")
                    self.current_label.config(text=column,bg="#337DFF",font="Windsor 9 bold")
                    self.widgetdic[adress] =cellobject
                else:
                    cellobject = Cell(column,row,"X",self.current_label,"X")
                    self.widgetdic[adress] = cellobject
            currow=0
        self.statuslabel = Label(self,text="Status: Not Fetched", bg="#337DFF",font="Windsor 10 bold")
        self.statuslabel.pack()

        self.pack(fill=BOTH,expand=TRUE)
class Course:
    def __init__(self,name, day, time):
        self.name = name
        self.day = day
        self.time = time

class Cell:
    def __init__(self, day, time, course,widget,color):
        self.day = day
        self.time = time
        self.course = course
        self.widget = widget
        self.color = color

root = Tk()
root.title("Course Planner")
root.geometry("1400x1000")
app = GUI(root)
root.mainloop()












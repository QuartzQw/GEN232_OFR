from tkinter import *
from tkinter import ttk
from tkinter import filedialog
import glob

templateDict = {}

def getFilePath(entry):
    entry.delete(0,END)
    templateTextBox.delete(1.0, END)
    templateDir = filedialog.askopenfilename(filetypes = [('JSON', '.json')])
    entry.insert(0, templateDir)
    jsonContent = open(templateDir, encoding="utf8").read()
    templateTextBox.insert(2.0, jsonContent)

def getFolderPath(entry):
    entry.delete(0,END)
    fileNameTextBox.delete(0,END)
    folderDir = filedialog.askdirectory()
    entry.insert(0, folderDir)
    fileNames = glob.glob(f"{folderDir}/*.jpg")
    for name in fileNames:
        fileNameTextBox.insert(END, name)
    # ttk.Label(root, text=folderDir).grid(column=4, row=2)

def getEntriesValues(*entries):
    entryRecord = []
    for entry in entries:
        entryRecord.append(entry.get())
    return entryRecord

def readMainPage(entryTemplate, entryTargetFolder):
    templateDir, folderDir = getEntriesValues(entryTemplate, entryTargetFolder)
    print(open(templateDir, encoding="utf8").read())
    ## print all file names in folderDir

# def createNewQuestion():
#     createNewQuestionWindow = Tk()
#     createNewQuestionWindow.title("create question")
#     question = StringVar()
#     Entry(root, textvariable = question)
#     btnCreatechoice = ttk.Button(createNewQuestionWindow, text="Add choice",command=createNewQuestion)
#     btnCreate.grid(column=0, row = 0)
#     return question.get()

# ##################################

# def showQuestion(editTemplateWindow):
#     templateDir = getFilePath()
#     jsonContent = open(templateDir, encoding="utf8").read()
#     # print(jsonContent)
#     ttk.Label(editTemplateWindow, text = jsonContent).grid(column=2, row= 3)

# def openEditTemplateWindow():
#     editTemplateWindow = Tk()
#     editTemplateWindow.title("Manage questions")
#     editTemplateWindow.geometry("500x360")

#     # btnCreate = ttk.Button(editTemplateWindow, text="Create form template...")
#     # btnCreate.grid(column=1, row = 1)

#     ttk.Label(editTemplateWindow, text="Select target template: ").grid(column=1, row= 1)
#     ttk.Button(editTemplateWindow, text="Path...", command=showQuestion(editTemplateWindow)).grid(column=3, row=1)

#     ttk.Button(editTemplateWindow, text="Save", command=editTemplateWindow.destroy).grid(column=1, row=5)
#     editTemplateWindow.mainloop()

# ############################

root = Tk()
root.title("Optical Form Recognition")
root.geometry("720x360+0+0")

tab = Menu() 
root.config(menu=tab)

subTabTemplate = Menu()
# subTabTemplate.add_command(label = "new template")
# subTabTemplate.add_command(label = "edit template", command=openEditTemplateWindow)

tab.add_cascade(label="Template", menu = subTabTemplate)

entryTemplate = Entry(root, width = 70)
entryTemplate.place(x = 250, y = 10)
Label(root, text="Upload form template").place(x = 10, y = 10)
btnFind = Button(root, text="Upload",command = lambda:getFilePath(entryTemplate))
btnFind.place(x = 150, y = 5)

entryTargetFolder = Entry(root, width = 70)
entryTargetFolder.place(x = 250, y = 40)
Label(root, text="Select written form folder").place(x = 10, y = 40)
btnFind = Button(root, text="Open Folder...",command = lambda:getFolderPath(entryTargetFolder))
btnFind.place(x = 150, y = 35)

Label(root, text="template file (.json):").place(x = 10, y = 75)
templateTextBox = Text(root, width = 40, height = 10)
templateTextBox.place(x = 40, y = 100)

Label(root, text="file(s) in target path:").place(x = 380, y = 75)
fileNameTextBox = Listbox(root, width = 40, height = 10)
fileNameTextBox.place(x = 410, y = 100)

Button(root, text="Submit", command=lambda:readMainPage(entryTemplate, entryTargetFolder), height= 2, width = 10).place(x = 300, y = 280)
Button(root, text="Quit", command=root.destroy, height = 2, width = 10).place(x = 400, y = 280)
root.mainloop()
from tkinter import *
from tkinter import ttk
from tkinter import filedialog
import glob
import os
from PIL import Image, ImageTk
import pandas as pd
from datetime import datetime
from showimg import ImageViewer
from saveToExcel import process_survey

templateDict = {}

def getFilePath(entry):
    """ เปิดไฟล์ JSON และแสดงเนื้อหา """
    entry.delete(0, END)
    if 'templateTextBox' in globals() and templateTextBox:
        templateTextBox.delete(1.0, END)
    
    templateDir = filedialog.askopenfilename(filetypes=[('JSON', '.json')], initialdir='./')
    entry.insert(0, templateDir)
    
    if templateDir:
        with open(templateDir, encoding="utf8") as file:
            jsonContent = file.read()
        if templateTextBox:
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

def readMainPage(entryCoordTemplate, entryTargetFolder):
    """ อ่านข้อมูลจาก JSON และประมวลผลภาพ """
    templateDir, folderDir = entryCoordTemplate.get(), entryTargetFolder.get()
    
    if not os.path.exists(templateDir):
        print("ไม่พบไฟล์ JSON กรุณาเลือกใหม่")
        return

    if not os.path.exists(folderDir):
        print("ไม่พบโฟลเดอร์รูปภาพ กรุณาเลือกใหม่")
        return

    # สร้างโฟลเดอร์สำหรับเก็บไฟล์ Excel
    excel_folder = "./GEN232_OFR/excelCollector"
    if not os.path.exists(excel_folder):
        os.makedirs(excel_folder)
    
    # กำหนดชื่อไฟล์ Excel ตามวันที่ปัจจุบัน
    current_time = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    output_excel = os.path.join(excel_folder, f"SurveyOnMultidimensionalPovertyIndex_{current_time}.xlsx")

    process_survey(folderDir, templateDir, output_excel)

# def readMainPage(entryCoordTemplate, entryTargetFolder):
#     templateDir, folderDir = getEntriesValues(entryCoordTemplate, entryTargetFolder)
#     print(open(templateDir, encoding="utf8").read())
    # os.system('.\generate"')
    ## print all file names in folderDir

# def genDocFromJson():
#     genDocWindow = Tk()
#     genDocWindow.title("json to docx")
#     genDocWindow.geometry("720x360+720+360")
#     entryTemplate = Entry(genDocWindow, width = 70)
#     entryTemplate.place(x = 250, y = 10)
#     Label(genDocWindow, text="Upload form template").place(x = 10, y = 10)
#     btnTemplate = Button(genDocWindow, text="Upload",command = lambda:getFilePath(entryTemplate))  
#     btnTemplate.place(x = 150, y = 5)
#     Button(genDocWindow, text="Quit", command=genDocWindow.destroy, height = 2, width = 10).place(x = 400, y = 100)

# def createNewQuestion():
#     createNewQuestionWindow = Tk()
#     createNewQuestionWindow.title("create question")
#     question = StringVar()
#     Entry(root, textvariable = question)
#     btnCreatechoice = ttk.Button(createNewQuestionWindow, text="Add choice",command=createNewQuestion)
#     btnCreate.grid(column=0, row = 0)
#     return question.get()

def open_image_viewer():
    """ เปิด ImageViewer และส่ง path ของไฟล์ Excel ล่าสุด """
    folder_path = entryTargetFolder.get()
    excel_folder = "./GEN232_OFR/excelCollector"

    if not os.path.exists(folder_path):
        print("กรุณาเลือกโฟลเดอร์ที่มีรูปภาพก่อน")
        return
    
    # หาไฟล์ Excel ล่าสุด
    excel_files = sorted(glob.glob(f"{excel_folder}/*.xlsx"), key=os.path.getctime, reverse=True)
    
    if not excel_files:
        print("ไม่พบไฟล์ Excel ในโฟลเดอร์")
        return

    latest_excel = excel_files[0]  # ใช้ไฟล์ Excel ล่าสุด

    # เปิด ImageViewer และส่ง path ของ Excel
    ImageViewer(root, folder_path, latest_excel)


root = Tk()
root.title("Optical Form Recognition")
root.geometry("720x360+0+0")

tab = Menu() 
root.config(menu=tab)

subTabTemplate = Menu()
# subTabTemplate.add_command(label = "new template")
# subTabTemplate.add_command(label = "edit template", command=openEditTemplateWindow)
# subTabTemplate.add_command(label = "generate docx from json", command=genDocFromJson)
# subTabTemplate.add_command(label = "embed coord to docx")

tab.add_cascade(label="Template", menu = subTabTemplate)

templateTextBox = Text(root, width=40, height=10)
templateTextBox.place(x=40, y=100)

entryCoordTemplate = Entry(root, width = 70)
entryCoordTemplate.place(x = 250, y = 10)
Label(root, text="Upload form template").place(x = 10, y = 10)
btnFind = Button(root, text="Upload",command = lambda:getFilePath(entryCoordTemplate))
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

Button(root, text="Submit", command=lambda:readMainPage(entryCoordTemplate, entryTargetFolder), height= 2, width = 10).place(x = 300, y = 280)
Button(root, text="Quit", command=root.destroy, height = 2, width = 10).place(x = 400, y = 280)
Button(root, text="Open Image Viewer", command=open_image_viewer, height=2, width=15).place(x=550, y=280)

root.mainloop()
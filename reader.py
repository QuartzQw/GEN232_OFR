import tkinter as tk
from tkinter import filedialog, ttk
import glob
import os
from PIL import Image, ImageTk
import pandas as pd
from datetime import datetime
from showimg import ImageViewer
import pickle
from saveToExcel import process_survey

templateDict = {}

def getFilePath(entry):
    """ open pointer file """
    entry.delete(0, tk.END)
    if 'templateTextBox' in globals() and templateTextBox:
        templateTextBox.delete(1.0, tk.END)
    
    templateDir = filedialog.askopenfilename(filetypes=[('DAT', '.dat')], initialdir='./')
    entry.insert(0, templateDir)
    
    if templateDir:
         with open(templateDir, "rb") as f:
            realCoords = pickle.load(f)
            # print(realCoords)
            if templateTextBox:
                templateTextBox.insert(2.0, realCoords)

def getFolderPath(entry):
    entry.delete(0, tk.END)
    fileNameTextBox.delete(0, tk.END)
    folderDir = filedialog.askdirectory()
    entry.insert(0, folderDir)
    fileNames = glob.glob(f"{folderDir}/*.jpg")
    for name in fileNames:
        fileNameTextBox.insert(tk.END, name)
    # ttk.Label(root, text=folderDir).grid(column=4, row=2)

def getEntriesValues(*entries):
    entryRecord = []
    for entry in entries:
        entryRecord.append(entry.get())
    return entryRecord

def readMainPage(entryCoordTemplate, entryTargetFolder):
    """ อ่านข้อมูลจาก dat และประมวลผลภาพ """
    templateDir, folderDir = entryCoordTemplate.get(), entryTargetFolder.get()
    
    if not os.path.exists(templateDir):
        tk.messagebox.showinfo(title = "System", message = "ไม่พบไฟล์พิกัด (.dat) กรุณาเลือกใหม่")
        return

    if not os.path.exists(folderDir):
        tk.messagebox.showinfo(title = "System", message = "ไม่พบโฟลเดอร์รูปภาพ กรุณาเลือกใหม่")
        return

    # สร้างโฟลเดอร์สำหรับเก็บไฟล์ Excel
    excel_folder = "./excelCollector"
    if not os.path.exists(excel_folder):
        os.makedirs(excel_folder)

    process_survey(folderDir, templateDir, excel_folder)

def open_image_viewer():
    """ เปิด ImageViewer และส่ง path ของไฟล์ Excel ล่าสุด """
    folder_path = entryTargetFolder.get()
    excel_folder = "./excelCollector"

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


root = tk.Tk()
root.title("Optical Form Recognition - Reader")
root.geometry("720x360+0+0")

templateTextBox = tk.Text(root, width=40, height=10)
templateTextBox.place(x=40, y=100)

entryCoordTemplate = tk.Entry(root, width = 70)
entryCoordTemplate.place(x = 250, y = 10)
tk.Label(root, text="Upload form template").place(x = 10, y = 10)
btnFind = tk.Button(root, text="Upload",command = lambda:getFilePath(entryCoordTemplate))
btnFind.place(x = 150, y = 5)

entryTargetFolder = tk.Entry(root, width = 70)
entryTargetFolder.place(x = 250, y = 40)
tk.Label(root, text="Select written form folder").place(x = 10, y = 40)
btnFind = tk.Button(root, text="Open Folder...",command = lambda:getFolderPath(entryTargetFolder))
btnFind.place(x = 150, y = 35)

tk.Label(root, text="template file (.json):").place(x = 10, y = 75)
templateTextBox = tk.Text(root, width = 40, height = 10)
templateTextBox.place(x = 40, y = 100)

tk.Label(root, text="file(s) in target path:").place(x = 380, y = 75)
fileNameTextBox = tk.Listbox(root, width = 40, height = 10)
fileNameTextBox.place(x = 410, y = 100)

tk.Button(root, text="Submit", command=lambda:readMainPage(entryCoordTemplate, entryTargetFolder), height= 2, width = 10).place(x = 300, y = 280)
tk.Button(root, text="Quit", command=root.destroy, height = 2, width = 10).place(x = 400, y = 280)
tk.Button(root, text="Open Image Viewer", command=open_image_viewer, height=2, width=15).place(x=550, y=280)

root.mainloop()
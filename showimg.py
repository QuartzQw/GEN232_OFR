from tkinter import *
from tkinter import ttk
import glob
import os
import pandas as pd
from PIL import Image, ImageTk

class ImageViewer:
    def __init__(self, root, folder_path, excel_file):
        """ สร้างหน้าต่างใหม่และโหลดรูปจาก path ที่รับมา """
        self.window = Toplevel(root)  
        self.window.title("Image Viewer")
        self.window.geometry("1100x650+5+5")

        self.image_list = glob.glob(f"{folder_path}/*.jpg")  
        self.image_index = 0
        self.excel_file = excel_file
        self.df = pd.read_excel(excel_file) if os.path.exists(excel_file) else pd.DataFrame()

        """ส่วน excel"""
        # Frame
        frame = Frame(self.window)
        frame.place(x=20, y=20, width=550, height=550)
        # สร้าง Treeview (ตาราง Excel)
        self.tree = ttk.Treeview(frame)
        self.tree.pack(side=LEFT, fill=BOTH, expand=True)

        # Scrollbar แนวตั้ง
        self.scrollbar_y = ttk.Scrollbar(frame, orient=VERTICAL, command=self.tree.yview)
        self.scrollbar_y.pack(side=RIGHT, fill=Y)
        self.tree.configure(yscrollcommand=self.scrollbar_y.set)
        # Scrollbar แนวนอน
        self.scrollbar_x = ttk.Scrollbar(self.window, orient=HORIZONTAL, command=self.tree.xview)
        self.scrollbar_x.place(x=20, y=570, width=550)
        self.tree.configure(xscrollcommand=self.scrollbar_x.set)

        # เชื่อม Scrollbar กับ MouseWheel (เลื่อนขึ้น-ลง)
        self.tree.bind("<MouseWheel>", self.on_vertical_scroll)
        # เชื่อม `Shift + MouseWheel` กับการเลื่อน ซ้าย-ขวา
        self.tree.bind("<Shift-MouseWheel>", self.on_horizontal_scroll)

        """ส่วนรูปภาพ"""
        # Canvas สำหรับแสดงรูป
        self.canvas = Canvas(self.window, width=465, height=550)
        self.canvas.place(x=600, y=20)

        # ปุ่มเลื่อนรูป
        Button(self.window, text="<Previous", command=self.prev_image).place(x=750, y=590)
        Button(self.window, text="Next>", command=self.next_image).place(x=850, y=590)

        """โหลดข้อมูล Excel และแสดงภาพแรก"""
        self.load_excel()
        if self.image_list:
            self.show_image()
        else:
            print("Not found img")

    def on_vertical_scroll(self, event):
        """ ปรับการ Scroll ขึ้น-ลง ด้วย MouseWheel """
        if event.delta > 0:
            self.tree.yview_scroll(-5, "units")  # เลื่อนขึ้น
        else:
            self.tree.yview_scroll(5, "units")  # เลื่อนลง

    def on_horizontal_scroll(self, event):
        """ ปรับการ Scroll ซ้าย-ขวา ด้วย Shift + MouseWheel """
        if event.delta > 0:
            self.tree.xview_scroll(-10, "units")  # เลื่อนทางซ้าย
        else:
            self.tree.xview_scroll(10, "units")  # เลื่อนทางขวา

    def load_excel(self):
        """ โหลดข้อมูลจากไฟล์ Excel และแสดงในตาราง """
        if self.df.empty:
            print("Excel file not found or empty")
            return
        
        # ล้างข้อมูลเก่า
        self.tree.delete(*self.tree.get_children())

        # กำหนดหัวตาราง จากคอลัมน์ใน Excel
        self.tree["columns"] = list(self.df.columns)
        self.tree["show"] = "headings"

        for col in self.df.columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=100)

        # เพิ่มข้อมูลลงตาราง
        for i, row in self.df.iterrows():
            self.tree.insert("", "end", values=list(row), iid=i)

    def highlight_row(self):
        """ ระบายสีแถว """
        if self.df.empty:
            return

        self.tree.tag_configure("highlight", background="#d3d3d3")
        self.tree.selection_remove(self.tree.selection())

        if self.image_index < len(self.df):
            self.tree.selection_add(self.image_index)
            self.tree.see(self.image_index)
            self.tree.item(self.image_index, tags=("highlight",))

    def show_image(self):
        """ แสดงรูป และเชื่อมโยงกับแถวใน Excel """
        if self.image_list:
            img_path = self.image_list[self.image_index]

            try:
                img = Image.open(img_path)
                img = img.convert("RGB")  
                original_width, original_height = img.size  

                max_width, max_height = 465, 550
                img.thumbnail((max_width, max_height), Image.LANCZOS)

                new_width, new_height = img.size
                x_offset = (max_width - new_width) // 2
                y_offset = (max_height - new_height) // 2

                self.canvas.delete("all")
                self.img_tk = ImageTk.PhotoImage(img)  
                self.canvas.create_image(x_offset, y_offset, anchor=NW, image=self.img_tk)

                # ไฮไลท์แถว
                self.highlight_row()

            except Exception as e:
                print(f"error : is can't load img {e}")

    def next_image(self):
        """ แสดงภาพถัดไป และอัปเดตตาราง """
        if self.image_list and self.image_index < len(self.image_list) - 1:
            self.image_index += 1
            self.show_image()

    def prev_image(self):
        """ แสดงภาพก่อนหน้า และอัปเดตตาราง """
        if self.image_list and self.image_index > 0:
            self.image_index -= 1
            self.show_image()

import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk, ImageDraw
import pickle
import fitz
import os
import glob
from datetime import datetime
from ver2_SaveToExcel import process_survey
import pandas as pd
import shutil

# === Global Vars ===
pdfImages = []
batchPages = []
pageSizes = []
realCoordsList = []
currentBatchIndex = 0
imageListTk = []
TEMP_DIR = "./temp"
offsets_by_page = {}
overlay_window = None

# === Init GUI ===
root = tk.Tk()
root.title("Optical Form Recognition - Reader")
root.geometry("820x480+0+0")

if not os.path.exists(TEMP_DIR):
    os.makedirs(TEMP_DIR)

def cleanup_temp_images():
    for file in glob.glob(os.path.join(TEMP_DIR, "temp_pdf_page_*.jpg")):
        try:
            os.remove(file)
        except Exception as e:
            print(f"Failed to delete {file}: {e}")

def on_close():
    # === ลบภาพ temp
    for file in glob.glob(os.path.join(TEMP_DIR, "temp_pdf_page_*.jpg")):
        try:
            os.remove(file)
        except Exception as e:
            print(f"Failed to delete {file}: {e}")

    # === ลบทั้งโฟลเดอร์ temp
    if os.path.exists(TEMP_DIR):
        try:
            shutil.rmtree(TEMP_DIR)
        except Exception as e:
            print(f"Failed to remove TEMP_DIR: {e}")

    # === ลบ tempArea
    if os.path.exists("./tempArea"):
        try:
            shutil.rmtree("./tempArea")
        except Exception as e:
            print(f"Failed to remove tempArea: {e}")

    # === ลบ check_structure.xlsx ถ้ามี
    if os.path.exists("check_structure.xlsx"):
        try:
            os.remove("check_structure.xlsx")
        except Exception as e:
            print(f"Failed to delete check_structure.xlsx: {e}")

    root.destroy()

root.protocol("WM_DELETE_WINDOW", on_close)

# === PDF/Image Loader ===
def convert_pdf_to_images_with_size(pdf_path):
    cleanup_temp_images()
    doc = fitz.open(pdf_path)
    image_paths = []
    sizes = []
    for i, page in enumerate(doc):
        pix = page.get_pixmap(dpi=150)
        img_path = os.path.join(TEMP_DIR, f"temp_pdf_page_{i}.jpg")
        pix.save(img_path)
        image_paths.append(img_path)
        sizes.append((int(page.rect.width), int(page.rect.height)))
    return image_paths, sizes

def getFilePath(entry):
    global realCoordsList, pageSizes
    entry.delete(0, tk.END)
    path = filedialog.askopenfilename(filetypes=[("DAT file", "*.dat")])
    if path:
        entry.insert(0, path)
        with open(path, "rb") as f:
            data = pickle.load(f)
            realCoordsList = data["pages"]
            pageSizes = data["sizes"]
        try_split_batches()

def getPDFPath(entry):
    global pdfImages
    entry.delete(0, tk.END)
    path = filedialog.askopenfilename(filetypes=[("PDF files", "*.pdf")])
    if path:
        entry.insert(0, path)
        pdfImages, _ = convert_pdf_to_images_with_size(path)
        try_split_batches()

def browseExcel(entry):
    path = filedialog.askopenfilename(filetypes=[("Excel files", "*.xlsx")])
    if path:
        entry.delete(0, tk.END)
        entry.insert(0, path)

# === Batch Logic ===
def try_split_batches():
    global batchPages, currentBatchIndex
    if pdfImages and realCoordsList:
        n = len(realCoordsList)
        batchPages = [pdfImages[i:i+n] for i in range(0, len(pdfImages), n)]
        currentBatchIndex = 0
        show_preview_images()

def show_preview_images():
    global imageListTk
    for widget in frame_preview.winfo_children():
        widget.destroy()
    imageListTk.clear()
    if currentBatchIndex >= len(batchPages): return
    pages = batchPages[currentBatchIndex]
    for img_path in pages:
        img = Image.open(img_path)
        img.thumbnail((180, 250), Image.LANCZOS)
        imgTk = ImageTk.PhotoImage(img)
        lbl = tk.Label(frame_preview, image=imgTk)
        lbl.image = imgTk
        lbl.pack(side="left", padx=5)
        imageListTk.append(imgTk)

def next_batch():
    global currentBatchIndex
    if currentBatchIndex < len(batchPages) - 1:
        currentBatchIndex += 1
        show_preview_images()

def prev_batch():
    global currentBatchIndex
    if currentBatchIndex > 0:
        currentBatchIndex -= 1
        show_preview_images()

# === Overlay ===
def get_image_and_coords(img_index, image_paths, realCoordsList):
    image = Image.open(image_paths[img_index])
    coords_list = realCoordsList[img_index % len(realCoordsList)]
    return image, coords_list

def open_overlay_window():
    global overlay_window
    overlay_window = tk.Toplevel(root)
    overlay_window.title("Overlay Preview")
    overlay_window.geometry("800x850")

    page_index = tk.IntVar(value=0)
    x_offset = tk.IntVar(value=0)
    y_offset = tk.IntVar(value=0)
    zoom_scale = 1.0

    # === Canvas + Scrollbars ===
    canvas_frame = tk.Frame(overlay_window)
    canvas_frame.pack(fill="both", expand=True)

    canvas = tk.Canvas(canvas_frame, bg="white")
    canvas.grid(row=0, column=0, sticky="nsew")

    v_scroll = tk.Scrollbar(canvas_frame, orient="vertical", command=canvas.yview)
    v_scroll.grid(row=0, column=1, sticky="ns")
    h_scroll = tk.Scrollbar(canvas_frame, orient="horizontal", command=canvas.xview)
    h_scroll.grid(row=1, column=0, sticky="ew")

    canvas.configure(yscrollcommand=v_scroll.set, xscrollcommand=h_scroll.set)
    canvas_frame.rowconfigure(0, weight=1)
    canvas_frame.columnconfigure(0, weight=1)

    def draw_overlay():
        canvas.delete("all")
        img_idx = currentBatchIndex * len(realCoordsList) + page_index.get()
        all_images = [img for batch in batchPages for img in batch]
        if img_idx >= len(all_images): return

        img, coords = get_image_and_coords(img_idx, all_images, realCoordsList)
        w, h = img.size
        draw = ImageDraw.Draw(img)

        x_off = x_offset.get()
        y_off = y_offset.get()
        offsets_by_page[page_index.get()] = (x_off, y_off)

        for coord in coords:
            x1 = coord[0] * w + x_off
            y1 = coord[1] * h + y_off
            x2 = coord[2] * w + x_off
            y2 = coord[3] * h + y_off
            color = "blue" if coord[4] == "image" else "green" if coord[4] == "number" else "red"
            draw.rectangle([x1, y1, x2, y2], outline=color, width=2)

        resized_img = img.resize((int(w * zoom_scale), int(h * zoom_scale)))
        imgTk = ImageTk.PhotoImage(resized_img)
        canvas.image = imgTk

        canvas_width = canvas.winfo_width()
        canvas_height = canvas.winfo_height()

        center_x = max(0, (canvas_width - imgTk.width()) // 2)
        center_y = max(0, (canvas_height - imgTk.height()) // 2)

        canvas.create_image(center_x, center_y, anchor="nw", image=imgTk)
        canvas.config(scrollregion=canvas.bbox("all"))

    def zoom(delta):
        nonlocal zoom_scale
        zoom_scale = max(0.5, min(2.5, zoom_scale + delta))
        draw_overlay()

    def change_page(delta):
        page_index.set(max(0, min(page_index.get() + delta, len(batchPages[currentBatchIndex]) - 1)))
        draw_overlay()

    def change_batch(delta):
        global currentBatchIndex
        currentBatchIndex = max(0, min(currentBatchIndex + delta, len(batchPages) - 1))
        page_index.set(0)
        draw_overlay()

    # === Controls ===
    control = tk.Frame(overlay_window)
    control.pack(fill="x", pady=5)

    # LEFT
    left_frame = tk.Frame(control)
    left_frame.pack(side="left", anchor="w", padx=10)
    tk.Label(left_frame, text="X Offset:").pack(side="left")
    tk.Entry(left_frame, textvariable=x_offset, width=5).pack(side="left", padx=(0, 10))
    tk.Label(left_frame, text="Y Offset:").pack(side="left")
    tk.Entry(left_frame, textvariable=y_offset, width=5).pack(side="left", padx=(0, 10))
    tk.Button(left_frame, text="Apply Offset", command=draw_overlay).pack(side="left", padx=(0, 20))

    # CENTER
    center_frame = tk.Frame(control)
    center_frame.pack(side="left", expand=True)
    tk.Button(center_frame, text="Zoom -", command=lambda: zoom(-0.15)).pack(side="left", padx=5)
    tk.Button(center_frame, text="Zoom +", command=lambda: zoom(0.15)).pack(side="left", padx=5)

    # RIGHT
    right_frame = tk.Frame(control)
    right_frame.pack(side="right", anchor="e", padx=10)
    tk.Button(right_frame, text="< Batch", command=lambda: change_batch(-1)).pack(side="left", padx=2)
    tk.Button(right_frame, text="Batch >", command=lambda: change_batch(1)).pack(side="left", padx=10)
    tk.Button(right_frame, text="< Page", command=lambda: change_page(-1)).pack(side="left", padx=2)
    tk.Button(right_frame, text="Page >", command=lambda: change_page(1)).pack(side="left", padx=2)

    overlay_window.after(50, draw_overlay)

# === Save to Excel ===
def save_excel():
    if not entryCoordTemplate.get() or not entryTargetPDF.get():
        messagebox.showwarning("Warning", "Please upload .dat and PDF before saving.")
        return

    image_folder = os.path.dirname(pdfImages[0]) if pdfImages else "./"
    templateDir = entryCoordTemplate.get()
    output_path = filedialog.asksaveasfilename(defaultextension=".xlsx")

    if not output_path:
        return

    old_excel_path = entryOldExcel.get()
    if old_excel_path and os.path.exists(old_excel_path):
        try:
            old_df = pd.read_excel(old_excel_path)
            new_df = pd.DataFrame(columns=old_df.columns)
            new_df.to_excel("check_structure.xlsx", index=False)
            with open(templateDir, "rb") as f:
                data = pickle.load(f)
            template_fields = [coord[5] for page in data["pages"] for coord in page]
            if not set(old_df.columns).issuperset(set(template_fields)):
                answer = messagebox.askyesno("Column Mismatch","คอลัมน์ใน Excel เดิมไม่ตรงกับฟอร์มคุณต้องการสร้างไฟล์ใหม่หรือไม่?")
                if not answer:
                    return
                else:
                    old_excel_path = None  # fallback to new file
        except Exception as e:
            messagebox.showerror("Error", f"ไม่สามารถอ่าน Excel เดิม: {e}")
            return

    process_survey(image_folder, templateDir, output_path, offsets_by_page, show_alert=True, append_excel_path=entryOldExcel.get())

# === GUI Layout ===
entryCoordTemplate = tk.Entry(root, width=70)
entryCoordTemplate.place(x=260, y=10)
tk.Label(root, text="Upload form template").place(x=10, y=10)

entryTargetPDF = tk.Entry(root, width=70)
entryTargetPDF.place(x=260, y=40)
tk.Label(root, text="Upload filled PDF").place(x=10, y=40)

entryOldExcel = tk.Entry(root, width=70)
entryOldExcel.place(x=260, y=70)
tk.Label(root, text="Use existing Excel (optional)").place(x=10, y=70)

tk.Button(root, text="Upload .dat", command=lambda: getFilePath(entryCoordTemplate)).place(x=170, y=5)
tk.Button(root, text="Upload PDF", command=lambda: getPDFPath(entryTargetPDF)).place(x=170, y=35)
tk.Button(root, text="Browse Excel", command=lambda: browseExcel(entryOldExcel)).place(x=170, y=65)
tk.Button(root, text="< Prev Batch", command=prev_batch).place(x=150, y=100)
tk.Button(root, text="Next Batch >", command=next_batch).place(x=270, y=100)
tk.Button(root, text="Show Overlay", command=open_overlay_window).place(x=400, y=100)
tk.Button(root, text="Save to Excel", command=save_excel).place(x=600, y=100)

scroll_canvas = tk.Canvas(root, height=260)
scroll_canvas.place(x=10, y=140, width=790)
frame_preview = tk.Frame(scroll_canvas)
scroll_canvas.create_window((0, 0), window=frame_preview, anchor="nw")
scrollbar_x = tk.Scrollbar(root, orient="horizontal", command=scroll_canvas.xview)
scrollbar_x.place(x=10, y=400, width=790)
scroll_canvas.configure(xscrollcommand=scrollbar_x.set)
scroll_canvas.bind_all("<Shift-MouseWheel>", lambda e: scroll_canvas.xview_scroll(-3 if e.delta > 0 else 3, "units"))
frame_preview.bind("<Configure>", lambda event: scroll_canvas.configure(scrollregion=scroll_canvas.bbox("all")))

root.mainloop()


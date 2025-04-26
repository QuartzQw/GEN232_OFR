import tkinter as tk
from tkinter import filedialog, ttk, messagebox
from PIL import Image, ImageTk
from ver2_AutoTrack import scan
import pickle
from datetime import datetime
import os
import fitz
import copy

# Global variables
ix = iy = index = -1
coords = []
realCoords = []
drawStat = False
resolutionValue = 0
imgPath = None
image = None
pdfPages = []
pageSizes = []
currentPage = 0
pageRealCoords = []
undoStack = []

def convert_pdf_to_images_with_size(pdf_path):
    doc = fitz.open(pdf_path)
    image_paths = []
    sizes = []
    for i, page in enumerate(doc):
        pix = page.get_pixmap(dpi=200)
        img_path = f"./temp_pdf_page_{i}.jpg"
        pix.save(img_path)
        image_paths.append(img_path)
        sizes.append((page.rect.width, page.rect.height))
    return image_paths, sizes

def handleFileInput(entry, setup_callback):
    global imgPath, pdfPages, currentPage, pageRealCoords, pageSizes
    entry.delete(0, tk.END)
    file_path = filedialog.askopenfilename(filetypes=[("Image or PDF", (".jpg", ".pdf"))], initialdir="./")
    entry.insert(0, file_path)
    imgPath = file_path

    if file_path.endswith(".pdf"):
        pdfPages, pageSizes = convert_pdf_to_images_with_size(file_path)
        pageRealCoords = [[] for _ in range(len(pdfPages))]
        currentPage = 0
        setup_callback(pdfPages[currentPage])
    else:
        pdfPages = [file_path]
        pageSizes = [(1, 1)]
        pageRealCoords = [[]]
        currentPage = 0
        setup_callback(file_path)

def loadPointerFile():
    global pageRealCoords, realCoords, coords
    if not pdfPages:
        messagebox.showwarning("Warning", "Please upload PDF before loading .dat file.")
        return

    path = filedialog.askopenfilename(filetypes=[("Data file", ".dat")])
    if path:
        with open(path, "rb") as f:
            data = pickle.load(f)
            pageRealCoords = data.get("pages", [])
            if len(pageRealCoords) != len(pdfPages):
                messagebox.showerror("Error", "Mismatch between PDF pages and .dat pages.")
                return

        realCoords = pageRealCoords[currentPage]
        coords[:] = [[rect[0] * formWidth, rect[1] * formHeight,
                      rect[2] * formWidth, rect[3] * formHeight,
                      rect[4], rect[5]] for rect in realCoords]
        setupFormCanva(pdfPages[currentPage])
        drawAllRect(coords)

def goToPage(delta):
    global currentPage, coords, realCoords
    nextPage = currentPage + delta
    if 0 <= nextPage < len(pdfPages):
        currentPage = nextPage
        realCoords = pageRealCoords[currentPage]
        coords = [[rect[0] * formWidth, rect[1] * formHeight,
                   rect[2] * formWidth, rect[3] * formHeight,
                   rect[4], rect[5]] for rect in realCoords]
        setupFormCanva(pdfPages[currentPage])
        drawAllRect(coords)

def drawAllRect(coords):
    formCanv.delete("all")
    formCanv.create_image(0, 0, image=image, anchor="nw")
    for rect in coords:
        color = {"number": "green", "image": "blue", "checkBox": "red", "imageLink": "purple"}.get(rect[4], "black")
        formCanv.create_rectangle(rect[0], rect[1], rect[2], rect[3], width=2, outline=color)

def searchRect(x, y):
    for i, rect in enumerate(coords):
        if rect[0] <= x <= rect[2] and rect[1] <= y <= rect[3]:
            return i, rect
    return -1, 0

def get_xy(event):
    global ix, iy, drawStat, index
    index, rect = searchRect(event.x, event.y)
    if index >= 0:
        drawStat = False
        drawAllRect(coords)
        formCanv.create_rectangle(rect[0], rect[1], rect[2], rect[3], width=2, outline='black')
        entryColumnBox.delete(0, tk.END)
        entryColumnBox.insert(0, coords[index][5])
        dataTypeBox.set(coords[index][4])
    else:
        if not drawStat:
            ix, iy = event.x, event.y
            drawStat = True
        else:
            x1, x2 = sorted([ix, event.x])
            y1, y2 = sorted([iy, event.y])
            box_type = "checkBox" if 0.8 <= (x2 - x1) / (y2 - y1) <= 1.2 else "image"
            undoStack.append((copy.deepcopy(coords), copy.deepcopy(realCoords)))
            field_index = len(realCoords)
            field_name = f"page_{currentPage}_{field_index}"
            coords.append([x1, y1, x2, y2, box_type, field_name])
            realCoords.append([x1 / formWidth, y1 / formHeight,
                               x2 / formWidth, y2 / formHeight,
                               box_type, field_name, None])
            drawStat = False
            drawAllRect(coords)

def del_element(event):
    global drawStat
    drawStat = False
    idx = next((i for i, rect in enumerate(coords)
                if rect[0] <= event.x <= rect[2] and rect[1] <= event.y <= rect[3]), -1)
    if idx != -1:
        undoStack.append((copy.deepcopy(coords), copy.deepcopy(realCoords)))
        del coords[idx]
        del realCoords[idx]
        drawAllRect(coords)

def undoDraw(event=None):
    global coords, realCoords
    if undoStack:
        coords, realCoords = undoStack.pop()
        drawAllRect(coords)

def autoDetectPress(imgPath, imgWidth, imgHeight, **params):
    global realCoords, coords
    undoStack.append((copy.deepcopy(coords), copy.deepcopy(realCoords)))
    detected = scan(
        file_path=imgPath,
        img_width=imgWidth,
        img_height=imgHeight,
        resolution=params["resolution"].get(),
        block_size=params["blockSize"].get(),
        c_val=params["cVal"].get(),
        min_area=params["minArea"].get()
    )
    for i, coord in enumerate(detected):
        coord[5] = f"page_{currentPage}_{i}"
        if len(coord) < 7:
            coord.append(None)
    pageRealCoords[currentPage] = detected
    realCoords = detected
    coords[:] = [[
        r[0] * formWidth, r[1] * formHeight,
        r[2] * formWidth, r[3] * formHeight,
        r[4], r[5]
    ] for r in realCoords]
    drawAllRect(coords)

def updateColName(entry, box, idx):
    if 0 <= idx < len(coords):
        name = entry.get()
        dtype = box.get()
        model = "trocr" if dtype == "text" else "digits-ocr" if dtype == "number" else None
        undoStack.append((copy.deepcopy(coords), copy.deepcopy(realCoords)))
        coords[idx][4], coords[idx][5] = dtype, name
        realCoords[idx][4], realCoords[idx][5], realCoords[idx][6] = dtype, name, model
        drawAllRect(coords)

def smart_sort(rects, line_threshold=0.002):
    rects = sorted(rects, key=lambda r: (r[1], r[0]))  # Sort by y first, then x
    grouped = []
    current_line = []
    last_y = None

    for r in rects:
        if last_y is None or abs(r[1] - last_y) > line_threshold:
            if current_line:
                grouped.append(sorted(current_line, key=lambda r: r[0]))  # Sort x inside the row
            current_line = [r]
            last_y = r[1]
        else:
            current_line.append(r)

    if current_line:
        grouped.append(sorted(current_line, key=lambda r: r[0]))

    sorted_rects = [item for group in grouped for item in group]
    return sorted_rects

def writeFile():
    os.makedirs("generateElement", exist_ok=True)
    path = f"generateElement/boxPointer-{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.dat"
    
    sorted_pages = []
    for page in pageRealCoords:
        sorted_page = smart_sort(page, line_threshold=0.005)
        sorted_pages.append(sorted_page)

    with open(path, "wb") as f:
        pickle.dump({"pages": sorted_pages, "sizes": pageSizes}, f)
    messagebox.showinfo("Saved", f"Template saved to: {os.path.abspath(path)}")

def setupFormCanva(imgPath):
    global image
    img = Image.open(imgPath)
    image = ImageTk.PhotoImage(img.resize((formWidth, formHeight)))
    formCanv.create_image(0, 0, image=image, anchor="nw")
    formCanv.image = image

def on_close():
    for file in os.listdir("."):
        if file.startswith("temp_pdf_page_") and file.endswith(".jpg"):
            try:
                os.remove(file)
            except Exception as e:
                print(f"Error deleting {file}: {e}")
    app.destroy()


# === GUI ===
app = tk.Tk()
app.title('Optical Form Recognition - Pointer')
width, height = app.winfo_screenwidth(), app.winfo_screenheight()
winWidth = int(width * 0.7)
winHeight = int(height * 0.8)
app.geometry(f"{winWidth}x{winHeight}+0+0")

isProtrait = messagebox.askquestion("System", "ฟอร์มขนาดแนวตั้งใช่ หรือไม่")
if(isProtrait == "yes"):
    formHeight = winHeight - 20
    formWidth = int(formHeight / 1.414213)
else:
    formWidth = winHeight - 20
    formHeight = int(formWidth / 1.414213) 

formCanv = tk.Canvas(app, width=formWidth, height=formHeight, bg="white")
formCanv.pack(side="left", padx=10, pady=10)
formCanv.bind("<Button-1>", get_xy)
formCanv.bind("<Button-3>", del_element)
formCanv.bind_all("<Control-z>", undoDraw)

font = ("Helvetica", 10, "bold")
xAuto = formWidth + 50
yAuto = 10
scaleLength = winWidth - formWidth - 350

def uploadTemplate_block():
    tk.Label(app, text="Upload template", font=font).place(x=xAuto, y=yAuto)
    entryCoordTemplate = tk.Entry(app, width=60)
    entryCoordTemplate.place(x=xAuto, y=yAuto + 40)
    tk.Button(app, text="Upload template (.pdf/.jpeg)", command=lambda: handleFileInput(entryCoordTemplate, setupFormCanva)).place(x=xAuto, y=yAuto + 80)
    tk.Button(app, text="Load pointer file (.dat)", command=loadPointerFile).place(x=xAuto + 200, y=yAuto + 80)

def tuneParameter_block():
    parameter_frame = tk.Frame(app)
    parameter_frame.place(x=xAuto, y=yAuto + 120)

    tk.Label(parameter_frame, text="Parameter tuning", font=font).grid(row=0, column=0, columnspan=2, sticky="w")

    # block size
    tk.Label(parameter_frame, text="block size").grid(row=1, column=0, sticky="e", pady=2)
    blockSize = tk.Scale(parameter_frame, from_=3, to=255, resolution=2, orient=tk.HORIZONTAL, length=200)
    blockSize.set(141)
    blockSize.grid(row=1, column=1, padx=5, pady=2)

    # C-value
    tk.Label(parameter_frame, text="C-value").grid(row=2, column=0, sticky="e", pady=2)
    cVal = tk.Scale(parameter_frame, from_=1, to=15, resolution=2, orient=tk.HORIZONTAL, length=200)
    cVal.set(5)
    cVal.grid(row=2, column=1, padx=5, pady=2)

    # min. area
    tk.Label(parameter_frame, text="min. area").grid(row=3, column=0, sticky="e", pady=2)
    minArea = tk.Scale(parameter_frame, from_=0, to=1000, orient=tk.HORIZONTAL, length=200)
    minArea.set(153)
    minArea.grid(row=3, column=1, padx=5, pady=2)

    # resolution
    tk.Label(parameter_frame, text="resolution").grid(row=4, column=0, sticky="e", pady=2)
    resolution = tk.Scale(parameter_frame, from_=1, to=8, orient=tk.HORIZONTAL, length=200)
    resolution.set(3)
    resolution.grid(row=4, column=1, padx=5, pady=2)

    # Buttons
    btn_frame = tk.Frame(parameter_frame)
    btn_frame.grid(row=5, column=0, columnspan=2, pady=10)

    tk.Button(btn_frame, text="Auto detect", command=lambda: autoDetectPress(
        imgPath=pdfPages[currentPage], imgWidth=formWidth, imgHeight=formHeight,
        blockSize=blockSize, cVal=cVal, minArea=minArea, resolution=resolution
    )).pack(side="left", padx=5)

    # รวม Previous กับ Next ไว้ด้วยกัน
    page_nav_frame = tk.Frame(btn_frame)
    page_nav_frame.pack(side="left", padx=20)

    tk.Button(page_nav_frame, text="< Previous", command=lambda: goToPage(-1)).pack(side="left", padx=(100,2))
    tk.Button(page_nav_frame, text="Next >", command=lambda: goToPage(1)).pack(side="left", padx=2)

def updateColumnDetail_block():
    global entryColumnBox, dataTypeBox
    tk.Label(app, text="Column name:", font=font).place(x=xAuto, y=yAuto + 400)
    entryColumnBox = tk.Entry(app, width=30)
    entryColumnBox.place(x=xAuto + 120, y=yAuto + 405)

    tk.Label(app, text="Data Type:", font=font).place(x=xAuto, y=yAuto + 430)
    dataTypeBox = ttk.Combobox(app, values=["image", "number", "checkBox", "imageLink"])
    dataTypeBox.current(0)
    dataTypeBox.place(x=xAuto + 120, y=yAuto + 435)

    tk.Button(app, text="Submit column name", command=lambda: updateColName(entryColumnBox, dataTypeBox, index) if index >= 0 else messagebox.showwarning("Warning", "Please select a box first.")).place(x=xAuto, y=yAuto + 480)
    tk.Button(app, text="Save .dat", command=writeFile).place(x=xAuto + 150, y=yAuto + 480)

uploadTemplate_block()
tuneParameter_block()
updateColumnDetail_block()

app.protocol("WM_DELETE_WINDOW", on_close)
app.mainloop()

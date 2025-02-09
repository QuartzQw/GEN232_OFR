from tkinter import *
from PIL import Image, ImageTk
from testAutoTrack import scan

ix = -1
iy = -1
coords = []
drawStat = False

app = Tk()
Scrollbar(app).pack(side = RIGHT, fill= Y)
width, height = app.winfo_screenwidth(), app.winfo_screenheight()
winWidth = int(width * 0.8)
winHeight = height-100
app.geometry(f"{winWidth}x{winHeight}+0+0")
formHeight = winHeight-50

def get_xy(event):
    global ix, iy, coords, drawStat

    if drawStat == False:
        ix = event.x 
        iy = event.y 
        drawStat = True
    else:
        coords.append([ix, iy, event.x, event.y])
        drawStat = False
    for rect in coords:
        print(coords)
        formCanv.create_rectangle(rect[0], rect[1], rect[2], rect[3], width = 1)

def del_element(event):
    formCanv.create_image(10,10, image = image, anchor = "nw")
    idxToDel = -1
    for i, rect in enumerate(coords):
        if (rect[0] <= event.x <= rect[2] and rect[1] <= event.y <= rect[3]):
            idxToDel = i
        else:
            formCanv.create_rectangle(rect[0], rect[1], rect[2], rect[3], width = 1)
    del coords[idxToDel]

def autoDetectPress(imgPath, imgWidth, imgHeight):
    # print(blockSize.get(), cVal.get(), minArea.get())
    # print(param1.get(), param2.get(), minRad.get(), maxRad.get(), minDist.get())
    scan(filePath = imgPath,
         imgHeight = imgHeight,
         imgWidth = imgWidth,
         blockSize = blockSize.get(),
         cVal = cVal.get(),
         minArea = minArea.get(),
         resolution = resolution.get())

formCanv = Canvas(app)
formCanv.pack(anchor="nw")

formCanv.bind("<Button-1>", get_xy)
formCanv.bind("<Button-3>", del_element)

imgPath = "./data/demo3.jpg"
img = Image.open(imgPath)
scaleFactor = formHeight/img.height
formWidth = int(img.width * scaleFactor)
formHeight = int(img.height * scaleFactor)

formCanv.config(width=formWidth, height= formHeight)
image = img.resize((formWidth, formHeight))
image = ImageTk.PhotoImage(image)
formCanv.create_image(10,10, image = image, anchor = "nw")

# w = Canvas(app, width=200, height=200)
# w.create_rectangle(0,0,50,50)
xAuto = formWidth+50
yAuto = 10
scaleLength = 150
Label(app, text="Parameter tuning for auto-detect").place(x = xAuto, y = yAuto)

Label(app, text="block size").place(x = xAuto+20, y = yAuto+40)
Label(app, text="C-value").place(x = xAuto+20, y = yAuto+80)
Label(app, text="min. area").place(x = xAuto+20, y = yAuto+120)
Label(app, text="resolution").place(x = xAuto+20, y = yAuto+160)
blockSize = Scale(app, from_=3, to=255, length = scaleLength, resolution=2, orient=HORIZONTAL)
blockSize.place(x=xAuto + 80, y= yAuto+20)
cVal = Scale(app, from_=1, to=15, length = scaleLength, resolution=2, orient=HORIZONTAL)
cVal.place(x=xAuto + 80, y= yAuto+60)
minArea = Scale(app, from_=0, to=1000, length = scaleLength, orient=HORIZONTAL)
minArea.place(x=xAuto + 80, y= yAuto+100)
resolution = Scale(app, from_=1, to=8, length = scaleLength, orient=HORIZONTAL)
resolution.place(x=xAuto + 80, y= yAuto+140)

blockSize.set(141)
cVal.set(7)
minArea.set(100)
resolution.set(2)

autoDetect = Button(app, text="Auto detect", command=lambda:autoDetectPress(imgPath=imgPath, imgWidth=formWidth, imgHeight= formHeight))
autoDetect.place(x = xAuto, y = yAuto + 180)

app.mainloop()


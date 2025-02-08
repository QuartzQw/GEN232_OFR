from tkinter import *
from PIL import Image, ImageTk

ix = -1
iy = -1
coords = []
drawStat = False

app = Tk()
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
        canvas.create_rectangle(rect[0], rect[1], rect[2], rect[3], width = 1)

def del_element(event):
    canvas.create_image(10,10, image = image, anchor = "nw")
    idxToDel = -1
    for i, rect in enumerate(coords):
        if (rect[0] <= event.x <= rect[2] and rect[1] <= event.y <= rect[3]):
            idxToDel = i
        else:
            canvas.create_rectangle(rect[0], rect[1], rect[2], rect[3], width = 1)
    del coords[idxToDel]
                 

canvas = Canvas(app)
canvas.pack(anchor="nw")

canvas.bind("<Button-1>", get_xy)
canvas.bind("<Button-3>", del_element)

img = Image.open("./data/demo3.jpg")
scaleFactor = formHeight/img.height
formWidth = int(img.width * scaleFactor)
formHeight = int(img.height * scaleFactor)

canvas.config(width=formWidth, height= formHeight)
image = img.resize((formWidth, formHeight))
image = ImageTk.PhotoImage(image)
canvas.create_image(10,10, image = image, anchor = "nw")

# w = Canvas(app, width=200, height=200)
# w.create_rectangle(0,0,50,50)
xAuto = formWidth+50
yAuto = 10
scaleLength = 150
Label(app, text="Parameter tuning for auto-detect").place(x = xAuto, y = yAuto)

Label(app, text="block size").place(x = xAuto+20, y = yAuto+40)
Label(app, text="C-value").place(x = xAuto+20, y = yAuto+80)
Label(app, text="min. area").place(x = xAuto+20, y = yAuto+120)
btnFind = Button(app, text="Auto detect")
btnFind.place(x = xAuto, y = yAuto + 180)
blockSize = Scale(app, from_=3, to=255, length = scaleLength, resolution=2, orient=HORIZONTAL)
blockSize.place(x=xAuto + 80, y= yAuto+20)
cVal = Scale(app, from_=1, to=15, length = scaleLength, resolution=2, orient=HORIZONTAL)
cVal.place(x=xAuto + 80, y= yAuto+60)
minArea = Scale(app, from_=100, to=10000, length = scaleLength, orient=HORIZONTAL)
minArea.place(x=xAuto + 80, y= yAuto+100)

Label(app, text="param1").place(x = xAuto+280, y = yAuto+40)
Label(app, text="param2").place(x = xAuto+280, y = yAuto+80)
Label(app, text="min. Rad.").place(x = xAuto+280, y = yAuto+120)
Label(app, text="max. Rad.").place(x = xAuto+280, y = yAuto+160)
Label(app, text="min. Dist.").place(x = xAuto+280, y = yAuto+200)
param1 = Scale(app, from_=20, to=200, length = scaleLength, resolution=5, orient=HORIZONTAL)
param1.place(x=xAuto + 340, y= yAuto+20)
param2 = Scale(app, from_=20, to=200, length = scaleLength, resolution=5, orient=HORIZONTAL)
param2.place(x=xAuto + 340, y= yAuto+60)
minRad = Scale(app, from_= 0, to=500, length = scaleLength, resolution=5, orient=HORIZONTAL)
minRad.place(x=xAuto + 340, y= yAuto+100)
maxRad = Scale(app, from_= 0, to=1000, length = scaleLength, resolution=5, orient=HORIZONTAL)
maxRad.place(x=xAuto + 340, y= yAuto+140)
minDist = Scale(app, from_= 0, to=1000, length = scaleLength, resolution=5, orient=HORIZONTAL)
minDist.place(x=xAuto + 340, y= yAuto+180)

app.mainloop()

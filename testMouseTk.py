from tkinter import *
from PIL import Image, ImageTk

ix = -1
iy = -1
coords = []
drawStat = False

app = Tk()
app.geometry("720x1080")

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
canvas.config(width=img.width // 4, height= img.height // 4)
image = img.resize((img.width // 4, img.height // 4))
image = ImageTk.PhotoImage(image)
canvas.create_image(10,10, image = image, anchor = "nw")

app.mainloop()

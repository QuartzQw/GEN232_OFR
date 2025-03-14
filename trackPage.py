from tkinter import *
from PIL import Image, ImageTk
from tkinter import filedialog
from autoTrack import scan, cropToPath
import pickle
from datetime import datetime

ix = -1
iy = -1
coords = []
realCoords = []
drawStat = False
resolutionValue = 0
index = -1
imgPath = "./data/emptyTemplate.jpg"

app = Tk()
Scrollbar(app).pack(side = RIGHT, fill= Y)
width, height = app.winfo_screenwidth(), app.winfo_screenheight()
print(width, height)
winWidth = int(width * 0.6)
winHeight = height-100
app.geometry(f"{winWidth}x{winHeight}+0+0")
formHeight = winHeight-50

def getFilePath(entry):
    """ open pointer file """
    global imgPath
    entry.delete(0, END)
    templateDir = filedialog.askopenfilename(filetypes=[('JPEG', '.jpg')], initialdir='./')
    entry.insert(0, templateDir)
    imgPath = templateDir

def searchRect(x, y):
    for i, rect in enumerate(coords):
        if (rect[0] <= x <= rect[2] and rect[1] <= y <= rect[3]):
            return i, rect
    return -1, 0

def drawAllRect(coords):
    for rect in coords:
        if rect[5] == "-":
            formCanv.create_rectangle(rect[0], rect[1], rect[2], rect[3], width = 2, outline='black')
        else:
            formCanv.create_rectangle(rect[0], rect[1], rect[2], rect[3], width = 2, outline='blue')

def get_xy(event):
    global ix, iy, coords, drawStat, index

    index, rect = searchRect(event.x, event.y)
    if index >= 0:
        drawStat = False
        drawAllRect(coords)

        # draw select box
        formCanv.create_rectangle(rect[0], rect[1], rect[2], rect[3], width = 2, outline='red')
        entryColumnBox.delete(0,END)
        entryColumnBox.insert(0,coords[index][5])
        
    else:
        if drawStat == False:
            ix = event.x 
            iy = event.y 
            formCanv.create_oval(ix,iy,ix,iy,fill="black", width=2)
            drawStat = True
        else:
            choiceType = "text"
            if(1.1 >= (event.x - ix)/(event.y - iy) >= 0.9):
                choiceType = "checkBox"
            coords.append([
                ix,
                iy,
                event.x,
                event.y, 
                choiceType, 
                "-"])
            realCoords.append([
                ix/formWidth, 
                iy/formHeight, 
                event.x/formWidth, 
                event.y/formHeight, 
                choiceType,
                "-"])
            drawStat = False
            drawAllRect(coords)

def del_element(event):
    global drawStat

    drawStat = False
    formCanv.create_image(10,10, image = image, anchor = "nw")
    idxToDel = -1
    for i, rect in enumerate(coords):
        if (rect[0] <= event.x <= rect[2] and rect[1] <= event.y <= rect[3]):
            idxToDel = i
        else:
            formCanv.create_rectangle(rect[0], rect[1], rect[2], rect[3], width = 2)
    if (idxToDel != -1): 
        del coords[idxToDel] 
        del realCoords[idxToDel]
        drawAllRect(coords)

def autoDetectPress(imgPath, imgWidth, imgHeight):
    global realCoords, resolutionValue, coords
    
    blockSizeValue = blockSize.get()
    cValue = cVal.get()
    minAreaValue = minArea.get()
    resolutionValue = resolution.get()

    realCoords = scan(filePath = imgPath,
         imgHeight = imgHeight,
         imgWidth = imgWidth,
         blockSize = blockSizeValue,
         cVal = cValue,
         minArea = minAreaValue,
         resolution = resolutionValue)
     
     # transform rect 
    coords = [[rect[0] * formWidth +10, rect[1] * formHeight +10, rect[2] * formWidth +10, rect[3] * formHeight +10, rect[4], rect[5]] for rect in realCoords]

    formCanv.create_image(10,10, image = image, anchor = "nw")

    for rect in coords:
       formCanv.create_rectangle(rect[0], rect[1], rect[2], rect[3], width = 2)

def cropPress(imgPath, imgWidth, imgHeight, realCoords, resolution):
    cropToPath(imgPath, imgWidth, imgHeight, realCoords, resolution)

def updateColName(entry, index):
    colName = entry.get()
    coords[index][5] = colName
    realCoords[index][5] = colName

def writeFile(realCoords):
    # open file
    currentTime = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    # output_excel = os.path.join(excel_folder, f"SurveyOnMultidimensionalPovertyIndex_{current_time}.xlsx")

    with open(f"./generateElement/boxPointer-{currentTime}.dat", "wb") as f:
        print(realCoords)
        pickle.dump(realCoords, f)
        print("File written successfully")

formCanv = Canvas(app)
formCanv.pack(anchor="nw")

formCanv.bind("<Button-1>", get_xy)
formCanv.bind("<Button-3>", del_element)

img = Image.open(imgPath)
scaleFactor = formHeight/img.height
formWidth = int(img.width * scaleFactor)
formHeight = int(img.height * scaleFactor)

formCanv.config(width=formWidth, height= formHeight)
image = img.resize((formWidth, formHeight))
image = ImageTk.PhotoImage(image)
formCanv.create_image(10,10, image = image, anchor = "nw")

font=("Helvetica", 10, "bold")
xAuto = formWidth+50
# yAuto = 10
yAuto = -90
scaleLength = winWidth-formWidth-200

# entryEmptyTemplate = Entry(app, width = int((winWidth-xAuto)*0.1))
# entryEmptyTemplate.place(x = xAuto+100, y = yAuto+45)
# Label(app, text="Upload form template", font=font).place(x = xAuto, y = yAuto)
# btnFind = Button(app, text="Select file",command = lambda:getFilePath(entryEmptyTemplate))
# btnFind.place(x = xAuto + 20, y = yAuto+40)

Label(app, text="Parameter tuning for auto-detect", font=font).place(x = xAuto, y = yAuto+100)

Label(app, text="block size").place(x = xAuto+20, y = yAuto+140)
Label(app, text="C-value").place(x = xAuto+20, y = yAuto+180)
Label(app, text="min. area").place(x = xAuto+20, y = yAuto+220)
Label(app, text="resolution").place(x = xAuto+20, y = yAuto+260)
blockSize = Scale(app, from_=3, to=255, length = scaleLength, resolution=2, orient=HORIZONTAL)
blockSize.place(x=xAuto + 80, y= yAuto+120)
cVal = Scale(app, from_=1, to=15, length = scaleLength, resolution=2, orient=HORIZONTAL)
cVal.place(x=xAuto + 80, y= yAuto+160)
minArea = Scale(app, from_=0, to=1000, length = scaleLength, orient=HORIZONTAL)
minArea.place(x=xAuto + 80, y= yAuto+200)
resolution = Scale(app, from_=1, to=8, length = scaleLength, orient=HORIZONTAL)
resolution.place(x=xAuto + 80, y= yAuto+240)

blockSize.set(141)
cVal.set(5)
minArea.set(153)
resolution.set(3)

autoDetect = Button(app, text="Auto detect", command=lambda:autoDetectPress(imgPath=imgPath, imgWidth=formWidth, imgHeight= formHeight))
autoDetect.place(x = xAuto, y = yAuto + 300)

Label(app, text="Column name:", font=font).place(x = xAuto, y = yAuto+360)
# autoDetect = Button(app, text="CROP!!!!!!!", command=lambda:cropPress(imgPath, imgWidth=formWidth, imgHeight= formHeight, realCoords = realCoords, resolution = resolutionValue))
# autoDetect.place(x = xAuto+200, y = yAuto + 180)
entryColumnBox = Entry(app, width = int((winWidth-xAuto)*0.07))
entryColumnBox.place(x= xAuto + 120, y= yAuto + 365)

submitColName = Button(app, text="Submit column name", command=lambda:updateColName(entryColumnBox, index))
submitColName.place(x = xAuto , y = yAuto + 400)

saveColData = Button(app, text = "save pointer file (.dat)", command=lambda:writeFile(realCoords))
saveColData.place(x = xAuto + 100, y = yAuto + 520)

app.mainloop()


entryEmptyTemplate = Entry(app, width = int((winWidth-xAuto)*0.1))
entryEmptyTemplate.place(x = xAuto+100, y = yAuto+45)
Label(app, text="Upload form template", font=font).place(x = xAuto, y = yAuto)
btnFind = Button(app, text="Select file",command = lambda:getFilePath(entryEmptyTemplate))
btnFind.place(x = xAuto + 20, y = yAuto+40)
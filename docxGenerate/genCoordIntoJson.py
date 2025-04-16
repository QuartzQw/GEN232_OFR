import aspose.words as aw
import json
import io

positionData = []
doc = aw.Document("./demo.docx")

# Use LayoutCollector and LayoutEnumerator to calculate coordinates of the shapes.
collector = aw.layout.LayoutCollector(doc)
enumerator = aw.layout.LayoutEnumerator(doc)

# Get the shapes.
shapes = doc.get_child_nodes(aw.NodeType.SHAPE, True)
for s in shapes :
    shape = s.as_shape()
    # skip shapes from header/footer.
    if shape.get_ancestor(aw.NodeType.BODY) == None :
        continue

    # # process only toplevel
    # if not shape.is_top_level :
    #     continue
        
    enumerator.set_current(collector, shape)
    # # Process only the first page.
    # if enumerator.page_index>1 :
    #     break

    rect = enumerator.rectangle
    # print(f"X={rect.left}; Y={rect.top}; Width={rect.width}; heigth={rect.height}")
    positionData.append([rect.left, rect.top, rect.width, rect.height, enumerator.page_index])

    # open template(.json file)
with open('./mockupTemplate.json', 'r', encoding="utf-8") as file:
    jsonContent = json.load(file)

questionIndex = 0
for question in jsonContent["questions"]:
    for choice, att in question["choices"].items():
        att["x"] = positionData[questionIndex][0]
        att["y"] = positionData[questionIndex][1]
        att["width"] = positionData[questionIndex][2]
        att["height"] = positionData[questionIndex][3]
        att["page"] = positionData[questionIndex][4]
        questionIndex += 1

jsonText = str(jsonContent).replace('\'', '"')

with io.open("./modifiedMockupTemplate.json", 'w', encoding="utf-8") as file:
    file.write(jsonText)
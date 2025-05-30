import numpy as np
import cv2
import requests
import json

classes = {}
# https://en.wikipedia.org/wiki/List_of_file_signatures
jpgHeader = bytes([0xff, 0xd8, 0xff])

def extractClassPlace(className):
    r = requests.get(f"https://api.laamea.com/storage/images/046-{className}.jpg", headers={"Referer": "https://laamea.com/046-0-20", "Host": "api.laamea.com"})
    if r.content[0:3] != jpgHeader:
        raise Exception(f"Couldn't find image of classroom {className}")

    r_nparr = np.frombuffer(r.content, np.uint8)
    image = cv2.imdecode(r_nparr, cv2.IMREAD_UNCHANGED)
    image = cv2.resize(image, (0, 0), fx=0.5, fy=0.5)
    h, w = image.shape[:2]
    ch, cw = (int(h/2), int(w/2))
    cv2.circle(image, (cw, ch), 52, (255, 255, 255), -1)

    # https://docs.opencv.org/4.x/d4/d70/tutorial_hough_circle.html
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    gray = cv2.medianBlur(gray, 5)
    circles = cv2.HoughCircles(gray, cv2.HOUGH_GRADIENT, 1, 10, param1 = 40, param2 = 20, minRadius = 0, maxRadius = 30)
    if circles is None:
        return (-1, -1)

    circles = np.uint16(np.around(circles))
    for i in circles[0, :]:
        return (i[0] * 2, i[1] * 2)

classRoomNames = ['0-20', '0-19', '0-18', '0-11', '0-11-1', '0-10', '0-9', '0-2', '0-2-2', '1-1', '1-2', '1-3', '1-4', '1-13', '1-15', '1-16', '1-17', '1-18', '1-19', '1-21', '1-30', '1-32', '1-33', '1-34', '2-6', '2-22']

if __name__ == '__main__':
    classes = {}
    for classroom in classRoomNames:
        clSplit = classroom.split("-", 1)
        if clSplit[0] not in classes.keys():
            classes[clSplit[0]] = {}
        if clSplit[1] not in classes[clSplit[0]]:
            classes[clSplit[0]][clSplit[1]] = {}
            x, y = extractClassPlace(classroom)
            classes[clSplit[0]][clSplit[1]]["X"] = str(x)
            classes[clSplit[0]][clSplit[1]]["Y"] = str(y)
    print(classes)
    with open("locations.json", "w") as outfile: 
        json.dump(classes, outfile)
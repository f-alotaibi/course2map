import numpy as np
import cv2
import random
import parser
import lecture_class
import os
import requests
import base64

# https://en.wikipedia.org/wiki/List_of_file_signatures
jpgHeader = bytes([0xff, 0xd8, 0xff])

def extractClassPlace(className):
    if not os.path.isfile(f".cache/{className}.jpg"):
        r = requests.get(f"https://laamea.com/media/maps/046-{className}.jpg", headers={"Referer": "https://laamea.com/046-0-20", "Host": "laamea.com"})
        if r.content[0:3] != jpgHeader:
            raise Exception(f"Couldn't find image of classroom {className}")
        open(f".cache/{className}.jpg", 'wb').write(r.content)

    image = cv2.imread(f".cache/{className}.jpg")

    # https://docs.opencv.org/4.x/d4/d70/tutorial_hough_circle.html
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    gray = cv2.medianBlur(gray, 5)
    rows = gray.shape[0]
    circles = cv2.HoughCircles(gray, cv2.HOUGH_GRADIENT, 1, rows / 8, param1=100, param2=30, minRadius=1, maxRadius=30)

    if circles is None:
        return (-1, -1)

    circles = np.uint16(np.around(circles))
    for i in circles[0, :]:
        return (i[0], i[1])

def extractClasses(input_text):
    floors = [{} for _ in range(3)]
    courses = parser.parseText(parser.chromeify(input_text))
    for course in courses:
        lecClass = lecture_class.LectureClass(course)
        for day, infoArray in lecClass.courseTimes.items():
            for info in infoArray:
                time = info["Time"]
                place = info["Place"]
                floor = place["Floor"]
                lecRoom = place["Room"]
                if lecRoom not in floors[floor]:
                    try:
                        val = extractClassPlace(f"{floor}-{lecRoom}")
                    except Exception as e:
                        raise e
                    if val == (-1, -1):
                        continue
                    floors[floor][lecRoom] = {
                        "Text": f"Room no. {lecRoom}",
                        "Color": (random.randrange(0, 168), random.randrange(0, 168), random.randrange(0, 168)), # limit the colors to darker sides for a more clear text
                        "Placement": val,
                    }
                floors[floor][lecRoom]["Text"] += f"\n{lecClass.code}-{day}-{time}"

    floorImages = []
    for floorNo in range(len(floors)):
        floor = floors[floorNo]
        if not bool(floor):
            continue
        floorImage = cv2.imread(f"{floorNo}_floor.jpg")
        original = floorImage.copy()
        for info in floor.values():
            position = info["Placement"]
            color = info["Color"]
            text = info["Text"]
            cv2.circle(original, position, 12, color, -1)
            text_newLines_split = text.split("\n")
            text_newLines_split[0], text_newLines_split[-1] = text_newLines_split[-1], text_newLines_split[0]
            for i, line in enumerate(text_newLines_split):
                line = line.replace("ص", "Mor").replace("م", "Eve")
                if position[1] < 200:
                    cv2.putText(original, line, (position[0] - 110, position[1] + 25 + (i * 14)), cv2.FONT_HERSHEY_COMPLEX, 0.45, color, 1, cv2.LINE_AA)
                else:
                    cv2.putText(original, line, (position[0] - 110, position[1] - 25 - (i * 14)), cv2.FONT_HERSHEY_COMPLEX, 0.45, color, 1, cv2.LINE_AA)
        floorImages.append(original)
    floorImages.reverse()
    return base64.b64encode(cv2.imencode('.jpg', cv2.vconcat(floorImages))[1]).decode()
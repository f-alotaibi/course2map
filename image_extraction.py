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

    image = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    lower = np.array([0, 100, 100], dtype="uint8")
    upper = np.array([10, 255, 255], dtype="uint8")

    mask = cv2.inRange(image, lower, upper)

    cnts = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    cnts = cnts[0] if len(cnts) == 2 else cnts[1]

    for c in cnts:
        perimeter = cv2.arcLength(c, True)
        approx = cv2.approxPolyDP(c, 0.04 * perimeter, True)
        if len(approx) != 7 and len(approx) != 8:
            cv2.drawContours(mask, [c], -1, (0, 0, 0), -1)
            continue
        M = cv2.moments(c)
        cX = int(M["m10"] / M["m00"])
        cY = int(M["m01"] / M["m00"])
        return cX, cY
    return -1, -1

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
            for i, line in enumerate(text_newLines_split):
                if i == 0:
                    continue
                line = line.replace("ص", "Mor").replace("م", "Eve")
                if position[1] < 200:
                    cv2.putText(original, line, (position[0] - 110, position[1] + 25 + (i * 14)), cv2.FONT_HERSHEY_COMPLEX, 0.45, color, 1, cv2.LINE_AA)
                else:
                    cv2.putText(original, line, (position[0] - 110, position[1] - 25 - (i * 14)), cv2.FONT_HERSHEY_COMPLEX, 0.45, color, 1, cv2.LINE_AA)
            if position[1] < 200:
                cv2.putText(original, text_newLines_split[0], (position[0] - 35, position[1] + 25 + (len(text_newLines_split) * 14)), cv2.FONT_HERSHEY_COMPLEX, 0.45, color, 1, cv2.LINE_AA)
            else:
                cv2.putText(original, text_newLines_split[0], (position[0] - 35, position[1] - 25 - (len(text_newLines_split) * 14)), cv2.FONT_HERSHEY_COMPLEX, 0.45, color, 1, cv2.LINE_AA)
        floorImages.append(original)
    floorImages.reverse()
    return base64.b64encode(cv2.imencode('.jpg', cv2.vconcat(floorImages))[1]).decode()
import numpy as np
import cv2
import random
import parser
import lecture_class
import requests
import base64
from concurrent.futures import ThreadPoolExecutor

cachedPositions = {}

# https://en.wikipedia.org/wiki/List_of_file_signatures
jpgHeader = bytes([0xff, 0xd8, 0xff])

def extractClassPlace(className):
    r = requests.get(f"https://api.laamea.com/storage/images/046-{className}.jpg", headers={"Referer": "https://laamea.com/046-0-20", "Host": "api.laamea.com"})
    if r.content[0:3] != jpgHeader:
        raise Exception(f"Couldn't find image of classroom {className}")

    r_nparr = np.frombuffer(r.content, np.uint8)
    image = cv2.imdecode(r_nparr, cv2.IMREAD_UNCHANGED)
    image = cv2.resize(image, (0, 0), fx=0.5, fy=0.5)

    # https://docs.opencv.org/4.x/d4/d70/tutorial_hough_circle.html
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    gray = cv2.medianBlur(gray, 5)
    circles = cv2.HoughCircles(gray, cv2.HOUGH_GRADIENT, 1, 20, param1 = 50, param2 = 30, minRadius = 0, maxRadius = 10)

    if circles is None:
        return (-1, -1)

    circles = np.uint16(np.around(circles))
    for i in circles[0, :]:
        cachedPositions[className] = (i[0] * 2, i[1] * 2)
        return (i[0] * 2, i[1] * 2)

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
                    floors[floor][lecRoom] = {
                        "Text": f"Room no. {lecRoom}",
                        "Color": (random.randrange(0, 168), random.randrange(0, 168), random.randrange(0, 168)), # limit the colors to darker sides for a more clear text
                    }
                floors[floor][lecRoom]["Text"] += f"\n{lecClass.code}-{day}-{time}"
    with ThreadPoolExecutor() as executor:
        for floorNo, floor in enumerate(floors):
            for lecRoom in floor.keys():
                if f"{floorNo}-{lecRoom}" in cachedPositions:
                    continue
                def run():
                    try:
                        val = extractClassPlace(f"{floorNo}-{lecRoom}")
                        if val == (-1, -1):
                            raise Exception(f"{floorNo}-{lecRoom} not found")
                    except Exception as e:
                        raise e
                executor.submit(run)
        executor.shutdown(wait=True)

    floorImages = []
    for floorNo in range(len(floors)):
        floor = floors[floorNo]
        if not bool(floor):
            continue
        floorImage = cv2.imread(f"{floorNo}_floor.jpg")
        original = floorImage.copy()
        for lecRoom, info in floor.items():
            position = cachedPositions[f"{floorNo}-{lecRoom}"]
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
class LectureClass:
    def __init__(self, text_list):
        self.code = text_list[0]
        courseTimes = text_list[6::][:-2]
        self.courseTimes = {}
        try:
            int(courseTimes[0][0])
        except:
            return
        i = 0
        while i < len(courseTimes):
            place = "".join(courseTimes[i+2].strip()[5:].split(" ")).split("-")
            if courseTimes[i] not in self.courseTimes:
                self.courseTimes[courseTimes[i]] = []
            self.courseTimes[courseTimes[i]].append({
                "Time": courseTimes[i+1],
                "Place": {
                    "Floor": int(place[0]),
                    "Room": place[1],
                },
            })
            i = i + 3
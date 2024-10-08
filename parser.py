def parseText(text):
  text_list = text.split('\n')
  if text_list[-1] == "":
     text_list = text_list[:-1]
  courses = []
  coursesTemp = []
  for s in text_list:
    if len(s.split(" ")) == 2:
        if len(s.split(" ")[0]) == 3 or len(s.split(" ")[1]) == 3:
            if s.split(" ")[0].isdigit():
                m = s.split(" ")
                m[0], m[1] = m[1], m[0]
                s = " ".join(m)
            if coursesTemp != []:
                courses.append(coursesTemp)
                coursesTemp = []
    coursesTemp.append(s)
  courses.append(coursesTemp)
  return courses

# a util function that just removes firefox whitespaces
def chromeify(text):
    textList = []
    for t in text.split("\n"):
      if t != '\t':
        textList.append(t.replace('\t', ''))
    return "\n".join(textList)
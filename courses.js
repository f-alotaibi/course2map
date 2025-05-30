const textarea = document.getElementById("input")

const canvas = document.getElementById('myCanvas');
const ctx = canvas.getContext('2d');

dayMap = {
    1: "Sunday",
    2: "Monday",
    3: "Tuesday",
    4: "Wednesday",
    5: "Thursday",
}

var currentValue = ""
function pollInput() {
    if (textarea.value == currentValue) {
        return
    }
    currentValue = textarea.value
    let coursesTemp = []
    let courses = {}
    for (let text of textarea.value.split('\n')) {
        if (text == '\t') {
            continue
        }
        let info = text.replaceAll('\t', "")
        let infoSplit = info.split(" ")
        if (infoSplit.length != 2 || (infoSplit[0].length != 3 && infoSplit[1].length != 3)) {
            coursesTemp.push(info)
            continue
        }
        if (coursesTemp.length > 0) {
            let courseCode = coursesTemp[0].split(" ").reverse().join(" ")
            let courseTimes = coursesTemp.slice(6, -2)
            if (courseTimes.length > 2) {
                for (let i = 0; i < courseTimes.length; i += 3) {
                    let day = parseInt(courseTimes[i])
                    if (day == NaN || courseTimes[i+2] == " ") {
                        continue
                    }
                    let placeLocation = courseTimes[i+2].replaceAll(' ', "").substring(4).split("-")
                    let floor = placeLocation[0]
                    let room = placeLocation[1]
                    if (!courses[floor]) courses[floor] = {}
                    if (!courses[floor][room]) courses[floor][room] = {
                        "X": data[floor][room]["X"],
                        "Y": data[floor][room]["Y"],
                        "Text": `ROOM 46-${floor}-${room}`,
                        "Color": [Math.floor(Math.random() * 168), Math.floor(Math.random() * 168), Math.floor(Math.random() * 168)]
                    }
                    courses[floor][room]["Text"] += `\n${courseCode}    ${dayMap[day]}  ${courseTimes[i+1].replaceAll("ص", "AM").replaceAll("م", "PM")}`
                }
            }
            coursesTemp = []
        }
        coursesTemp.push(info)
    }
    console.log(courses)
    runCanvas(courses)
}

function runCanvas(courses) {
    let imagesLoaded = 0;
    function loadImage() {
        imagesLoaded++;
        if (imagesLoaded == Object.keys(courses).length) {
            drawImage()
        }
    }
    function drawImage() {
        canvas.width = 0;
        canvas.height = images.reduce((totalHeight, image) => totalHeight + image.height, 0);;
        let currentY = 0
        for (let image of images) {
            if (canvas.width == 0) {
                canvas.width = image.width;
            }
            ctx.drawImage(image, 0, currentY, canvas.width, image.height);
            floor = image.FLOOR
            for (let room of Object.keys(courses[floor])) {
                let X = parseInt(courses[floor][room]["X"])
                let Y = parseInt(courses[floor][room]["Y"])
                let Color = courses[floor][room]["Color"]
                ctx.beginPath();
                ctx.fillStyle = `rgb(${Color[0]}, ${Color[1]}, ${Color[2]})`;
                ctx.arc(X, currentY + Y, 12, 0, Math.PI * 2)
                ctx.fill();
                ctx.closePath();
                for (const [i, line] of Object.entries(courses[floor][room]["Text"].split("\n"))) {
                    ctx.font = "16px sans-serif"
                    if (Y < 200) {
                        ctx.fillText(line, X - 80 ,currentY + Y + 30 + (16 * i));
                    } else {
                        ctx.fillText(line, X - 80 ,currentY + Y - 20 - (16 * i));
                    }
                }
            }
            currentY += image.height
        }
    }
    var images = []
    for (let course of Object.keys(courses).reverse()){
        let image = new Image()
        images.push(image)
        image.src = `${course}_floor.jpg`;
        image.FLOOR = course
        image.onload = loadImage;
    }
}
self.setInterval(pollInput, 50)
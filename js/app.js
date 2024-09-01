// Cash
const textarea = document.getElementById("input")
const outputarea = document.getElementById("output")

let input = ""

function pollInput() {
    if (textarea.value == input || textarea.value == "") {
        return
    }
    console.log("Sending", textarea.value)
    input = textarea.value
    outputarea.innerHTML = ``
    fetch("extract-classes", {
        method: "POST",
        body: new URLSearchParams({
            Input: input,
        })
    }).then((response) => {
        return response.text()
    }).then((base64Img) => {
        let dom_img = document.createElement("img")
        dom_img.src = `data:image/png;base64, ${base64Img}`
        dom_img.style = `width: 100%`
        outputarea.appendChild(dom_img)
    }).catch((err) => {
        outputarea.innerHTML = `Error: ${err}`
    })
}

self.setInterval(pollInput, 500)
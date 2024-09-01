// Cash
const textarea = document.getElementById("input")
const outputarea = document.getElementById("output")

let input = ""

function pollInput() {
    if (textarea.value == input || textarea.value == "") {
        return
    }
    input = textarea.value
    outputarea.innerHTML = ``
    fetch("extract-classes", {
        method: "POST",
        body: new URLSearchParams({
            Input: input,
        })
    }).then(async (response) => {
        return [response.ok, await response.text()]
    }).then(([ok, txt]) => {
        if (!ok) {
            throw new Error(txt)
        }
        let dom_img = document.createElement("img")
        dom_img.src = `data:image/png;base64, ${txt}`
        dom_img.style = `width: 100%`
        outputarea.appendChild(dom_img)
    }).catch((err) => {
        outputarea.innerHTML = `${err}`
    })
}

self.setInterval(pollInput, 500)
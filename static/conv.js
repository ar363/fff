
const lt = pdfjsLib.getDocument({
    url: document.getElementById('book-url').value
})

let cwh = 0
let pts = []
let mode = 'W'

let hist = {
    past: [],
    future: []
}

function addLine(cw, pt) {
    let c = document.createElement('div')
    c.classList.add('gcur')
    c.style.top = pt + 'px'
    cw.appendChild(c)
}

function removeLine(cw, pt) {
    Array.from(document.querySelectorAll('.gcur')).filter(e => e.style.top === pt + 'px').forEach(e => e.parentElement.removeChild(e))
}

lt.promise.then((pdf) => {
    pdf.getPage(pageNo).then(page => {
        var scale = 1.5;
        var viewport = page.getViewport({ scale: scale, });
        // Support HiDPI-screens.
        var outputScale = window.devicePixelRatio || 1;

        var canvas = document.getElementById('the-canvas');
        var cw = document.getElementById('cwrap')
        var context = canvas.getContext('2d');

        canvas.width = Math.floor(viewport.width * outputScale);
        canvas.height = Math.floor(viewport.height * outputScale);
        canvas.style.width = Math.floor(viewport.width) + "px";
        cw.style.width = Math.floor(viewport.width) + "px";
        canvas.style.height = Math.floor(viewport.height) + "px";
        cw.style.height = Math.floor(viewport.height) + "px";
        cwh = viewport.height

        var transform = outputScale !== 1
            ? [outputScale, 0, 0, outputScale, 0, 0]
            : null;

        var renderContext = {
            canvasContext: context,
            transform: transform,
            viewport: viewport
        };
        page.render(renderContext).promise.then(() => {
            fetch(`/get-pts/${bookId}/${pageNo}`).then(res => res.json()).then(ptsRes => {
                ptsRes.pts.forEach(pt => {
                    let pty = parseFloat((pt * cwh / 100).toFixed(4))

                    let c = document.createElement('div')
                    c.classList.add('gcur-pre')
                    c.style.top = pty + 'px'
                    pts.push(pt)
                    cw.appendChild(c)
                })



                cw.addEventListener('click', (e) => {
                    if (mode === 'W') {
                        let c = document.createElement('div')
                        c.classList.add('gcur')
                        c.style.top = e.offsetY + 'px'
                        cw.appendChild(c)

                        pts.push(parseFloat((e.offsetY / cwh * 100).toFixed(3)))
                        hist.past.push({
                            action: 'ADD_LINE',
                            vals: [e.offsetY]
                        })
                        hist.future = []
                    }

                    if (mode === 'X') {
                        if (e.target.classList.contains('gcur') || e.target.classList.contains('gcur-pre') || e.target.classList.contains('gcur-sugg')) {
                            console.log(e.target)
                            pts = pts.filter(xe => Math.round(xe) !== Math.round(parseFloat((parseFloat(e.target.style.top.replace('px', '')) / cwh * 100).toFixed(3))))
                            e.target.parentElement.removeChild(e.target)
                        }
                    }
                })

                document.addEventListener('keydown', function (event) {
                    if (event.key === 'w') activateWriteMode()
                    if (event.key === 'x') activateDeleteMode()

                    if (event.ctrlKey && event.key === 'z') {

                        let l_ac = hist.past.pop()

                        if (l_ac !== undefined) {


                            if (l_ac.action === 'ADD_LINE') {
                                removeLine(cw, l_ac.vals[0])
                                pts = pts.filter(e => Math.round(e) !== Math.round(parseFloat((l_ac.vals[0] / cwh * 100).toFixed(3))))
                            }

                            hist.future.push(l_ac)
                        }


                    }
                    if (event.ctrlKey && event.key === 'y') {
                        let f_ac = hist.future.pop()

                        if (f_ac !== undefined) {

                            if (f_ac.action === 'ADD_LINE') {
                                addLine(cw, f_ac.vals[0])
                                pts.push(parseFloat((f_ac.vals[0] / cwh * 100).toFixed(3)))
                            }

                            hist.past.push(f_ac)
                        }
                    }
                    if (event.ctrlKey && event.key === 's') {
                        event.preventDefault()
                        saveNextPage()
                    }
                });

                document.addEventListener('keyup', (e) => {
                    if (e.key === 'x') activateWriteMode()
                })

            })
        });

    })
})



document.getElementById('save').addEventListener('click', saveNextPage)

function saveNextPage() {

    fetch('/clrsave-pts', {
        method: 'post',
        body: JSON.stringify({
            id: parseInt(bookId),
            page: pageNo,
            pts: pts
        }),
        headers: {
            'content-type': 'application/json'
        }
    }).then(r => r.json()).then(d => {
        if (d.ok) {
            window.location.href = `/book_cap/${bookId}/${pageNo + 1}/`
        }
    })

}

function activateDeleteMode() {
    mode = 'X'

    document.querySelectorAll('.gcur').forEach(e => {
        e.style.height = '12px'
        e.style.opacity = '0.5'
    })
    document.querySelectorAll('.gcur-pre').forEach(e => {
        e.style.height = '12px'
        e.style.opacity = '0.5'
    })
    document.querySelectorAll('.gcur-sugg').forEach(e => {
        e.style.height = '12px'
        e.style.opacity = '0.5'
    })
}


function activateWriteMode() {
    mode = 'W'

    document.querySelectorAll('.gcur').forEach(e => {
        e.style.height = '2px'
        e.style.opacity = '1'
    })
    document.querySelectorAll('.gcur-pre').forEach(e => {
        e.style.height = '2px'
        e.style.opacity = '1'
    })
    document.querySelectorAll('.gcur-sugg').forEach(e => {
        e.style.height = '2px'
        e.style.opacity = '1'
    })
}

function addSuggestedLines() {
    let sgel = document.getElementById('sugg')
    sgel.parentElement.removeChild(sgel)

    fetch(`/sugg_pts/${bookId}/${pageNo}/`)
        .then(res => res.json())
        .then(data => {
            let cw = document.getElementById('cwrap')
            data.pts.forEach(pt => {
                let pty = parseFloat((pt * cwh / 100).toFixed(4))

                let c = document.createElement('div')
                c.classList.add('gcur-sugg')
                c.style.top = pty + 'px'
                pts.push(pt)
                cw.appendChild(c)
            })
        })

}

document.addEventListener("DOMContentLoaded", function () {
    const dropArea = document.getElementById("drop-area");
    const inputFile = document.getElementById("input-file");
    const dragIcon = document.getElementById("drag-drop-image");
    const fileView = document.getElementById("file-view");
    const uploadIcon = document.getElementById("upload-icon");
    
    uploadIcon.addEventListener("click", function (e) {
        inputFile.click();
    });
    // Dragover
    dropArea.addEventListener("dragover", function (e) {
        e.preventDefault();
        dropArea.classList.add("dragover");
        dragIcon.classList.remove("d-none");
    });
    document.getElementById("submit-btn").addEventListener("click", function (e) {
        console.log(inputFile.files);
    })

    // Dragleave
    dropArea.addEventListener("dragleave", function (e) {
        e.preventDefault();
        dropArea.classList.remove("dragover");
        dragIcon.classList.add("d-none");
    });


    // Drop
    dropArea.addEventListener("drop", function (e) {
        e.preventDefault();
        dropArea.classList.remove("dragover");
        dragIcon.classList.add("d-none");

        const files = e.dataTransfer.files;
        
        if (files.length > 0) {
            inputFile.files = files;

            for (const element of files) {
                const fileDivElement = document.createElement('button');
                fileDivElement.className = 'btn btn-primary';
                fileDivElement.innerText = element.name;

                fileDivElement.onclick = function(ev) {
                    fileDivElement.remove(); // sauberer
                };

                const deleteSpan = document.createElement('span');
                deleteSpan.className = 'badge badge-light';
                deleteSpan.innerText = 'x';

                fileDivElement.appendChild(deleteSpan);
                fileView.appendChild(fileDivElement);
            }

            // Optional: Wenn nur eine Datei, zeige den Inhalt in der Textarea
            if (files[0].type === "text/plain" || files[0].name.endsWith(".py") || files[0].name.endsWith(".js")) {
                const reader = new FileReader();
                reader.onload = function (event) {
                    dropArea.querySelector("textarea").value = event.target.result;
                };
                reader.readAsText(files[0]);
            }
        }
    });
 


    // File Input change Event
    inputFile.addEventListener("change", (e) => {
        const files = e.target.files;
        
        if (files.length == 1) {
            const reader = new FileReader();
            reader.onload = function (event) {
                dropArea.querySelector("textarea").value = event.target.result;
            };
            reader.readAsText(files[0]);
            return;
        }
        
        for (let index = 0; index < files.length; index++) {
            const file = files[index];
            const fileDivElement = document.createElement('button');
            fileDivElement.className = 'btn btn-primary';
            fileDivElement.innerText = file.name;

            fileDivElement.onclick = function(ev) {
                fileDivElement.remove();
            };

            const deleteSpan = document.createElement('span');
            deleteSpan.className = 'badge badge-light';
            deleteSpan.innerText = 'x';

            fileDivElement.appendChild(deleteSpan);
            fileView.appendChild(fileDivElement);
        }
    });
});
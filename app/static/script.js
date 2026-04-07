document.addEventListener("DOMContentLoaded", function () {
    const dropArea = document.getElementById("drop-area");
    const inputFile = document.getElementById("input-file");
    const dragIcon = document.getElementById("drag-drop-image");

    // Dragover
    dropArea.addEventListener("dragover", function (e) {
        e.preventDefault();
        dropArea.classList.add("dragover");
        dragIcon.classList.remove("d-none");
    });

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

    // Klick auf Textarea/DropArea öffnet File Dialog
    dropArea.addEventListener("click", () => inputFile.click());

    // File Input change Event
    inputFile.addEventListener("change", (e) => {
        const file = e.target.files[0];
        if (file) {
            const reader = new FileReader();
            reader.onload = function (event) {
                dropArea.querySelector("textarea").value = event.target.result;
            };
            reader.readAsText(file);
        }
    });
});
document.addEventListener("DOMContentLoaded", function () {
    const dropArea = document.getElementById("drop-area");
    const inputFile = document.getElementById("input-file");
    const dragIcon = document.getElementById("drag-drop-image");
    const fileView = document.getElementById("file-view");
    const uploadIcon = document.getElementById("upload-icon");
    const loadingSpinner = document.getElementById("loading-spinner");

    if (dropArea && inputFile && dragIcon && fileView && uploadIcon) {
        uploadIcon.addEventListener("click", function () {
            inputFile.click();
        });

        dropArea.addEventListener("dragover", function (e) {
            e.preventDefault();
            dropArea.classList.add("dragover");
            dragIcon.classList.remove("d-none");
        });

        const submitBtn = document.getElementById("submit-btn");
        if (submitBtn && loadingSpinner) {
            submitBtn.addEventListener("click", function () {
                loadingSpinner.style.display = "block";
                console.log(inputFile.files);
            });
        }

        dropArea.addEventListener("dragleave", function (e) {
            e.preventDefault();
            dropArea.classList.remove("dragover");
            dragIcon.classList.add("d-none");
        });

        dropArea.addEventListener("drop", function (e) {
            e.preventDefault();
            dropArea.classList.remove("dragover");
            dragIcon.classList.add("d-none");

            const files = e.dataTransfer.files;

            if (files.length > 0) {
                inputFile.files = files;

                for (const element of files) {
                    const fileDivElement = document.createElement("button");
                    fileDivElement.className = "btn btn-primary";
                    fileDivElement.innerText = element.name;

                    fileDivElement.onclick = function () {
                        fileDivElement.remove();
                    };

                    const deleteSpan = document.createElement("span");
                    deleteSpan.className = "badge badge-light";
                    deleteSpan.innerText = "x";

                    fileDivElement.appendChild(deleteSpan);
                    fileView.appendChild(fileDivElement);
                }

                if (files[0].type === "text/plain" || files[0].name.endsWith(".py") || files[0].name.endsWith(".js")) {
                    const reader = new FileReader();
                    reader.onload = function (event) {
                        dropArea.querySelector("textarea").value = event.target.result;
                    };
                    reader.readAsText(files[0]);
                }
            }
        });

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
                const fileDivElement = document.createElement("button");
                fileDivElement.className = "btn btn-primary";
                fileDivElement.innerText = file.name;

                fileDivElement.onclick = function () {
                    fileDivElement.remove();
                };

                const deleteSpan = document.createElement("span");
                deleteSpan.className = "badge badge-light";
                deleteSpan.innerText = "x";

                fileDivElement.appendChild(deleteSpan);
                fileView.appendChild(fileDivElement);
            }
        });
    }

    const themeButtons = document.querySelectorAll("[data-theme-choice]");
    const themePreview = document.getElementById("theme-preview");

    if (themeButtons.length > 0) {
        const storedTheme = localStorage.getItem("codeReviewerTheme") || "dark";
        const root = document.documentElement;

        const applyTheme = function (theme) {
            const resolvedTheme = theme === "auto"
                ? (window.matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light")
                : theme;

            root.setAttribute("data-bs-theme", resolvedTheme);

            themeButtons.forEach((button) => {
                button.classList.toggle("active", button.dataset.themeChoice === theme);
            });

            if (themePreview) {
                themePreview.textContent = theme === "auto" ? "Systemsteuerung" : theme.charAt(0).toUpperCase() + theme.slice(1);
            }
        };

        applyTheme(storedTheme);

        themeButtons.forEach((button) => {
            button.addEventListener("click", function () {
                const theme = button.dataset.themeChoice;
                localStorage.setItem("codeReviewerTheme", theme);
                applyTheme(theme);
            });
        });
    }

    const promptReviewCheck = document.getElementById("prompt-review-check");

    if (promptReviewCheck) {
        const storedPromptReview = localStorage.getItem("codeReviewerPromptReview");

        if (storedPromptReview !== null) {
            promptReviewCheck.checked = storedPromptReview === "true";
        }

        promptReviewCheck.addEventListener("change", function () {
            localStorage.setItem("codeReviewerPromptReview", String(promptReviewCheck.checked));
        });
    }
});
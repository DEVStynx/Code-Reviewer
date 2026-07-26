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

    const settingValuesElement = document.getElementById("setting-values");
    let serverSettings = {};

    if (settingValuesElement?.textContent) {
        try {
            serverSettings = JSON.parse(settingValuesElement.textContent);
        } catch (error) {
            console.error("Failed to parse server settings:", error);
        }
    }

    const updateSettingInDatabase = async function (key, value) {
        const response = await fetch(`/settings/${encodeURIComponent(key)}`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({ value: String(value) })
        });

        if (!response.ok) {
            throw new Error(`Failed to save setting "${key}" (${response.status})`);
        }
    };

    const themeButtons = document.querySelectorAll("[data-theme-choice]");
    const themePreview = document.getElementById("theme-preview");

    if (themeButtons.length > 0) {
        const root = document.documentElement;
        let activeTheme = serverSettings.theme || localStorage.getItem("codeReviewerTheme") || "dark";

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

        applyTheme(activeTheme);

        themeButtons.forEach((button) => {
            button.addEventListener("click", async function () {
                const nextTheme = button.dataset.themeChoice;
                if (!nextTheme || nextTheme === activeTheme) {
                    return;
                }

                const previousTheme = activeTheme;
                activeTheme = nextTheme;
                localStorage.setItem("codeReviewerTheme", nextTheme);
                applyTheme(nextTheme);

                try {
                    await updateSettingInDatabase("theme", nextTheme);
                } catch (error) {
                    activeTheme = previousTheme;
                    localStorage.setItem("codeReviewerTheme", previousTheme);
                    applyTheme(previousTheme);
                    console.error(error);
                    window.alert("Theme konnte nicht gespeichert werden.");
                }
            });
        });
    }

    const promptReviewCheck = document.getElementById("prompt-review-check");

    if (promptReviewCheck) {
        const storedPromptReview = localStorage.getItem("codeReviewerPromptReview");
        const serverPromptReview = serverSettings["prompt-check"];

        if (serverPromptReview !== undefined) {
            promptReviewCheck.checked = String(serverPromptReview).toLowerCase() === "true";
        } else if (storedPromptReview !== null) {
            promptReviewCheck.checked = storedPromptReview === "true";
        }

        promptReviewCheck.addEventListener("change", async function () {
            const nextValue = promptReviewCheck.checked;
            const previousValue = !nextValue;
            localStorage.setItem("codeReviewerPromptReview", String(nextValue));

            try {
                await updateSettingInDatabase("prompt-check", nextValue);
            } catch (error) {
                promptReviewCheck.checked = previousValue;
                localStorage.setItem("codeReviewerPromptReview", String(previousValue));
                console.error(error);
                window.alert("Prompt-Check konnte nicht gespeichert werden.");
            }
        });
    }
});
const pages = {
    home: document.getElementById("homePage"),
    presentation: document.getElementById("presentationPage"),
    tutorial: document.getElementById("tutorialPage")
};

const tutorialData = [
    {
        title: "Choose File",
        text: "Make sure that the selected file is a .pptx file and that file is valid.",
        image: "../assets/tutorial/step1.png"
    },
    {
        title: "Start Presentation",
        text: "Makesure the file you select is correct and appropriate.",
        image: "../assets/tutorial/step2.png"
    },
    {
        title: "Control with Hand Gestures",
        text: "• Make an open palm gesture and hold it until the slide changes. \n\n • Make a fist to return to the previous slide.",
        image: "../assets/tutorial/step3.png"
    }
];

let currentTutorialStep = 0;
let selectedPresentationPath = "";
let pywebviewReadyPromise = null;

function initializePyWebView() {
    if (window.pywebview && window.pywebview.api) {
        return Promise.resolve(window.pywebview.api);
    }

    if (!pywebviewReadyPromise) {
        pywebviewReadyPromise = new Promise((resolve) => {
            window.addEventListener(
                "pywebviewready",
                () => resolve(window.pywebview.api),
                { once: true }
            );
        });
    }

    return pywebviewReadyPromise;
}

async function getAPI() {
    return await initializePyWebView();
}

function showPage(pageName) {
    Object.values(pages).forEach((page) => {
        page.classList.remove("active-page");
    });

    pages[pageName].classList.add("active-page");
}

function updateTutorial() {
    const step = tutorialData[currentTutorialStep];

    document.getElementById("tutorialStepNumber").textContent =
        `Step ${currentTutorialStep + 1}`;

    document.getElementById("tutorialIndicator").textContent =
        `${currentTutorialStep + 1} / ${tutorialData.length}`;

    document.getElementById("tutorialTitle").textContent = step.title;
    document.getElementById("tutorialText").textContent = step.text;
    document.getElementById("tutorialImage").src = step.image;

    const previousButton =
        document.getElementById("tutorialPreviousButton");

    const nextButton =
        document.getElementById("tutorialNextBottomButton");

    previousButton.disabled = currentTutorialStep === 0;
    nextButton.disabled =
        currentTutorialStep === tutorialData.length - 1;
}

function openTutorial() {
    currentTutorialStep = 0;
    updateTutorial();
    showPage("tutorial");
}

function nextTutorialStep() {
    if (currentTutorialStep >= tutorialData.length - 1) return;
    currentTutorialStep++;
    updateTutorial();
}

function previousTutorialStep() {
    if (currentTutorialStep <= 0) return;
    currentTutorialStep--;
    updateTutorial();
}

async function choosePowerPointFile() {
    const button = document.getElementById("chooseFileButton");
    const text = document.getElementById("chooseFileText");

    try {
        button.disabled = true;
        text.textContent = "Opening file picker...";

        const api = await getAPI();
        const result = await api.choose_file();

        if (result && result.success) {
            selectedPresentationPath = result.path;
            text.textContent = result.filename;
            return;
        }

        text.textContent = "Choose File";
    } catch (error) {
        console.error("File selection error:", error);
        text.textContent = "Choose File";

        alert(
            "Failed to open the file picker.\n\n" +
            "Check the terminal for the Python error."
        );
    } finally {
        button.disabled = false;
    }
}

async function startPresentation() {
    if (!selectedPresentationPath) {
        alert("Please choose a PowerPoint file first.");
        return;
    }

    try {
        const api = await getAPI();

        const success = await api.open_presentation(
            selectedPresentationPath
        );

        if (!success) {
            alert("Failed to open the PowerPoint presentation.");
            return;
        }

        showPage("presentation");
        updateCameraStatus("Starting camera...");

        const cameraStarted = await api.start_camera();

        if (!cameraStarted) {
            updateCameraStatus("Camera failed to start");
        }
    } catch (error) {
        console.error("Presentation launch error:", error);
        alert("Failed to open the PowerPoint presentation.");
    }
}

function updateCameraFrame(imageData) {
    const cameraFeed = document.getElementById("cameraFeed");
    const placeholder = document.getElementById("cameraPlaceholder");

    if (!cameraFeed) return;

    cameraFeed.src = imageData;
    cameraFeed.classList.add("active");

    if (placeholder) {
        placeholder.classList.add("hidden");
    }
}

function updateCameraStatus(status) {
    const statusElement = document.getElementById("cameraStatus");
    const placeholderText =
        document.querySelector("#cameraPlaceholder strong");

    if (statusElement) statusElement.textContent = status;
    if (placeholderText) placeholderText.textContent = status;
}

async function handleGesture(action) {
    try {
        const api = await getAPI();

        if (action === "next") {
            await api.next_slide();
        } else if (action === "previous") {
            await api.previous_slide();
        }
    } catch (error) {
        console.error("Gesture action error:", error);
    }
}

async function returnToHome() {
    try {
        const api = await getAPI();

        await api.stop_camera();
        await api.close_presentation();

        selectedPresentationPath = "";

        document.getElementById("chooseFileText").textContent =
            "Choose File";

        const cameraFeed = document.getElementById("cameraFeed");
        const placeholder = document.getElementById("cameraPlaceholder");

        if (cameraFeed) {
            cameraFeed.src = "";
            cameraFeed.classList.remove("active");
        }

        if (placeholder) {
            placeholder.classList.remove("hidden");
        }

        updateCameraStatus("Camera stopped");
        showPage("home");
    } catch (error) {
        console.error("Error returning to home:", error);
    }
}

async function exitApplication() {
    try {
        const api = await getAPI();

        document.getElementById("exitButton").disabled = true;
        await api.exit_app();
    } catch (error) {
        console.error("Exit error:", error);
    }
}

document.getElementById("chooseFileButton")
    .addEventListener("click", choosePowerPointFile);

document.getElementById("startPresentationButton")
    .addEventListener("click", startPresentation);

document.getElementById("presentationBackButton")
    .addEventListener("click", returnToHome);

document.getElementById("tutorialButton")
    .addEventListener("click", openTutorial);

document.getElementById("tutorialBackButton")
    .addEventListener("click", () => showPage("home"));

document.getElementById("tutorialPreviousButton")
    .addEventListener("click", previousTutorialStep);

document.getElementById("tutorialNextBottomButton")
    .addEventListener("click", nextTutorialStep);

document.getElementById("exitButton")
    .addEventListener("click", exitApplication);

window.addEventListener("pywebviewready", () => {
    console.log("pywebview API ready.");
});

updateTutorial();

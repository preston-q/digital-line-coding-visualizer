const API_ENDPOINT = "/api/linecode";

const bitTab = document.getElementById("bit-tab");
const audioTab = document.getElementById("audio-tab");

const bitPanel = document.getElementById("bit-panel");
const audioPanel = document.getElementById("audio-panel");

const bitInput = document.getElementById("bit-input");

const audioInput = document.getElementById("audio-input");
const audioBrowse = document.getElementById("audio-browse");
const dropZone = document.getElementById("drop-zone");
const selectedFile = document.getElementById("selected-file");

const schemeSelect = document.getElementById("scheme-select");
const generateButton = document.getElementById("generate-button");
const generateLabel = document.getElementById("generate-label");

const statusMessage = document.getElementById("status-message");
const statusDot = document.getElementById("status-dot");

const emptyState = document.getElementById("empty-state");
const waveOutput = document.getElementById("wave-output");
const signalMeta = document.getElementById("signal-meta");

let currentMode = "bits";
let chosenFile = null;


/* -----------------------------
   Input mode
----------------------------- */

function setMode(mode) {
    currentMode = mode;

    const isBits = mode === "bits";

    bitPanel.classList.toggle("hidden", !isBits);
    audioPanel.classList.toggle("hidden", isBits);

    bitTab.classList.toggle("is-active", isBits);
    audioTab.classList.toggle("is-active", !isBits);

    bitTab.setAttribute("aria-selected", String(isBits));
    audioTab.setAttribute("aria-selected", String(!isBits));
}


/* -----------------------------
   Status
----------------------------- */

function setStatus(message, type = "idle") {
    statusMessage.textContent = message;

    statusDot.className = "status-dot";

    if (type !== "idle") {
        statusDot.classList.add(type);
    }
}


function setLoading(isLoading) {
    generateButton.disabled = isLoading;

    generateLabel.textContent = isLoading
        ? "Processing signal…"
        : "Generate Waveform";

    generateButton
        .querySelector("svg")
        ?.classList.toggle("animate-pulse", isLoading);
}


/* -----------------------------
   Audio file
----------------------------- */

function setFile(file) {
    if (!file) return;

    chosenFile = file;

    selectedFile.textContent = file.name;
    selectedFile.classList.remove("hidden");

    setStatus(
        "Audio file selected. Ready to process.",
        "success"
    );
}


/* -----------------------------
   Bit validation
----------------------------- */

function validateBits(value) {
    return value.length > 0 && /^[01]+$/.test(value);
}


/* -----------------------------
   Generate waveform
----------------------------- */

async function generateWaveform() {
    const scheme = schemeSelect.value;


    if (currentMode === "bits") {
        const bits = bitInput.value.trim();

        if (!validateBits(bits)) {
            setStatus(
                "Enter a binary string containing only 0 and 1.",
                "error"
            );

            bitInput.focus();
            return;
        }

    } else if (!chosenFile) {
        setStatus(
            "Choose an audio file before generating a waveform.",
            "error"
        );

        audioBrowse.focus();
        return;
    }


    setLoading(true);

    setStatus(
        "Sending request to the line-coding backend…",
        "processing"
    );


    try {
        let response;


        if (currentMode === "bits") {

            response = await fetch(API_ENDPOINT, {
                method: "POST",

                headers: {
                    "Content-Type": "application/json"
                },

                body: JSON.stringify({
                    mode: "bits",
                    bits: bitInput.value.trim(),
                    scheme
                })
            });

        } else {

            const formData = new FormData();

            formData.append("mode", "audio");
            formData.append("scheme", scheme);
            formData.append("audio", chosenFile);

            response = await fetch(
                API_ENDPOINT,
                {
                    method: "POST",
                    body: formData
                }
            );
        }


        if (!response.ok) {
            let message =
                `Backend returned HTTP ${response.status}.`;

            try {
                const errorData =
                    await response.json();

                message =
                    errorData.detail ||
                    errorData.error ||
                    message;

            } catch (_) {}

            throw new Error(message);
        }


        const payload =
            await response.json();

        waveOutput.innerHTML = payload.svg;
        emptyState.classList.add("hidden");
        waveOutput.classList.remove("hidden");

        setStatus(
            "Waveform generated successfully.",
            "success"
        );

    } catch (error) {

        setStatus(
            error.message ||
            "Unable to reach the line-coding backend.",
            "error"
        );

    } finally {

        setLoading(false);
    }
}


/* -----------------------------
   Event listeners
----------------------------- */

bitTab.addEventListener(
    "click",
    () => setMode("bits")
);

audioTab.addEventListener(
    "click",
    () => setMode("audio")
);

audioBrowse.addEventListener(
    "click",
    () => audioInput.click()
);

audioInput.addEventListener(
    "change",
    () => setFile(audioInput.files[0])
);


["dragenter", "dragover"].forEach(
    (eventName) => {
        dropZone.addEventListener(
            eventName,
            (event) => {
                event.preventDefault();
                dropZone.classList.add("is-dragging");
            }
        );
    }
);


["dragleave", "drop"].forEach(
    (eventName) => {
        dropZone.addEventListener(
            eventName,
            (event) => {
                event.preventDefault();
                dropZone.classList.remove("is-dragging");
            }
        );
    }
);


dropZone.addEventListener(
    "drop",
    (event) => {
        const file =
            event.dataTransfer.files[0];

        if (
            file &&
            file.type.startsWith("audio/")
        ) {
            setFile(file);
        } else {
            setStatus(
                "Please drop a supported audio file.",
                "error"
            );
        }
    }
);


generateButton.addEventListener(
    "click",
    generateWaveform
);


/* -----------------------------
   Initialization
----------------------------- */

document.addEventListener(
    "DOMContentLoaded",
    () => {
        lucide.createIcons();
    }
);
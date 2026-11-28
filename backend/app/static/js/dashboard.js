var voiceEnabled = true;

// ======================================
// MOTEUR SONORE & VOCAL HORS-LIGNE (WEB AUDIO API)
// ======================================
let audioCtx = null;

function playTone(freq, duration, delay = 0, type = "sine") {
    if (!voiceEnabled) return;
    if (!audioCtx) {
        const AudioContext = window.AudioContext || window.webkitAudioContext;
        if (AudioContext) audioCtx = new AudioContext();
    }
    if (!audioCtx) return;
    if (audioCtx.state === "suspended") audioCtx.resume();

    const osc = audioCtx.createOscillator();
    const gain = audioCtx.createGain();
    osc.type = type;
    osc.frequency.setValueAtTime(freq, audioCtx.currentTime + delay);
    gain.gain.setValueAtTime(0.25, audioCtx.currentTime + delay);
    gain.gain.exponentialRampToValueAtTime(0.001, audioCtx.currentTime + delay + duration);

    osc.connect(gain);
    gain.connect(audioCtx.destination);
    osc.start(audioCtx.currentTime + delay);
    osc.stop(audioCtx.currentTime + delay + duration);
}

function playSignAlert(signClass) {
    if (signClass === "STOP") {
        playTone(440, 0.18, 0.0, "square");
        playTone(330, 0.25, 0.22, "square");
    } else if (signClass === "LEFT") {
        playTone(660, 0.12, 0.0, "triangle");
        playTone(520, 0.18, 0.15, "triangle");
    } else if (signClass === "RIGHT") {
        playTone(520, 0.12, 0.0, "triangle");
        playTone(660, 0.18, 0.15, "triangle");
    } else if (signClass === "SLOW") {
        playTone(480, 0.20, 0.0, "sine");
        playTone(480, 0.20, 0.25, "sine");
    } else if (signClass === "ARRIVAL") {
        playTone(523, 0.12, 0.0, "sine");
        playTone(659, 0.12, 0.14, "sine");
        playTone(784, 0.25, 0.28, "sine");
    }
}

﻿
// ======================================
// ORION-ROVER - DASHBOARD JAVASCRIPT
// GROUPE 2 - ORION UNIVERSITY
// ======================================


// ======================================
// 0. ADRESSES DE L'API
// ======================================

const API = {
    navigation: "/api/navigation/decision",
    navigationHistory: "/api/navigation/history",
    sensors: "/api/sensors",
    delivery: "/api/command",
    emergencyStop: "/api/emergency-stop",
    emergencyReset: "/api/emergency-reset",
    aiPredict: "/api/ai/predict"
};

const CAMERA_API = {
    start: "/api/video/start",
    frame: "/api/video/frame",
    stop: "/api/video/stop"
};


// ======================================
// 1. VARIABLES DE LA CAMERA
// ======================================

let cameraRunning = false;
let cameraTimer = null;
let cameraBusy = false;

let aiBusy = false;
let lastAIAnalysis = 0;

const CAMERA_INTERVAL = 1000;
const AI_INTERVAL = 1000;


// ======================================
// 2. ELEMENTS HTML
// ======================================

const cameraFeed = document.getElementById("camera-feed");
const cameraStatus = document.getElementById("camera-status");

const cameraStartButton =
    document.getElementById("camera-start");

const cameraStopButton =
    document.getElementById("camera-stop");


// ======================================
// 3. AFFICHAGE GENERAL
// ======================================

function updateText(id, value) {

    const element = document.getElementById(id);

    if (element) {
        element.textContent = value;
    }
}


function formatDistance(value) {

    if (value === null || value === undefined) {
        return "-- cm";
    }

    const number = Number(value);

    if (!Number.isFinite(number)) {
        return "-- cm";
    }

    return number.toFixed(1) + " cm";
}


// ======================================
// 4. AFFICHAGE DE LA NAVIGATION
// ======================================

function updateNavigation(data) {

    const robot = data.robot || {};
    const sensors = data.sensors || {};

    const ultrasonic = sensors.ultrasonic || {};
    const infrared = sensors.infrared || {};

    const decision = data.decision || {};

    updateText(
        "robot-status",
        robot.status || "INCONNU"
    );

    updateText(
        "robot-decision",
        decision.decision || "--"
    );

    updateText(
        "robot-speed",
        (decision.speed ?? 0) + " %"
    );

    updateText(
        "robot-direction",
        decision.direction || "NONE"
    );

    updateText(
        "decision-reason",
        decision.reason || "Aucune information"
    );

    updateText(
        "distance-front",
        formatDistance(ultrasonic.front)
    );

    updateText(
        "distance-left",
        formatDistance(ultrasonic.left)
    );

    updateText(
        "distance-right",
        formatDistance(ultrasonic.right)
    );

    updateText("ir-s1", infrared.s1 ?? "--");
    updateText("ir-s2", infrared.s2 ?? "--");
    updateText("ir-s3", infrared.s3 ?? "--");
    updateText("ir-s4", infrared.s4 ?? "--");
    updateText("ir-s5", infrared.s5 ?? "--");
}


// ======================================
// 5. CONNEXION AU SERVEUR
// ======================================

function updateConnection(connected) {

    const dot = document.getElementById("connection-dot");
    const text = document.getElementById("connection-text");

    if (!dot || !text) {
        return;
    }

    if (connected) {

        dot.style.background = "#22c55e";
        text.textContent = "Serveur connectÃ©";

    } else {

        dot.style.background = "#ef4444";
        text.textContent = "Serveur dÃ©connectÃ©";
    }
}


// ======================================
// 6. CHARGEMENT DU DASHBOARD
// ======================================

async function loadDashboard() {

    try {

        const response = await fetch(API.navigation);

        if (!response.ok) {
            throw new Error("Erreur serveur");
        }

        const data = await response.json();

        if (!data.success) {
            throw new Error("RÃ©ponse invalide");
        }

        updateNavigation(data);
        updateConnection(true);

    } catch (error) {

        console.error("Erreur Dashboard :", error);

        updateConnection(false);
    }
}


// ======================================
// 7. HISTORIQUE DE NAVIGATION
// ======================================

function formatDate(timestamp) {

    if (!timestamp) {
        return "--";
    }

    const date = new Date(timestamp);

    if (Number.isNaN(date.getTime())) {
        return "--";
    }

    return date.toLocaleString("fr-FR");
}


function createHistoryRow(item) {

    const row = document.createElement("tr");

    const idCell = document.createElement("td");
    idCell.textContent = item.id ?? "--";
    row.appendChild(idCell);

    const decisionCell = document.createElement("td");

    const badge = document.createElement("span");

    const decision = item.decision || "--";

    badge.textContent = decision;
    badge.className = "decision-badge";

    switch (decision) {

        case "FORWARD":
            badge.classList.add("badge-forward");
            break;

        case "SLOW":
            badge.classList.add("badge-slow");
            break;

        case "AVOID":
            badge.classList.add("badge-avoid");
            break;

        case "STOP":
            badge.classList.add("badge-stop");
            break;

        default:
            badge.classList.add("badge-default");
    }

    decisionCell.appendChild(badge);
    row.appendChild(decisionCell);

    const directionCell = document.createElement("td");
    directionCell.textContent = item.direction || "--";
    row.appendChild(directionCell);

    const speedCell = document.createElement("td");
    speedCell.textContent = (item.speed ?? 0) + " %";
    row.appendChild(speedCell);

    const reasonCell = document.createElement("td");
    reasonCell.textContent = item.reason || "--";
    row.appendChild(reasonCell);

    const dateCell = document.createElement("td");
    dateCell.textContent = formatDate(item.timestamp);
    row.appendChild(dateCell);

    return row;
}


async function loadNavigationHistory() {

    const tableBody =
        document.getElementById("navigation-history");

    if (!tableBody) {
        return;
    }

    try {

        const response = await fetch(API.navigationHistory);

        if (!response.ok) {
            throw new Error("Impossible de charger l'historique");
        }

        const data = await response.json();

        if (!data.success) {
            throw new Error("RÃ©ponse historique invalide");
        }

        const history = data.history || [];

        updateText(
            "history-count",
            data.count ?? history.length
        );

        tableBody.replaceChildren();

        if (history.length === 0) {

            const row = document.createElement("tr");
            const cell = document.createElement("td");

            cell.colSpan = 6;
            cell.textContent = "Aucune dÃ©cision enregistrÃ©e.";

            row.appendChild(cell);
            tableBody.appendChild(row);

        } else {

            history.forEach(item => {
                tableBody.appendChild(createHistoryRow(item));
            });
        }

        updateText(
            "history-message",
            "Historique actualisÃ©."
        );

    } catch (error) {

        console.error("Erreur historique :", error);

        updateText(
            "history-message",
            "Erreur : impossible de rÃ©cupÃ©rer l'historique."
        );
    }
}


// ======================================
// 8. MISSION DE LIVRAISON
// ======================================

async function sendDelivery() {

    const destinationInput =
        document.getElementById("destination");

    const message =
        document.getElementById("delivery-message");

    if (!destinationInput || !message) {
        return;
    }

    const destination = destinationInput.value.trim();

    if (!destination) {

        message.textContent =
            "Veuillez saisir une destination.";

        return;
    }

    try {

        const response = await fetch(API.delivery, {

            method: "POST",

            headers: {
                "Content-Type": "application/json"
            },

            body: JSON.stringify({
                destination: destination
            })

        });

        const data = await response.json();

        if (!response.ok || !data.success) {

            throw new Error(
                data.message || "Mission refusÃ©e"
            );
        }

        message.textContent =
            "Mission enregistrÃ©e : " + destination;

        destinationInput.value = "";

    } catch (error) {

        message.textContent =
            "Erreur : " + error.message;
    }
}


// ======================================
// 9. AFFICHAGE DU RESULTAT IA
// ======================================

function displayPrediction(prediction, automatic = false) {

    const result =
        document.getElementById("ai-result");

    if (!result) {
        return;
    }

    result.replaceChildren();

    const title = document.createElement("h3");

    title.textContent =
        "Panneau dÃ©tectÃ© : " + prediction.class;

    const confidence = document.createElement("p");

    confidence.textContent =
        "Score du modÃ¨le : " + prediction.confidence + " %";

    const message = document.createElement("p");

    message.textContent = automatic
        ? "Analyse automatique par camÃ©ra."
        : (prediction.message || "Analyse terminÃ©e.");

    if (prediction.class === "STOP") {

        title.style.color = "#ef4444";

    } else if (prediction.class === "LEFT") {

        title.style.color = "#3b82f6";

    } else if (prediction.class === "RIGHT") {

        title.style.color = "#22c55e";
    }

    result.appendChild(title);
    result.appendChild(confidence);
    result.appendChild(message);
}


// ======================================
// 10. RECONNAISSANCE MANUELLE D'UNE IMAGE
// ======================================

async function analyzeSign() {

    const imageInput =
        document.getElementById("ai-image");

    const button =
        document.getElementById("ai-analyze");

    const result =
        document.getElementById("ai-result");

    if (!imageInput || !button || !result) {
        return;
    }

    const image = imageInput.files[0];

    if (!image) {

        result.textContent =
            "Veuillez sÃ©lectionner une image.";

        return;
    }

    if (!image.type.startsWith("image/")) {

        result.textContent =
            "Le fichier sÃ©lectionnÃ© n'est pas une image.";

        return;
    }

    try {

        button.disabled = true;

        button.textContent = "Analyse en cours...";

        result.textContent =
            "Le modÃ¨le CNN analyse l'image...";

        const formData = new FormData();

        formData.append("image", image);

        const response = await fetch(API.aiPredict, {

            method: "POST",

            body: formData

        });

        const data = await response.json();

        if (!response.ok || !data.success) {

            throw new Error(
                data.message || "Erreur de reconnaissance"
            );
        }

        displayPrediction(data.prediction);

    } catch (error) {

        console.error("Erreur reconnaissance IA :", error);

        result.textContent =
            "Erreur IA : " + error.message;

    } finally {

        button.disabled = false;

        button.textContent =
            "Analyser le panneau";
    }
}


// ======================================
// 11. ANALYSE AUTOMATIQUE DE LA CAMERA
// ======================================

async function analyzeCameraImage(base64Image) {

    if (!cameraRunning || aiBusy) {
        return;
    }

    const now = Date.now();

    if (now - lastAIAnalysis < AI_INTERVAL) {
        return;
    }

    aiBusy = true;
    lastAIAnalysis = now;

    try {

        const imageResponse = await fetch(base64Image);

        const imageBlob = await imageResponse.blob();

        const formData = new FormData();

        formData.append(
            "image",
            imageBlob,
            "camera.jpg"
        );

        const response = await fetch(API.aiPredict, {

            method: "POST",

            body: formData

        });

        const data = await response.json();

        if (!response.ok || !data.success) {

            throw new Error(
                data.message || "Erreur IA"
            );
        }

        if (cameraRunning) {

            displayPrediction(
                data.prediction,
                true
            );
        }

    } catch (error) {

        console.error(
            "Erreur IA automatique :",
            error
        );

    } finally {

        aiBusy = false;
    }
}


// ======================================
// 12. CAPTURER UNE IMAGE DE LA CAMERA
// ======================================

async function captureCameraFrame() {

    if (!cameraRunning || cameraBusy) {
        return;
    }

    cameraBusy = true;

    try {

        const response = await fetch(
            CAMERA_API.frame + "?t=" + Date.now()
        );

        const data = await response.json();

        if (!response.ok || !data.success) {

            throw new Error(
                data.message || "Capture impossible"
            );
        }

        if (!cameraRunning) {
            return;
        }

        const imageSource =
            "data:image/jpeg;base64," + data.image;

        cameraFeed.src = imageSource;

        cameraFeed.style.display = "block";

        updateText(
            "camera-status",
            "CamÃ©ra active - Analyse automatique"
        );

        // Envoyer l'image au modÃ¨le CNN
        await analyzeCameraImage(imageSource);

    } catch (error) {

        updateText(
            "camera-status",
            "Erreur de capture : " + error.message
        );

        console.error("Erreur image :", error);

    } finally {

        cameraBusy = false;
    }
}


// ======================================
// 13. DEMARRER LA CAMERA
// ======================================

async function startCamera() {

    if (cameraRunning) {
        return;
    }

    if (!cameraFeed || !cameraStatus) {
        console.error("Ã‰lÃ©ments HTML de la camÃ©ra introuvables.");
        return;
    }

    cameraStartButton.disabled = true;

    cameraStatus.textContent =
        "DÃ©marrage de la camÃ©ra...";

    try {

        const response = await fetch(
            CAMERA_API.start,
            { method: "POST" }
        );

        const data = await response.json();

        if (!response.ok || !data.success) {

            throw new Error(
                data.message || "Impossible de dÃ©marrer la camÃ©ra"
            );
        }

        cameraRunning = true;

        lastAIAnalysis = 0;

        cameraStatus.textContent =
            "CamÃ©ra active";

        cameraStartButton.disabled = true;
        cameraStopButton.disabled = false;

        cameraFeed.style.display = "block";

        const placeholder =
            document.getElementById("camera-placeholder");

        if (placeholder) {
            placeholder.style.display = "none";
        }

        // PremiÃ¨re capture immÃ©diate
        captureCameraFrame();

        // Captures suivantes toutes les secondes
        cameraTimer = setInterval(
            captureCameraFrame,
            CAMERA_INTERVAL
        );

    } catch (error) {

        cameraStatus.textContent =
            "Erreur camÃ©ra : " + error.message;

        cameraStartButton.disabled = false;

        console.error("Erreur camÃ©ra :", error);
    }
}


// ======================================
// 14. ARRETER LA CAMERA
// ======================================

async function stopCamera() {

    if (!cameraRunning) {
        return;
    }

    cameraRunning = false;

    if (cameraTimer !== null) {

        clearInterval(cameraTimer);

        cameraTimer = null;
    }

    cameraStatus.textContent =
        "ArrÃªt de la camÃ©ra...";

    try {

        const response = await fetch(
            CAMERA_API.stop,
            { method: "POST" }
        );

        const data = await response.json();

        if (!response.ok || !data.success) {

            throw new Error(
                data.message || "ArrÃªt impossible"
            );
        }

        cameraStatus.textContent =
            "CamÃ©ra arrÃªtÃ©e";

        cameraFeed.style.display = "none";
        cameraFeed.src = "";

        const placeholder =
            document.getElementById("camera-placeholder");

        if (placeholder) {
            placeholder.style.display = "flex";
        }

    } catch (error) {

        cameraStatus.textContent =
            "Erreur : " + error.message;

        console.error("Erreur arrÃªt camÃ©ra :", error);

    } finally {

        cameraStartButton.disabled = false;
        cameraStopButton.disabled = false;
    }
}


// ======================================
// 15. ARRET D'URGENCE
// ======================================

async function emergencyStop() {

    try {

        const response = await fetch(
            API.emergencyStop,
            { method: "POST" }
        );

        const data = await response.json();

        if (!response.ok || !data.success) {

            throw new Error(
                data.message || "Ã‰chec de l'arrÃªt"
            );
        }

        await loadDashboard();
        await loadNavigationHistory();

        alert("ArrÃªt d'urgence logiciel activÃ©.");

    } catch (error) {

        alert("Erreur : " + error.message);
    }
}


// ======================================
// 16. REINITIALISER L'ARRET D'URGENCE
// ======================================

async function emergencyReset() {

    try {

        const response = await fetch(
            API.emergencyReset,
            { method: "POST" }
        );

        const data = await response.json();

        if (!response.ok || !data.success) {

            throw new Error(
                data.message || "Ã‰chec de la rÃ©initialisation"
            );
        }

        await loadDashboard();

        alert("ArrÃªt d'urgence rÃ©initialisÃ©.");

    } catch (error) {

        alert("Erreur : " + error.message);
    }
}


// ======================================
// 17. INITIALISATION DES EVENEMENTS
// ======================================

function initializeEvents() {

    const deliveryButton =
        document.getElementById("send-delivery");

    const stopButton =
        document.getElementById("emergency-stop");

    const resetButton =
        document.getElementById("emergency-reset");

    const analyzeButton =
        document.getElementById("ai-analyze");

    if (deliveryButton) {
        deliveryButton.addEventListener(
            "click",
            sendDelivery
        );
    }

    if (stopButton) {
        stopButton.addEventListener(
            "click",
            emergencyStop
        );
    }

    if (resetButton) {
        resetButton.addEventListener(
            "click",
            emergencyReset
        );
    }

    if (analyzeButton) {
        analyzeButton.addEventListener(
            "click",
            analyzeSign
        );
    }

    if (cameraStartButton) {
        cameraStartButton.addEventListener(
            "click",
            startCamera
        );
    }

    if (cameraStopButton) {
        cameraStopButton.addEventListener(
            "click",
            stopCamera
        );
    }
}


// ======================================
// 18. INITIALISATION DU DASHBOARD
// ======================================

function initializeDashboard() {

    initializeEvents();

    loadDashboard();

    loadNavigationHistory();

    // Actualiser les donnÃ©es toutes les secondes
    setInterval(loadDashboard, 1000);

    // Actualiser l'historique toutes les 5 secondes
    setInterval(loadNavigationHistory, 5000);

    // Etat initial de la camÃ©ra
    if (cameraFeed) {
        cameraFeed.style.display = "none";
    }

    if (cameraStartButton) {
        cameraStartButton.disabled = false;
    }

    if (cameraStopButton) {
        cameraStopButton.disabled = true;
    }
}


// Lancer le dashboard quand le HTML est chargÃ©
if (document.readyState === "loading") {

    document.addEventListener(
        "DOMContentLoaded",
        initializeDashboard
    );

} else {

    initializeDashboard();
}



// Gestion des boutons Voix ON/OFF et Test
document.addEventListener("DOMContentLoaded", () => {
    const toggleBtn = document.getElementById("voice-toggle");
    const testBtn = document.getElementById("voice-test");

    if (toggleBtn) {
        toggleBtn.addEventListener("click", () => {
            voiceEnabled = !voiceEnabled;
            toggleBtn.textContent = voiceEnabled ? "🔊 Voix : ON" : "🔇 Voix : OFF";
            toggleBtn.style.background = voiceEnabled ? "#1e3a8a" : "#334155";
            if (!voiceEnabled && "speechSynthesis" in window) {
                window.speechSynthesis.cancel();
            } else if (voiceEnabled) {
                speakFrench("Synthèse vocale activée");
            }
        });
    }

    if (testBtn) {
        testBtn.addEventListener("click", () => {
            playSignAlert("ARRIVAL"); speakFrench("Système vocal ORION Rover opérationnel.");
        });
    }
});

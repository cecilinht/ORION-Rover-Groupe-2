
// ============================================================================
// CARTE 2D INTERACTIVE & RADAR 3 ZONES EN TEMPS REEL
// ============================================================================
let roverTrail = [{ x: 110, y: 160 }];
let roverAngle = 0;

function drawRoverMap(frontDist, leftDist, rightDist, status) {
    const canvas = document.getElementById("rover-map");
    if (!canvas) return;
    const ctx = canvas.getContext("2d");
    const W = canvas.width, H = canvas.height;

    ctx.clearRect(0, 0, W, H);

    // Grille metrique (1 carreau = 50 cm)
    ctx.strokeStyle = "rgba(56, 189, 248, 0.08)";
    ctx.lineWidth = 1;
    for (let x = 0; x <= W; x += 40) { ctx.beginPath(); ctx.moveTo(x, 0); ctx.lineTo(x, H); ctx.stroke(); }
    for (let y = 0; y <= H; y += 40) { ctx.beginPath(); ctx.moveTo(0, y); ctx.lineTo(W, y); ctx.stroke(); }

    // Piste noire ovale du circuit (6m x 4m)
    ctx.strokeStyle = "rgba(148, 163, 184, 0.35)";
    ctx.lineWidth = 14;
    ctx.strokeRect(70, 50, W - 140, H - 100);
    ctx.strokeStyle = "#38bdf8";
    ctx.lineWidth = 1.5;
    ctx.setLineDash([8, 6]);
    ctx.strokeRect(70, 50, W - 140, H - 100);
    ctx.setLineDash([]);

    // Points de livraison (Base, Zone A, Zone B, Zone C)
    const zones = [
        { x: 70, y: 160, label: "BASE", color: "#10b981" },
        { x: W / 2, y: 50, label: "ZONE A", color: "#a855f7" },
        { x: W - 70, y: 160, label: "ZONE B", color: "#a855f7" },
        { x: W / 2, y: H - 50, label: "ZONE C", color: "#a855f7" }
    ];
    zones.forEach(z => {
        ctx.fillStyle = z.color;
        ctx.beginPath(); ctx.arc(z.x, z.y, 6, 0, Math.PI * 2); ctx.fill();
        ctx.fillStyle = "#e2e8f0";
        ctx.font = "bold 11px sans-serif";
        ctx.fillText(z.label, z.x - 20, z.y - 11);
    });

    // Mise a jour position si le robot roule
    const cur = roverTrail[roverTrail.length - 1];
    if (status === "EN_MISSION" || (frontDist !== null && frontDist > 15)) {
        const nx = Math.min(W - 70, Math.max(70, cur.x + Math.cos(roverAngle) * 2.2));
        const ny = Math.min(H - 50, Math.max(50, cur.y + Math.sin(roverAngle) * 2.2));
        if (nx >= W - 72 && roverAngle === 0) roverAngle = Math.PI / 2;
        else if (ny >= H - 52 && Math.abs(roverAngle - Math.PI / 2) < 0.1) roverAngle = Math.PI;
        else if (nx <= 72 && Math.abs(roverAngle - Math.PI) < 0.1) roverAngle = -Math.PI / 2;
        else if (ny <= 52 && Math.abs(roverAngle + Math.PI / 2) < 0.1) roverAngle = 0;

        if (status === "EN_MISSION") {
            roverTrail.push({ x: nx, y: ny });
            if (roverTrail.length > 150) roverTrail.shift();
        }
    }

    const pos = roverTrail[roverTrail.length - 1];

    // Trace de la trajectoire odometrique
    if (roverTrail.length > 1) {
        ctx.strokeStyle = "rgba(56, 189, 248, 0.7)";
        ctx.lineWidth = 2.5;
        ctx.beginPath();
        ctx.moveTo(roverTrail.x, roverTrail.y);
        for (let i = 1; i < roverTrail.length; i++) ctx.lineTo(roverTrail[i].x, roverTrail[i].y);
        ctx.stroke();
    }

    // Faisceau Ultrason Avant (couleur selon zone Verte >40, Orange 15-40, Rouge <15)
    const fDist = frontDist !== null ? frontDist : 80;
    const beamLen = Math.min(90, fDist * 1.1);
    const beamColor = fDist < 15 ? "#ef4444" : (fDist <= 40 ? "#f59e0b" : "#10b981");

    ctx.fillStyle = beamColor + "33";
    ctx.beginPath();
    ctx.moveTo(pos.x, pos.y);
    ctx.arc(pos.x, pos.y, beamLen, roverAngle - 0.35, roverAngle + 0.35);
    ctx.closePath();
    ctx.fill();

    // Dessin du Rover
    ctx.save();
    ctx.translate(pos.x, pos.y);
    ctx.rotate(roverAngle);
    ctx.fillStyle = "#38bdf8";
    ctx.fillRect(-12, -9, 24, 18);
    ctx.fillStyle = "#ffffff";
    ctx.fillRect(6, -6, 4, 12); // Avant du robot
    ctx.restore();

    // Legende radar en haut a gauche
    ctx.fillStyle = "#94a3b8";
    ctx.font = "11px monospace";
    ctx.fillText(`Avant: ${fDist}cm | Gauche: ${leftDist ?? "--"}cm | Droite: ${rightDist ?? "--"}cm`, 14, 20);
}

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



const CAMERA_INTERVAL = 1500;

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

        text.textContent = "Serveur connecté";



    } else {



        dot.style.background = "#ef4444";

        text.textContent = "Serveur déconnecté";

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

            throw new Error("Réponse invalide");

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

            throw new Error("Réponse historique invalide");

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

            cell.textContent = "Aucune décision enregistrée.";



            row.appendChild(cell);

            tableBody.appendChild(row);



        } else {



            history.forEach(item => {

                tableBody.appendChild(createHistoryRow(item));

            });

        }



        updateText(

            "history-message",

            "Historique actualisé."

        );



    } catch (error) {



        console.error("Erreur historique :", error);



        updateText(

            "history-message",

            "Erreur : impossible de récupérer l'historique."

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

                data.message || "Mission refusée"

            );

        }



        message.textContent =

            "Mission enregistrée : " + destination;



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

        "Panneau détecté : " + prediction.class;



    const confidence = document.createElement("p");



    confidence.textContent =

        "Score du modèle : " + prediction.confidence + " %";



    const message = document.createElement("p");



    message.textContent = automatic

        ? "Analyse automatique par caméra."

        : (prediction.message || "Analyse terminée.");



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

            "Veuillez sélectionner une image.";



        return;

    }



    if (!image.type.startsWith("image/")) {



        result.textContent =

            "Le fichier sélectionné n'est pas une image.";



        return;

    }



    try {



        button.disabled = true;



        button.textContent = "Analyse en cours...";



        result.textContent =

            "Le modèle CNN analyse l'image...";



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



        if (!cameraFeed.src.includes("/api/video/stream")) { cameraFeed.src = "/api/video/stream?t=" + Date.now(); }



        cameraFeed.style.display = "block";



        updateText(

            "camera-status",

            "Caméra active - Analyse automatique"

        );



        // Envoyer l'image au modèle CNN

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

        console.error("Éléments HTML de la caméra introuvables.");

        return;

    }



    cameraStartButton.disabled = true;



    cameraStatus.textContent =

        "Démarrage de la caméra...";



    try {



        const response = await fetch(

            CAMERA_API.start,

            { method: "POST" }

        );



        const data = await response.json();



        if (!response.ok || !data.success) {



            throw new Error(

                data.message || "Impossible de démarrer la caméra"

            );

        }



        cameraRunning = true;



        lastAIAnalysis = 0;



        cameraStatus.textContent =

            "Caméra active";



        cameraStartButton.disabled = true;

        cameraStopButton.disabled = false;



        cameraFeed.style.display = "block";



        const placeholder =

            document.getElementById("camera-placeholder");



        if (placeholder) {

            placeholder.style.display = "none";

        }



        // Première capture immédiate

        captureCameraFrame();



        // Captures suivantes toutes les secondes

        cameraTimer = setInterval(

            captureCameraFrame,

            CAMERA_INTERVAL

        );



    } catch (error) {



        cameraStatus.textContent =

            "Erreur caméra : " + error.message;



        cameraStartButton.disabled = false;



        console.error("Erreur caméra :", error);

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

        "Arrêt de la caméra...";



    try {



        const response = await fetch(

            CAMERA_API.stop,

            { method: "POST" }

        );



        const data = await response.json();



        if (!response.ok || !data.success) {



            throw new Error(

                data.message || "Arrêt impossible"

            );

        }



        cameraStatus.textContent =

            "Caméra arrêtée";



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



        console.error("Erreur arrêt caméra :", error);



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

                data.message || "Échec de l'arrêt"

            );

        }



        await loadDashboard();

        await loadNavigationHistory();



        alert("Arrêt d'urgence logiciel activé.");



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

                data.message || "Échec de la réinitialisation"

            );

        }



        await loadDashboard();



        alert("Arrêt d'urgence réinitialisé.");



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



    // Actualiser les données toutes les secondes

    setInterval(loadDashboard, 1000);



    // Actualiser l'historique toutes les 5 secondes

    setInterval(loadNavigationHistory, 5000);



    // Etat initial de la caméra

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





// Lancer le dashboard quand le HTML est chargé

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



// Bouton Croix (X) pour fermer/masquer la vignette camera flottante
document.addEventListener("DOMContentLoaded", () => {
    const camSection = document.getElementById("camera");
    if (!camSection || document.getElementById("cam-close-btn")) return;

    const closeBtn = document.createElement("button");
    closeBtn.id = "cam-close-btn";
    closeBtn.type = "button";
    closeBtn.title = "Fermer la caméra";
    closeBtn.textContent = "✕";
    camSection.appendChild(closeBtn);

    const reopenBtn = document.createElement("button");
    reopenBtn.id = "cam-reopen-btn";
    reopenBtn.type = "button";
    reopenBtn.innerHTML = "📷 Ouvrir la caméra";
    document.body.appendChild(reopenBtn);

    closeBtn.addEventListener("click", () => {
        camSection.classList.add("cam-hidden");
        reopenBtn.style.display = "flex";
    });

    reopenBtn.addEventListener("click", () => {
        camSection.classList.remove("cam-hidden");
        reopenBtn.style.display = "none";
    });
});

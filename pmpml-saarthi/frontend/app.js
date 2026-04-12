const BASE_URL = 'http://localhost:8000';

const ui = {
    destInput: document.getElementById('destinationInput'),
    micBtn: document.getElementById('micBtn'),
    goBtn: document.getElementById('goBtn'),
    statusMsg: document.getElementById('statusMsg'),
    resultsSection: document.getElementById('resultsSection'),
    routeNameVal: document.getElementById('routeNameVal'),
    etaVal: document.getElementById('etaVal'),
    nearestStopVal: document.getElementById('nearestStopVal'),
    destStopVal: document.getElementById('destStopVal'),
    speechVal: document.getElementById('speechVal'),
    playSpeechBtn: document.getElementById('playSpeechBtn')
};

// State
let userLoc = { lat: 18.5156, lng: 73.8404 }; // Default to Pune location if Geolocation fails
let currentSpeech = '';

// Initialize
function init() {
    ui.goBtn.addEventListener('click', handleFindRoute);
    ui.micBtn.addEventListener('click', handleVoiceInput);
    ui.playSpeechBtn.addEventListener('click', playSpeech);
    ui.destInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') handleFindRoute();
    });

    // Try getting user's real location
    if (navigator.geolocation) {
        navigator.geolocation.getCurrentPosition(
            (pos) => {
                userLoc = { lat: pos.coords.latitude, lng: pos.coords.longitude };
                setStatus("Location acquired.", "success");
            },
            (err) => {
                console.warn("Geolocation denied or failed. Using fallback location.");
                setStatus("Using default location (Pune).", "warning");
            }
        );
    } else {
        setStatus("Geolocation not supported.", "warning");
    }
}

function setStatus(msg, type="info") {
    ui.statusMsg.textContent = msg;
    ui.statusMsg.style.color = type === 'error' ? 'var(--danger)' : 
                               type === 'success' ? 'var(--success)' : 'var(--text-muted)';
}

async function handleFindRoute() {
    const dest = ui.destInput.value.trim();
    if (!dest) {
        setStatus("Please enter a destination.", "error"); return;
    }

    setStatus("Planning route...");
    ui.resultsSection.classList.add('hidden');
    ui.goBtn.disabled = true;

    try {
        const res = await fetch(`${BASE_URL}/find-route`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                user_lat: userLoc.lat,
                user_lng: userLoc.lng,
                destination_name: dest
            })
        });

        if (!res.ok) throw new Error("Backend error or destination not found.");

        const data = await res.json();
        
        // Update UI
        ui.routeNameVal.textContent = data.route_name;
        ui.etaVal.textContent = `${data.next_bus_eta_minutes} min`;
        ui.nearestStopVal.textContent = data.nearest_stop.name;
        ui.destStopVal.textContent = data.destination_stop.name;
        ui.speechVal.textContent = `"${data.speech}"`;
        currentSpeech = data.speech;

        ui.resultsSection.classList.remove('hidden');
        setStatus("Route found!", "success");
        speakText(currentSpeech);

    } catch (err) {
        setStatus(err.message, "error");
    } finally {
        ui.goBtn.disabled = false;
    }
}

// Simple Web Speech API Implementation for Speech-To-Text
function handleVoiceInput() {
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (!SpeechRecognition) {
        setStatus("Speech Recognition not supported in this browser.", "error");
        return;
    }

    const recognition = new SpeechRecognition();
    recognition.lang = 'en-US';
    recognition.interimResults = false;

    recognition.onstart = () => {
        ui.micBtn.classList.add('recording');
        setStatus("Listening...");
    };

    recognition.onresult = async (event) => {
        const text = event.results[0][0].transcript;
        ui.destInput.value = text;
        setStatus("Parsing destination...");
        
        try {
            const res = await fetch(`${BASE_URL}/parse-destination`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ text })
            });
            if (res.ok) {
                const data = await res.json();
                if (data.destination) {
                    ui.destInput.value = data.destination;
                    setStatus("Destination parsed. Press GO to find route.", "success");
                } else {
                    setStatus("Could not understand destination.", "error");
                }
            } else {
                 setStatus("Could not parse destination.", "error");
            }
        } catch (err) {
            setStatus("Parse error.", "error");
        }
    };

    recognition.onspeechend = () => recognition.stop();
    recognition.onend = () => ui.micBtn.classList.remove('recording');
    recognition.onerror = () => {
        ui.micBtn.classList.remove('recording');
        setStatus("Microphone error.", "error");
    };

    recognition.start();
}

function speakText(text) {
    if ('speechSynthesis' in window) {
        // Cancel any ongoing speech
        window.speechSynthesis.cancel();
        const u = new SpeechSynthesisUtterance(text);
        u.lang = 'en-US';
        window.speechSynthesis.speak(u);
    }
}

function playSpeech() {
    if(currentSpeech) speakText(currentSpeech);
}

// Start app
init();

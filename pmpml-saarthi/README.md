# PMPML Saarthi 🚌🗣️

**Voice-first mobile assistant for visually impaired users to navigate Pune's PMPML bus network.**

PMPML Saarthi lets users speak their destination, finds the nearest bus stop, plans the optimal route, and provides real-time voice alerts during their ride — all without needing to look at the screen.

---

## Quick Start (under 10 steps)

### Prerequisites

| Tool | Version | Purpose |
|------|---------|---------|
| Python | 3.10+ | Backend |
| Node.js | 18+ | Expo CLI |
| Expo Go | Latest | Mobile testing (phone) |
| Firebase (optional) | — | Firestore database |

### 1. Clone & enter the project

```bash
git clone <repo-url> pmpml-saarthi
cd pmpml-saarthi
```

### 2. Create your `.env` file

```bash
cp .env.example .env
# Edit .env and fill in your keys (see below)
```

### 3. Start the backend

**Option A — Automated (Linux/macOS):**
```bash
chmod +x run.sh
./run.sh
```

**Option B — Manual (any OS):**
```bash
cd backend
python -m venv .venv

# Activate the virtual environment:
# macOS/Linux:
source .venv/bin/activate
# Windows:
.venv\Scripts\activate

pip install -r requirements.txt
python -m spacy download en_core_web_sm   # optional

uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

### 4. (Optional) Seed Firebase

```bash
python firebase/seed_data.py
```

> If Firebase credentials are not configured, the backend uses built-in fallback data automatically.

### 5. Start the mobile app

```bash
cd mobile
npm install
npx expo start
```

Scan the QR code with **Expo Go** on your phone, or press `a` (Android emulator) / `i` (iOS simulator).

### 6. Configure backend URL for mobile

Edit `mobile/services/apiService.js` — update `BASE_URL`:

| Device | URL |
|--------|-----|
| Android Emulator | `http://10.0.2.2:8000` |
| iOS Simulator | `http://localhost:8000` |
| Physical Device | `http://<your-LAN-IP>:8000` |

### 7. Test it!

1. Open the app → hear: *"Welcome to PMPML Saarthi. Where would you like to go?"*
2. Type **Shivajinagar** in the text field and tap **GO**
3. See route details → tap **Start Ride**
4. Watch the ride tracker with stop countdown

---

## Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `FIREBASE_CREDENTIALS_PATH` | No* | Path to Firebase service account JSON |
| `GOOGLE_MAPS_API_KEY` | No* | Google Maps API key (for future geocoding) |
| `BACKEND_URL` | No | Override backend URL (default: `http://localhost:8000`) |

> *The backend works without Firebase credentials using built-in sample data.

---

## Architecture

```
┌─────────────────┐    HTTP/JSON     ┌──────────────────┐     Firestore
│  React Native   │ ◄──────────────► │   FastAPI         │ ◄──────────►  Firebase
│  (Expo)         │                  │   Python Backend   │   (or fallback)
│                 │                  │                    │
│  • TTS (speak)  │                  │  /parse-destination│
│  • STT (record) │                  │  /find-route       │
│  • GPS tracking │                  │  /check-proximity  │
└─────────────────┘                  └──────────────────┘
```

---

## API Endpoints

### `POST /parse-destination`
Extracts the destination name from raw voice text.

**Request:**
```json
{ "text": "Take me to Shivajinagar" }
```
**Response:**
```json
{ "destination": "Shivajinagar", "command": null }
```

### `POST /find-route`
Plans a trip: finds the nearest stop, destination stop, route, and ETA.

**Request:**
```json
{
  "user_lat": 18.5156,
  "user_lng": 73.8404,
  "destination_name": "Shivajinagar"
}
```
**Response:**
```json
{
  "nearest_stop": { "id": "deccan_gymkhana", "name": "Deccan Gymkhana", "lat": 18.5156, "lng": 73.8404, "distance_meters": 42.3 },
  "destination_stop": { "id": "shivajinagar", "name": "Shivajinagar", "lat": 18.5308, "lng": 73.8474 },
  "route_name": "Route 156",
  "route_id": "route_156",
  "next_bus_eta_minutes": 8,
  "stops_on_journey": ["Deccan Gymkhana", "Shivajinagar"],
  "total_stops": 1,
  "walk_direction": "north",
  "walk_distance_meters": 42.3,
  "speech": "Walk 42 meters north to Deccan Gymkhana Bus Stop. Board Bus 156 arriving in 8 minutes. Your journey has 1 stops. I will alert you before your stop."
}
```

### `POST /check-proximity`
Checks distance between user and a target stop (for alight alerts).

**Request:**
```json
{
  "user_lat": 18.5290,
  "user_lng": 73.8470,
  "target_stop_lat": 18.5308,
  "target_stop_lng": 73.8474
}
```
**Response:**
```json
{
  "distance_meters": 204.7,
  "alert": false,
  "message": "You are 204 meters from your stop."
}
```

---

## Sample Data

### Bus Stops (10 Pune locations)

| # | Name | Lat | Lng | Routes |
|---|------|-----|-----|--------|
| 1 | Swargate | 18.5018 | 73.8636 | 156, 11 |
| 2 | Shivajinagar | 18.5308 | 73.8474 | 156 |
| 3 | Deccan Gymkhana | 18.5156 | 73.8404 | 156 |
| 4 | Pune Station | 18.5297 | 73.8743 | 156, 50 |
| 5 | Katraj | 18.4529 | 73.8682 | 11 |
| 6 | Hadapsar | 18.5018 | 73.9252 | 50 |
| 7 | Kothrud Depot | 18.5074 | 73.8077 | 11 |
| 8 | Wakad | 18.5991 | 73.7601 | — |
| 9 | Hinjewadi | 18.5912 | 73.7389 | 50 |
| 10 | Warje | 18.4849 | 73.8007 | 11 |

### Routes (3 lines)

| Route | Stops | Frequency |
|-------|-------|-----------|
| 156 | Swargate → Deccan → Shivajinagar → Pune Station | 15 min |
| 11 | Katraj → Swargate → Warje → Kothrud Depot | 20 min |
| 50 | Pune Station → Hadapsar → Hinjewadi | 25 min |

---

## Accessibility Features

- **Voice-first**: Every action is spoken aloud via TTS
- **High contrast**: Black background + Yellow text (WCAG AAA compliant)
- **Large touch targets**: All buttons ≥ 80×80px
- **No visual-only info**: Icons always paired with text/voice
- **Voice commands**: "go to [place]", "repeat", "cancel", "where am I"
- **Vibration feedback**: Haptic alerts before and at destination

---

## Docker (optional)

```bash
docker-compose up --build
```

Backend will be available at `http://localhost:8000`.

---

## Project Structure

```
pmpml-saarthi/
├── backend/
│   ├── main.py              # FastAPI app with 3 endpoints
│   ├── nlp_utils.py         # Regex + spaCy destination extractor
│   ├── geo_utils.py         # Haversine distance & bearing calculator
│   ├── firebase_client.py   # Firestore client (+ fallback data)
│   ├── requirements.txt     # Python dependencies
│   └── Dockerfile           # Container build file
├── mobile/
│   ├── App.js               # React Navigation root
│   ├── package.json          # Expo dependencies
│   ├── app.json              # Expo config + permissions
│   ├── screens/
│   │   ├── HomeScreen.js     # Mic button + greeting
│   │   ├── RouteScreen.js    # Route info cards
│   │   └── RideScreen.js     # Live ride tracker
│   └── services/
│       ├── voiceService.js   # TTS + STT wrapper
│       ├── apiService.js     # Axios API calls
│       └── locationService.js# GPS helpers
├── firebase/
│   ├── firestore_schema.md   # Collection schema docs
│   └── seed_data.py          # Firestore seed script
├── run.sh                    # One-command local startup
├── docker-compose.yml        # Docker config
├── .env.example              # Required env vars template
└── README.md                 # This file
```

---

## License

MIT — Built for Pune's visually impaired commuters. 🇮🇳

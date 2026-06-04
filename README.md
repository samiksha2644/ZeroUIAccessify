# TransitVoice

1. Project Overview
TransitVoice is an audio-only public transit assistant designed for visually impaired users navigating the PMPML bus network in Pune, India. It solves the critical problem of inaccessible transit apps by relying entirely on voice commands and audio feedback for planning journeys, tracking buses, and managing digital payments. 

2. Architecture Diagram
```text
[ Mobile App (Expo) ]
       |  (Voice / HTTP)
       v
[ FastAPI Backend ]
       |
       +---> [ Firebase ]
       |       - Firestore (Static Data, Wallet, Trips)
       |       - Realtime DB (Live GPS tracking)
       |
       +---> [ OpenAI APIs ]
       |       - Whisper (Speech to text)
       |       - TTS-1 Nova (Text to speech)
       |
       +---> [ Google Maps ]
               - Places API (Nearest stops)
               - Directions API (Route planning)
```

3. Tech Stack
| Technology          | Purpose                                                                 |
|---------------------|-------------------------------------------------------------------------|
| React Native + Expo | Mobile frontend with audio recording capabilities and voice output.     |
| FastAPI             | High-performance async Python backend to route requests.                |
| Firebase Admin SDK  | Database interactions (Firestore for static, Realtime DB for live).     |
| OpenAI Whisper      | Transcribes the user's audio commands.                                  |
| OpenAI TTS-1        | Generates natural, spoken responses using the "Nova" voice.             |
| Google Maps APIs    | Geocoding, finding nearby transit stations, and generating route paths. |
| Geopy               | Calculating point-to-point distance using offline math logic.           |

4. Prerequisites
- Python 3.11+
- Node 18+
- Expo CLI
- Firebase CLI
- A Google Cloud account
- An OpenAI account

5. Environment Setup
```bash
# Clone the repository
git clone https://github.com/samiksha2644/ZeroUIAccessify/.git
cd ZeroUIAccessify/backend

# Create and activate Python virtual environment
python -m venv venv
# On Windows:
venv\Scripts\activate
# On MacOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Copy environment variables
cp .env.example .env
```
Fill in the `.env` file using these direct URLs:
- **OpenAI API Key**: [OpenAI Platform](https://platform.openai.com/api-keys)
- **Google Maps API Key**: [Google Cloud Console](https://console.cloud.google.com/google/maps-apis/api-list)
- **Firebase Keys**: [Firebase Console](https://console.firebase.google.com/)

6. Firebase Setup
1. Go to the Firebase Console and Create a new Firebase project.
2. Navigate to "Build -> Firestore Database" and Create Database.
3. Navigate to "Build -> Realtime Database" and Create Database.
4. Go to "Project Settings -> Service Accounts", click "Generate new private key", and download the JSON file. Save it inside the `backend` folder as `serviceAccountKey.json`.
5. Set the `FIREBASE_REALTIME_DB_URL` in your `.env` (it looks like `https://your-project.firebaseio.com`).
6. Set Firestore security rules (Database -> Rules) for development:
```javascript
rules_version = '2';
service cloud.firestore {
  match /databases/{database}/documents {
    match /{document=**} {
      allow read, write: if true;
    }
  }
}
```

7. Seeding the database
Run the following scripts from the `backend` directory to populate stops and routes from OpenCity data:
```bash
python seed/seed_stops.py
# Expected output:
# Downloading KML file...
# Downloaded successfully.
# Parsed <N> stops. Seeding Firestore via batched writes...
# Written 500 stops...
# Written <N> stops. Done!

python seed/seed_routes.py
# Expected output:
# Downloading Routes CSV...
# Downloaded successfully.
# Written 500 routes...
# Written <N> routes. Done!
```

8. Running the backend
Start the FastAPI server using Uvicorn:
```bash
uvicorn app.main:app --reload
# Expected output:
# INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
# INFO:     Started reloader process [...]
# INFO:     Started server process [...]
# INFO:     Waiting for application startup.
# INFO:     Application startup complete.
```

9. API Reference Table

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| GET | `/api/v1/health` | Pings backend and DB health | No |
| POST | `/api/v1/auth/register` | Registers a new user | No |
| GET | `/api/v1/auth/user/{user_id}` | Gets user profile | Bearer (Expected) |
| GET | `/api/v1/stops/nearest` | Finds 3 nearest stops to coordinates | No |
| POST | `/api/v1/journey/plan` | Finds common route between two stops | Yes |
| POST | `/api/v1/trip/start` | Creates trip, checks balance, writes to RTDB | Yes |
| PUT | `/api/v1/trip/{id}/location` | Real-time GPS check for off-route / arrival | Yes |
| POST | `/api/v1/trip/{id}/end` | Deducts final fare, marks complete | Yes |
| GET | `/api/v1/wallet/{user_id}` | Gets wallet balance and recent activity | Yes |
| POST | `/api/v1/wallet/topup` | Adds funds to wallet atomically | Yes |
| GET | `/api/v1/wallet/{id}/transactions` | Gets paginated transaction list | Yes |
| POST | `/api/v1/voice/command` | Processes speech, routes intent, returns audio | Yes |

10. Mobile App Setup
```bash
# In another terminal window, go to root folder (or frontend app folder)
cd ..
npm install
# or yarn install

# Install Expo CLI globally if not already installed
npm install -g expo-cli

# Start the Expo development server
npx expo start
```
Make sure your mobile app points to your local machine IP (e.g., `http://192.168.1.100:8000`) instead of `localhost` in `services/api.js`.

11. Demo Script (for Hackathon Judges)
**Goal:** Show a blind user planning a trip and tracking it within 3 minutes.
1. **Open App:** "We open TransitVoice. The interface is high-contrast, strictly relying on audio."
2. **Tap & Speak:** Tap the mic button. Say: *"Nearest stop."*
3. **Listen:** The app replies via TTS: *"The nearest stop is Shivaji Nagar, 200 meters away."*
4. **Tap & Speak:** Tap mic again. Say: *"Take me to Pune Station."*
5. **Listen:** Setup shows route. App says: *"Planning a journey to Pune Station. Route 43 will take you there."*
6. **Simulate Trip Location Update:** (Hit the `/api/v1/trip/{trip_id}/location` from VSCode ThunderClient to mock the user moving).
7. **Trip End:** Call the `/api/v1/trip/{trip_id}/end` or say *"End trip"*. App replies: *"Your trip has ended. 20 rupees have been deducted from your wallet."*

12. Folder Structure
```text
.
├── backend/
│   ├── .env.example
│   ├── requirements.txt
│   ├── app/
│   │   ├── config.py             # Environment configuration
│   │   ├── firebase.py           # DB Singleton setup
│   │   ├── main.py               # FastAPI App instance
│   │   ├── models/
│   │   │   └── schemas.py        # Pydantic v2 data models
│   │   ├── routers/              # API Endpoints
│   │   │   ├── auth.py
│   │   │   ├── journey.py
│   │   │   ├── stops.py
│   │   │   ├── trip.py
│   │   │   ├── voice.py
│   │   │   └── wallet.py
│   │   └── services/             # Business Logic & External APIs
│   │       ├── detection.py
│   │       ├── fare.py
│   │       ├── maps.py
│   │       ├── tts.py
│   │       └── whisper.py
│   └── seed/
│       ├── seed_routes.py
│       └── seed_stops.py
├── app/                     # Expo UI Code
├── components/              
└── README.md                # You are reading this
```

13. Known Limitations (Hackathon Build)
- **Fare Calculation:** Static fallback to 15.0/20.0 INR used if specific zone mapping data is not populated.
- **NLP intent engine:** Relies on hardcoded substring matching (e.g. `if "nearest stop" in ...`) rather than a robust conversational agent/LLM router.
- **Route Tracking Polyline:** Simple geodesic point distance mock is used. Real Map matching algorithm is excluded for brevity.
- **Data Completeness:** PMPML dataset from OpenCity is static and might have anomalies in coordinate formatting.

14. Team & Contacts

| Name | Role | Contact |
|------|------|---------|
| Pranav Shirode | Backend Engineer | pranav.shirode24@gmail.com |
| Samiksha Mote | Frontend Engineer, App Dev | samiksha.mote24@pccoepune.com |
| Tanvi Chavan | Product/Design | - |

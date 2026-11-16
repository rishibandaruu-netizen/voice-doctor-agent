# CareVoice – Voice AI Doctor Appointment Assistant

CareVoice is an AI-powered voice assistant that helps patients check doctor availability, book appointments, and cancel appointments through natural voice conversations.

## Features

- Voice conversations using Pipecat.
- Speech recognition using ElevenLabs.
- AI responses using Google Gemini.
- Voice responses using ElevenLabs Text-to-Speech.
- Check doctor availability by specialty.
- Book doctor appointments.
- Cancel existing appointments.
- Confirm phone numbers before booking or cancellation.
- SQLite database for doctors, slots, and appointments.
- Live browser dashboard with conversation transcripts and appointment updates.
- Voice activity detection using Silero VAD.

## Technology Stack

- Python
- Pipecat
- Google Gemini
- ElevenLabs STT and TTS
- SQLite
- FastAPI
- HTML, CSS, JavaScript
- Vite
- WebRTC

## Project Structure

```text
voice-doctor-agent/
├── backend/
│   ├── agent.py
│   ├── bot.py
│   ├── database.py
│   ├── dashboard_api.py
│   ├── tools.py
│   └── .env
├── frontend/
│   ├── index.html
│   ├── script.js
│   └── style.css
├── .env.example
├── .gitignore
├── requirements.txt
├── package.json
└── README.md
```

## Setup Instructions

### 1. Clone the repository

```bash
git clone https://github.com/rishibandaruu-netizen/voice-doctor-agent.git
cd voice-doctor-agent
```

### 2. Create and activate a virtual environment

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

### 3. Install Python dependencies

```powershell
pip install -r requirements.txt
```

### 4. Install frontend dependencies

```powershell
npm install
```

### 5. Configure environment variables

Create the backend environment file:

```powershell
Copy-Item .env.example backend/.env
```

Add your API credentials inside `backend/.env`:

```env
GOOGLE_API_KEY=your_google_api_key
ELEVENLABS_API_KEY=your_elevenlabs_api_key
ELEVENLABS_VOICE_ID=your_elevenlabs_voice_id
```

Never upload your actual API keys to GitHub.

### 6. Initialize the database

```powershell
python -m backend.database
```

## Run the Application

Open three separate terminals in the project directory.

**Terminal 1 – Start the voice assistant**

```powershell
python -m backend.bot -t webrtc
```

**Terminal 2 – Start the dashboard API**

```powershell
uvicorn backend.dashboard_api:app --host 0.0.0.0 --port 8000
```

**Terminal 3 – Start the frontend**

```powershell
npm run dev
```

Open the application in your browser:

http://localhost:5173/

## Available Voice Assistant Functions

1. `check_doctor_availability` – Checks available doctors and appointment slots.
2. `book_appointment` – Books an appointment after confirming the patient's phone number and permission.
3. `cancel_appointment` – Cancels an appointment after verifying the appointment ID and phone number.

## Database

SQLite stores:

- Doctor details
- Available appointment slots
- Patient appointment records
- Appointment status

## Security and Validation

- API credentials are stored in a local environment file.
- Environment files and database files are excluded from Git.
- Phone numbers are validated before appointment actions.
- Phone numbers are read back for patient confirmation.
- Booking and cancellation require explicit confirmation.


## Author

**Rishi Bandaru**  
IIIT Kottayam | Electronics and Communication Engineering  
GitHub: [@rishibandaruu-netizen](https://github.com/rishibandaruu-netizen)


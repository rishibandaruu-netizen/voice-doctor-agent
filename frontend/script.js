
import { PipecatClient } from "@pipecat-ai/client-js";
import { SmallWebRTCTransport } from "@pipecat-ai/small-webrtc-transport";

const status = document.getElementById("status");
const message = document.getElementById("call-message");
const transcript = document.getElementById("transcript");
const startButton = document.getElementById("startCall");
const endButton = document.getElementById("endCall");

let client;

function addMessage(speaker, text) {
    const empty = transcript.querySelector(".empty");
    if (empty) empty.remove();

    const line = document.createElement("p");
    line.className = "message";
    line.textContent = `${speaker}: ${text}`;
    transcript.appendChild(line);
    transcript.scrollTop = transcript.scrollHeight;
}

client = new PipecatClient({
    transport: new SmallWebRTCTransport(),
    enableMic: true,
    enableCam: false,

    callbacks: {
        onConnected: () => {
            status.textContent = "● Connected";
            message.textContent = "You are connected. Start speaking!";
            startButton.disabled = true;
            endButton.disabled = false;
        },

        onDisconnected: () => {
            status.textContent = "● Ready";
            message.textContent = "Call ended. Click Start Call to try again.";
            startButton.disabled = false;
            endButton.disabled = true;
        },

        onUserTranscript: (data) => {
            if (data.final && data.text) {
                addMessage("You", data.text);
            }
        },

        onBotTranscript: (data) => {
            if (data.text) {
                addMessage("Assistant", data.text);
            }
        },

        onTrackStarted: (track, participant) => {
            if (track.kind === "audio" && !participant?.local) {
                const audio = document.createElement("audio");
                audio.autoplay = true;
                audio.srcObject = new MediaStream([track]);
                document.body.appendChild(audio);
            }
        },
    },
});

startButton.addEventListener("click", async () => {
    try {
        status.textContent = "● Connecting...";
        message.textContent = "Please allow microphone access.";
        startButton.disabled = true;

        await client.initDevices();

        await client.startBotAndConnect({
            endpoint: "http://localhost:7860/start",
            requestData: {
                transport: "webrtc",
                enableDefaultIceServers: true,
            },
        });

    } catch (error) {
        console.error("Connection error:", error);
        status.textContent = "● Connection failed";
        message.textContent = "Could not connect. Check the Python backend.";
        startButton.disabled = false;
    }
});

endButton.addEventListener("click", async () => {
    await client.disconnect();
});

async function loadAppointments() {
    const container = document.getElementById("appointments");

    try {
        const response = await fetch(
            "http://localhost:8000/api/appointments"
        );

        if (!response.ok) {
            throw new Error("Failed to load appointments");
        }

        const appointments = await response.json();
        container.innerHTML = "";

        if (appointments.length === 0) {
            container.textContent = "No appointments yet.";
            return;
        }

        appointments.forEach((appointment) => {
            const card = document.createElement("div");
            card.className = "doctor";

            const details = [
                `Appointment #${appointment.id}`,
                `Patient: ${appointment.patient_name || "Patient"}`,
                `Doctor: ${appointment.doctor_name || "Unknown"}`,
                `Specialty: ${appointment.specialty || "N/A"}`,
                `Time: ${appointment.slot_time || "N/A"}`,
                `Status: ${appointment.status}`
            ];

            card.textContent = details.join(" | ");
            container.appendChild(card);
        });

    } catch (error) {
        console.error("Appointment loading error:", error);
        container.textContent = "Could not load appointments.";
    }
}

loadAppointments();
setInterval(loadAppointments, 3000);

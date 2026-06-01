# Jaylogic Chrome Extension

Chrome extension that streams Google Meet tab video frames to a deployed diarization WebSocket endpoint and displays live speaker-labeled words.

## Backend contract

This extension targets the WebSocket URL entered in the popup, for example:

- `wss://your-diarization-host.example/ws`

Outgoing frame payload:

```json
{"ts_ms": 1234.5, "frame": "<base64 jpeg>"}
```

Incoming backend messages:

```json
{"event": "init", "speakers": ["person_1", "person_2"]}
{"speaker": "person_1", "word": "hello", "start_ms": 1200, "end_ms": 1400}
```

The extension relays these messages to any open Recognize web app tab through `page-bridge.js`.
The Vercel page receives them with `window.postMessage`; the page does not host a WebSocket server.

## Install

1. Open `chrome://extensions`
2. Enable **Developer mode**
3. Click **Load unpacked**
4. Select the folder:
   - `/Users/senpai/Desktop/Projects/RecognizeAI/recognize/jaylogic/extension`

## Run

1. Open your Google Meet tab.
2. Click the extension icon.
3. Enter your deployed diarization WebSocket URL.
4. Click **Start**.
5. Watch transcript lines stream in popup.

## Notes

- Capture runs from an offscreen document using `tabCapture`.
- Frames are sent at 12 FPS as JPEG.
- If backend is unreachable, popup status shows an error.

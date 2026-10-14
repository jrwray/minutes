# Minutes

A local meeting transcriber. Drop in a recording and get back a timestamped transcript with speaker names, a summary of the meeting, and neatly named files. Transcription and speaker detection run entirely on your machine, with no upload sites and no command-line juggling.

```
meeting.mp4 → transcript (Whisper) → speakers (pyannote) → summary (Ollama or Claude) → named folder
```

## Features

- **Drag-and-drop web UI** on `localhost`, with a queue, live progress and time-remaining estimates, plus a live preview of the text as it's transcribed
- **Accurate transcription** with [faster-whisper](https://github.com/SYSTRAN/faster-whisper) `large-v3-turbo` (int8, CPU-friendly). It skips silence and takes a custom vocabulary for names and jargon
- **Speaker detection** with [pyannote](https://github.com/pyannote/pyannote-audio). Rename "Speaker 1" to a real name and the transcript, summary and files all update
- **Meeting summary** with an overview, decisions, action items (owner and due date), open questions and clickable topic timestamps
  - **Ollama** (fully local) or **Claude** (Anthropic API), switchable per meeting
- **Sensible file names**, such as `2026-10-14_Q4-Budget-Review/`, using the recording date plus an AI-generated title. You can edit the name in the UI and the folder and every file are renamed to match
- Outputs `_transcript.txt`, `.srt` subtitles, `_summary.md`, full `.json`, and an optional 16 kHz WAV
- **Delete** a meeting from the UI, which moves its folder to the Recycle Bin so it can be restored
- Light and dark themes, keyboard friendly

## Setup (Windows)

1. Install [Python](https://www.python.org/downloads/) 3.11+ and then [uv](https://docs.astral.sh/uv/): `pip install uv`
2. Clone this repo and run `uv sync` inside it. This installs everything, ffmpeg included, so you don't need a separate install.
3. Double-click **`Start.bat`**. The app opens in your browser at http://127.0.0.1:7860

The Whisper model (~1.6 GB) downloads automatically on first use, and after that transcription works offline.

### Optional: speaker detection

1. Create a free [Hugging Face](https://huggingface.co) account
2. Accept the terms on [pyannote/speaker-diarization-3.1](https://huggingface.co/pyannote/speaker-diarization-3.1) and [pyannote/segmentation-3.0](https://huggingface.co/pyannote/segmentation-3.0)
3. Create a read token at <https://huggingface.co/settings/tokens> and paste it into **Settings → Speakers**

### Optional: summaries

- **Local:** install [Ollama](https://ollama.com/download), then `ollama pull qwen2.5:7b`. Any chat model you have pulled can be picked in Settings.
- **Claude:** paste an [Anthropic API key](https://console.anthropic.com/) into **Settings → Summary**. Only the transcript text is sent to Anthropic, never the audio. If your key isn't scoped to a workspace, also fill in **Workspace ID**.

Keys are stored only in `data/settings.json`, which git ignores.

## Performance

These timings were measured on CPU only (Ryzen 7 7730U, a laptop chip, no GPU), and the 1-hour column is extrapolated from them.

| Step | 9-min recording (measured) | 1-hour meeting (est.) |
| --- | --- | --- |
| Transcribe (`large-v3-turbo` int8) | 4 min | ~28 min |
| Speakers (pyannote 3.1) | 7.5 min | ~50 min |
| Summary (Ollama `qwen2.5:7b`) | 3 min | ~10–15 min |
| Summary (Claude) | not measured | typically under a minute |

Speaker detection is the slow step on CPU. Turn it off in Settings when you only need the text. GPU acceleration isn't wired up yet.

## Project layout

```
minutes/
  transcribe.py   faster-whisper wrapper
  diarize.py      pyannote + word-level speaker alignment
  summarize.py    Ollama / Claude summaries (structured JSON)
  export.py       naming, .txt/.srt/.md/.json writers
  jobs.py         single-worker queue
  server.py       FastAPI routes
static/           UI (vanilla HTML/CSS/JS, no build step)
Start.bat         launcher
```

## License

MIT

# AI Video Assistant

I made this project to understand long YouTube videos, meetings, and audio files quickly. Instead of watching a full video, the user can give a YouTube link or a local audio/video file. The project converts the speech into text and gives useful information from it.

## What My Project Does

My AI Video Assistant can:

- Download audio from a YouTube video or use a local audio/video file.
- Convert the audio into small chunks.
- Transcribe the spoken audio into text using Groq Whisper.
- Create a short title and summary of the video or meeting.
- Find action items, important decisions, and open questions.
- Answer questions about the video through a chat feature.

## How It Works

1. The user enters a YouTube link or local file path.
2. The project downloads or converts the audio into WAV format.
3. It splits long audio into smaller parts so it can be processed easily.
4. Groq Whisper changes the audio into a text transcript.
5. Groq LLM reads the transcript and creates the title, summary, action items, decisions, and questions.
6. The transcript is saved as embeddings in ChromaDB.
7. When the user asks a question, the project finds the relevant transcript parts and answers from them.

## What I Used

- Python
- Streamlit for the web interface
- Groq API for transcription and AI responses
- Whisper for speech-to-text
- LangChain for connecting the AI steps
- ChromaDB for saving and searching transcript information
- Hugging Face embeddings for semantic search
- yt-dlp, pydub, and FFmpeg for downloading and processing audio

## Files in the Project

```text
app.py                    Streamlit web application
main.py                   Command-line application
utils/audio_processor.py  Downloads, converts, and chunks audio
core/transcriber.py       Changes audio into text
core/summarizer.py        Creates the title and summary
core/extractor.py         Finds action items, decisions, and questions
core/vector_store.py      Saves transcript embeddings in ChromaDB
core/rag_engine.py        Lets the user ask questions about the video
```

## How to Run It

1. Create and activate a virtual environment.

```bash
python -m venv venv
venv\Scripts\activate
```

2. Install the required packages.

```bash
pip install -r Requirements.txt
```

3. Install FFmpeg and make sure it is available in your system PATH.

4. Create a `.env` file and add your Groq API key.

```env
GROQ_API_KEY=your_groq_api_key
```

5. Start the web application.

```bash
streamlit run app.py
```

You can also run the terminal version:

```bash
python main.py
```

## What I Did

I built the complete workflow for processing a video or audio file. I connected audio downloading, audio conversion, transcription, summarization, information extraction, and question answering in one project. I also created a Streamlit interface so the project is easy to use, and added a command-line version for testing.

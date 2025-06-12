# 🎵 YouTube Playlist Transcriber

[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![Docker](https://img.shields.io/badge/Docker-Ready-brightgreen.svg)](https://www.docker.com/)
[![OpenAI](https://img.shields.io/badge/OpenAI-Whisper-orange.svg)](https://openai.com/research/whisper)

Transform YouTube playlists and videos into text transcripts using OpenAI's Whisper AI! 🚀

## ✨ Features

- 🎬 **Playlist & Video Support** - Works with YouTube playlists and individual videos
- 🤖 **AI Transcription** - Uses OpenAI Whisper for accurate speech-to-text
- 🐳 **Docker Ready** - Containerized for easy deployment
- 🔄 **Smart Resume** - Skips already processed content
- ⚡ **Rate Limit Handling** - Intelligent retry logic
- 📊 **Progress Tracking** - Real-time progress indicators

## 🚀 Quick Start

### 1. Build Docker Image
```bash
git clone https://github.com/haldahini/YoutubeTranscriber.git
cd YoutubeTranscriber
docker build -t yt-transcriber .
```

### 2. Run Transcriber
```bash
docker run --rm \
  -v "$(pwd)/transcriptions:/app/transcriptions" \
  -v "$(pwd)/downloads:/app/downloads" \
  yt-transcriber \
  --url "https://www.youtube.com/playlist?list=YOUR_PLAYLIST_ID" \
  --api-key "sk-your-openai-api-key"
```

## 🛠️ Options

| Option | Description | Default | Required |
|--------|-------------|---------|----------|
| `--url` | YouTube playlist or video URL | - | ✅ |
| `--api-key` | OpenAI API key | - | ✅ |
| `--output` | Folder for transcripts | `transcriptions` | ❌ |
| `--delay` | Delay between API calls (seconds) | `5` | ❌ |

## 📁 Project Structure

```
YoutubeTranscriber/
├── README.md
├── Dockerfile
├── requirements.txt
├── youtube_playlist_to_text.py
├── downloads/          # Audio files (auto-created)
└── transcriptions/     # Text transcripts (auto-created)
```

## 💡 How It Works

1. **🔍 Discovery** - Analyzes YouTube URL to extract video list
2. **⬇️ Download** - Downloads audio using yt-dlp
3. **🧠 Transcribe** - Sends audio to OpenAI Whisper API
4. **💾 Save** - Stores text transcripts in organized files
5. **🔄 Resume** - Skips already processed content

## 🤖 AI-Powered Development

**This project was essentially built with the assistance of AI:**
- **Claude 4 Sonnet** - Core script development, Docker containerization, and error handling
- **ChatGPT** - Additional optimization and debugging support
- **This README** - Also crafted with Claude 4 Sonnet

## ⚠️ Important Notes

- **Costs**: OpenAI Whisper charges $0.006 per minute of audio
- **Limits**: 25MB max file size per audio file
- **Storage**: Audio files preserved for re-processing
- **API Key**: Get yours at [OpenAI Platform](https://platform.openai.com/api-keys)

## 🤝 Contributing

Contributions welcome! Please open an issue for major changes.

## 📝 License

MIT License - see [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [yt-dlp](https://github.com/yt-dlp/yt-dlp) - YouTube downloader
- [OpenAI Whisper](https://openai.com/research/whisper) - Speech recognition
- [FFmpeg](https://ffmpeg.org/) - Media processing
- **Claude 4 Sonnet & ChatGPT** - AI assistance in development and documentation

---

⭐ **Star this repo if it helped you!** ⭐
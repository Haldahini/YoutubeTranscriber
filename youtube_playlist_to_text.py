import argparse
import json
import subprocess
from pathlib import Path
from openai import OpenAI
from openai import RateLimitError
import time
import sys

def print_header():
    """Print a fancy header"""
    print("=" * 60)
    print("🎵 YouTube Playlist to Text Transcriber 🎵")
    print("=" * 60)

def print_section(title):
    """Print a section separator"""
    print(f"\n{'─' * 50}")
    print(f"📋 {title}")
    print('─' * 50)

def get_video_list(url):
    print_section("GETTING VIDEO LIST")
    print("🔍 Analyzing playlist/video...")
    
    try:
        result = subprocess.run([
            "yt-dlp",
            "--flat-playlist",
            "-J",
            url
        ], capture_output=True, check=True, text=True)

        data = json.loads(result.stdout)
        entries = data.get("entries", [])

        if not entries and data.get("id"):
            print("📹 Single video detected")
            return [url]

        video_urls = [f"https://www.youtube.com/watch?v={entry['id']}" for entry in entries]
        print(f"✨ Found {len(video_urls)} video(s) in playlist")
        
        # Show first few video titles for confirmation
        if len(video_urls) > 1:
            print("📝 Preview of videos:")
            for i, entry in enumerate(entries[:3]):
                title = entry.get('title', 'Unknown Title')[:50]
                print(f"   {i+1}. {title}...")
            if len(entries) > 3:
                print(f"   ... and {len(entries) - 3} more videos")
        
        return video_urls
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Error getting video list: {e}")
        sys.exit(1)

def check_file_size(file_path, max_size_mb=25):
    """Check if file is under OpenAI's limit with fancy output"""
    size_mb = file_path.stat().st_size / (1024 * 1024)
    
    if size_mb > max_size_mb:
        print(f"⚠️  File too large: {file_path.name} ({size_mb:.1f}MB > {max_size_mb}MB limit)")
        return False
    else:
        print(f"📏 File size OK: {size_mb:.1f}MB")
        return True

def download_audio_if_needed(url, output_path):
    """Download audio with improved feedback"""
    # List all mp3s before
    before_files = set(output_path.glob("*.mp3"))

    print(f"🎧 Downloading audio...")
    print(f"🔗 URL: {url}")
    
    cmd = [
        "yt-dlp",
        "-f", "bestaudio",
        "--extract-audio",
        "--audio-format", "mp3",
        "--output", str(output_path / "%(title)s.%(ext)s"),
        "--restrict-filenames",  # normalize filenames
        "--no-warnings",  # reduce noise
        url
    ]
    
    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        
        # Detect the new file
        after_files = set(output_path.glob("*.mp3"))
        new_files = after_files - before_files
        
        if new_files:
            new_file = new_files.pop()
            print(f"✅ Downloaded: {new_file.name}")
            check_file_size(new_file)
            return new_file
        else:
            print("⚠️  No new audio file detected")
            return None
            
    except subprocess.CalledProcessError as e:
        print(f"❌ Download failed: {e}")
        return None

def transcribe_audio(file_path, client, max_retries=3):
    """Transcribe audio with fancy retry logic"""
    print(f"🧠 Transcribing: {file_path.name}")
    
    for attempt in range(max_retries):
        try:
            with open(file_path, "rb") as audio_file:
                print("🔄 Sending to OpenAI Whisper...")
                transcript = client.audio.transcriptions.create(
                    model="whisper-1",
                    file=audio_file
                )
            
            word_count = len(transcript.text.split())
            print(f"📊 Transcription complete: {word_count} words")
            return transcript.text
            
        except RateLimitError as e:
            if "insufficient_quota" in str(e).lower():
                print("💳 Insufficient quota - please add credits to your OpenAI account")
                print("🔗 Visit: https://platform.openai.com/account/billing")
                return None
            else:
                wait_time = (attempt + 1) * 60
                print(f"⏳ Rate limit hit - waiting {wait_time}s (attempt {attempt + 1}/{max_retries})")
                if attempt < max_retries - 1:
                    time.sleep(wait_time)
                    continue
                else:
                    print("❌ Max retries reached for rate limiting")
                    return None
                    
        except Exception as e:
            print(f"❌ Transcription error: {str(e)}")
            if attempt < max_retries - 1:
                print(f"🔄 Retrying in 5 seconds... (attempt {attempt + 2}/{max_retries})")
                time.sleep(5)
                continue
            else:
                print("❌ Max retries reached")
                return None
    
    return None

def main():
    print_header()
    
    parser = argparse.ArgumentParser(
        description="🎵 Transcribe YouTube playlists/videos using OpenAI Whisper API",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --url "https://youtube.com/playlist?list=..." --api-key "sk-..."
  %(prog)s --url "https://youtube.com/watch?v=..." --api-key "sk-..." --delay 10
        """
    )
    parser.add_argument("--url", required=True, help="YouTube playlist or video URL")
    parser.add_argument("--api-key", required=True, help="OpenAI API key")
    parser.add_argument("--output", default="transcriptions", help="Folder to store transcripts (default: transcriptions)")
    parser.add_argument("--delay", type=int, default=5, help="Delay between transcriptions in seconds (default: 5)")

    args = parser.parse_args()

    # Setup paths
    downloads_path = Path("downloads")
    transcripts_path = Path(args.output)
    downloads_path.mkdir(exist_ok=True)
    transcripts_path.mkdir(exist_ok=True)

    print(f"📁 Downloads folder: {downloads_path.absolute()}")
    print(f"📁 Transcripts folder: {transcripts_path.absolute()}")

    # Initialize OpenAI client
    try:
        client = OpenAI(api_key=args.api_key)
        print("🔑 OpenAI client initialized")
    except Exception as e:
        print(f"❌ Failed to initialize OpenAI client: {e}")
        sys.exit(1)

    # Get video list
    video_urls = get_video_list(args.url)

    # Download phase
    print_section("DOWNLOADING AUDIO FILES")
    downloaded_files = []
    
    for i, url in enumerate(video_urls, 1):
        print(f"\n🎬 Processing video {i}/{len(video_urls)}")
        
        # Check if already downloaded
        before_files = set(downloads_path.glob("*.mp3"))
        mp3_file = download_audio_if_needed(url, downloads_path)
        
        if mp3_file:
            downloaded_files.append(mp3_file)
        else:
            # Check if file already existed
            after_files = set(downloads_path.glob("*.mp3"))
            if before_files == after_files:
                print("⏭️  Possibly already downloaded or failed")

    print(f"\n📊 Download Summary: {len(downloaded_files)} new files downloaded")

    # Transcription phase
    print_section("TRANSCRIBING AUDIO FILES")
    all_mp3_files = sorted(downloads_path.glob("*.mp3"))
    transcribed_count = 0
    skipped_count = 0

    for i, mp3_file in enumerate(all_mp3_files, 1):
        print(f"\n🎵 Processing audio {i}/{len(all_mp3_files)}: {mp3_file.name}")
        
        transcript_file = transcripts_path / f"{mp3_file.stem}.txt"
        
        if transcript_file.exists():
            print(f"📄 Transcript already exists: {transcript_file.name}")
            skipped_count += 1
            continue

        text = transcribe_audio(mp3_file, client)
        
        if text:
            transcript_file.write_text(text, encoding="utf-8")
            print(f"💾 Saved transcript: {transcript_file.name}")
            transcribed_count += 1
            
            # Add delay between requests
            if i < len(all_mp3_files):
                print(f"⏱️  Waiting {args.delay} seconds before next transcription...")
                time.sleep(args.delay)
        else:
            print(f"⚠️  Skipped transcription for: {mp3_file.name}")
            skipped_count += 1

    # Final summary
    print_section("COMPLETION SUMMARY")
    print(f"🎯 Total audio files: {len(all_mp3_files)}")
    print(f"✅ Successfully transcribed: {transcribed_count}")
    print(f"⏭️  Skipped (already existed): {skipped_count}")
    print(f"❌ Failed: {len(all_mp3_files) - transcribed_count - skipped_count}")
    print(f"📁 Transcripts saved to: {transcripts_path.absolute()}")
    print("\n🎉 All done! Happy reading! 📚")

if __name__ == "__main__":
    main()
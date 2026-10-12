"""Repeat the processing without putting temporary media URLs in source."""
import argparse
import json
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
VIDEO_URL = 'https://kinescope.io/eHTc1UJ83wrTzEZL2kxKWz'
REFERER = 'https://dzen.guru/video-claudecode'


def run(args):
    subprocess.run(args, check=True, cwd=ROOT)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--transcriber', type=Path, default=Path.home() / '.codex/skills/gigaam-transcribe/scripts/transcribe.py')
    parser.add_argument('--skip-download', action='store_true')
    args = parser.parse_args()
    for program in ['yt-dlp', 'ffmpeg', 'ffprobe']:
        if not shutil.which(program):
            raise RuntimeError(f'{program} is missing from PATH')
    if not args.transcriber.is_file():
        raise RuntimeError(f'GigaAM transcriber not found: {args.transcriber}')
    for folder in ['data/media', 'data/transcript', 'data/source']:
        (ROOT / folder).mkdir(parents=True, exist_ok=True)
    if not args.skip_download:
        if shutil.disk_usage(ROOT).free < 1_500_000_000:
            raise RuntimeError('At least 1.5 billion free bytes required')
        run(['yt-dlp', '--no-progress', '-f', 'bestvideo[height<=480]+bestaudio/best[height<=480]',
             '--merge-output-format', 'mp4', '--referer', REFERER,
             '-o', 'data/media/lesson.%(ext)s', VIDEO_URL])
    media = ROOT / 'data/media/lesson.mp4'
    if not media.is_file():
        raise RuntimeError('Video file is missing')
    run(['ffmpeg', '-hide_banner', '-loglevel', 'error', '-y', '-i', str(media),
         '-vn', '-ac', '1', '-ar', '16000', '-c:a', 'flac', 'data/media/lesson.flac'])
    run([sys.executable, str(args.transcriber), 'data/media/lesson.flac', '--out-dir', 'data/transcript'])
    run([sys.executable, 'scripts/build.py'])


if __name__ == '__main__':
    main()

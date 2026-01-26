#!/usr/bin/env python3
"""
Record proof engine runs as shareable content.
Creates terminal recordings and GIFs for Twitter/social.
"""

import os
import subprocess
import sys
import json
from datetime import datetime
from pathlib import Path

BASE_DIR = Path(__file__).parent
RECORDINGS_DIR = BASE_DIR / "recordings"
RECORDINGS_DIR.mkdir(exist_ok=True)


def check_tools():
    """Check what recording tools are available."""
    tools = {}

    # Check asciinema
    result = subprocess.run(["which", "asciinema"], capture_output=True)
    tools["asciinema"] = result.returncode == 0

    # Check ffmpeg
    result = subprocess.run(["which", "ffmpeg"], capture_output=True)
    tools["ffmpeg"] = result.returncode == 0

    # Check script (built into macOS)
    result = subprocess.run(["which", "script"], capture_output=True)
    tools["script"] = result.returncode == 0

    return tools


def record_with_asciinema(command: str, title: str = "BST Probe") -> dict:
    """Record terminal session with asciinema."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"probe_{timestamp}.cast"
    filepath = RECORDINGS_DIR / filename

    print(f"Recording to {filepath}...")
    print("=" * 60)

    # Run asciinema
    result = subprocess.run(
        ["asciinema", "rec", "-t", title, "-c", command, str(filepath)],
        cwd=BASE_DIR,
    )

    if filepath.exists():
        print(f"\nRecording saved: {filepath}")
        print(f"\nTo upload and share:")
        print(f"  asciinema upload {filepath}")
        print(f"\nTo play locally:")
        print(f"  asciinema play {filepath}")

        return {
            "success": True,
            "file": str(filepath),
            "upload_cmd": f"asciinema upload {filepath}",
        }

    return {"success": False, "error": "Recording failed"}


def record_with_script(command: str) -> dict:
    """Fallback: record with built-in script command."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"probe_{timestamp}.txt"
    filepath = RECORDINGS_DIR / filename

    print(f"Recording to {filepath}...")
    print("=" * 60)

    # Use script to capture output
    result = subprocess.run(
        ["script", "-q", str(filepath), "bash", "-c", command],
        cwd=BASE_DIR,
    )

    if filepath.exists():
        print(f"\nTranscript saved: {filepath}")
        return {
            "success": True,
            "file": str(filepath),
            "type": "text",
        }

    return {"success": False, "error": "Recording failed"}


def record_probe(model: str = "claude", question: int = 14):
    """Record a specific probe question."""
    command = f"python3 proof_engine.py single {model} {question}"

    tools = check_tools()

    if tools.get("asciinema"):
        return record_with_asciinema(command, f"BST Q{question} - {model}")
    elif tools.get("script"):
        return record_with_script(command)
    else:
        print("No recording tools available.")
        print("Install asciinema: brew install asciinema")
        return {"success": False, "error": "No tools"}


def record_all_models():
    """Record Q14 across all models - the money shot."""
    command = "python3 proof_engine.py all 14"
    title = "5 AIs Read Their Own Autopsy"

    tools = check_tools()

    if tools.get("asciinema"):
        return record_with_asciinema(command, title)
    else:
        return record_with_script(command)


def record_personalized(username: str, statement: str):
    """Record a personalized probe."""
    # Escape quotes in statement
    safe_statement = statement.replace('"', '\\"')
    command = f'python3 probe_personalizer.py {username} "{safe_statement}"'

    tools = check_tools()

    if tools.get("asciinema"):
        return record_with_asciinema(command, f"BST Probe: @{username}")
    else:
        return record_with_script(command)


def create_gif_from_cast(cast_file: str, output: str = None):
    """Convert asciinema cast to GIF using agg."""
    if output is None:
        output = cast_file.replace(".cast", ".gif")

    # Check if agg is installed
    result = subprocess.run(["which", "agg"], capture_output=True)
    if result.returncode != 0:
        print("agg not found. Install with: cargo install agg")
        print("Or use: https://github.com/asciinema/agg")
        return None

    subprocess.run(["agg", cast_file, output])
    print(f"GIF created: {output}")
    return output


def upload_to_asciinema(cast_file: str) -> str:
    """Upload recording to asciinema.org and return URL."""
    result = subprocess.run(
        ["asciinema", "upload", cast_file],
        capture_output=True,
        text=True,
    )

    if result.returncode == 0:
        # Parse URL from output
        for line in result.stdout.split("\n"):
            if "asciinema.org" in line:
                return line.strip()

    return None


if __name__ == "__main__":
    tools = check_tools()
    print("Available recording tools:")
    for tool, available in tools.items():
        status = "YES" if available else "NO"
        print(f"  {tool}: {status}")

    if len(sys.argv) < 2:
        print("\nUsage:")
        print("  python video_recorder.py probe claude 14  # Record single probe")
        print("  python video_recorder.py all              # Record all models Q14")
        print("  python video_recorder.py personal @user 'statement'")
        print("  python video_recorder.py gif file.cast    # Convert to GIF")
        sys.exit(0)

    cmd = sys.argv[1]

    if cmd == "probe":
        model = sys.argv[2] if len(sys.argv) > 2 else "claude"
        q = int(sys.argv[3]) if len(sys.argv) > 3 else 14
        record_probe(model, q)

    elif cmd == "all":
        record_all_models()

    elif cmd == "personal":
        username = sys.argv[2].lstrip("@")
        statement = " ".join(sys.argv[3:])
        record_personalized(username, statement)

    elif cmd == "gif":
        create_gif_from_cast(sys.argv[2])

    elif cmd == "upload":
        url = upload_to_asciinema(sys.argv[2])
        if url:
            print(f"Uploaded: {url}")

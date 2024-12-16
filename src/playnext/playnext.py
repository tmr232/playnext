import os
import re
import subprocess
from pathlib import Path

import typer
import tkinter.messagebox

VLC_PATH = r"C:\Program Files\VideoLAN\VLC\vlc.exe"

app = typer.Typer()


def find_episode(episode_root: Path, episode_number: int, bookmark_pattern: re.Pattern) -> Path | None:
    for root, _, files in os.walk(episode_root):
        for file in files:
            if (match := bookmark_pattern.search(file)):
                if int(match.group(1)) == episode_number:
                    return Path(root) / file


def play_episode(episode_path: Path):
    subprocess.check_call(
        [VLC_PATH, "--fullscreen", str(episode_path), "vlc://quit"]
    )


@app.command()
def main(bookmark_path: Path):
    bookmark_pattern = re.compile(bookmark_path.read_text())
    episode_number = int(bookmark_path.with_suffix("").name)
    episode = find_episode(bookmark_path.parent, episode_number, bookmark_pattern)
    if episode is None:
        tkinter.messagebox.showerror("Playnext", "Failed to find episode.")
        raise typer.Exit(-1)

    try:
        play_episode(episode)
    except subprocess.CalledProcessError:
        tkinter.messagebox.showerror("Playnext", f"Failed to play episode: {episode}")
        raise typer.Exit(-1)

    advance_episode = tkinter.messagebox.askyesno("Playnext", "Advance episode?")
    if advance_episode:
        bookmark_path.rename(bookmark_path.with_name(str(episode_number + 1)).with_suffix(bookmark_path.suffix))

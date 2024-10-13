from pathlib import Path
from typing import Annotated

from pydub import AudioSegment
from rich.console import Console
from typer import Argument, Option, Typer

app = Typer()
console = Console()
path_arg = Annotated[Path, Argument()]


def _extract_audio(video_file: str, output_file: str) -> Path:
    """Extract audio from vídeo.

    Args:
        video_file: Video to extract audio
        output_file:

    Returns:
        A audio Path
    """
    audio: AudioSegment = AudioSegment.from_file(video_file)
    audio.export(output_file, format='wav')

    return Path(output_file)


@app.command()
def extract_audio(
    video_file: path_arg,
    output_file: Path = Argument(default='output.wav'),
):
    """Extracts the audio from a video."""
    console.print(_extract_audio(str(video_file), str(output_file)))

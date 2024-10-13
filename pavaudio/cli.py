from enum import Enum
from pathlib import Path
from typing import Annotated

from pydub import AudioSegment
from pydub import silence
from rich.console import Console
from typer import Argument, Option, Typer

app = Typer()
console = Console()
path_arg = Annotated[Path, Argument()]


class Distance(str, Enum):
    negative = 'negative'
    tiny = 'tiny'
    small = 'small'
    medium = 'medium'
    large = 'large'
    huge = 'huge'


silence_option = Option(
    400,
    '--silence-time',
    '-s',
    help='Minimal time in ms for configure a silence',
)

threshold_option = Option(
    -65,
    '--threshold',
    '-t',
    help='Value in db for detect silence',
)

distance_option = Option(
    Distance.tiny,
    '--distance',
    '-d',
    help='Distance betweet silences',
)


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


def _cut_silences(
    audio_file: str,
    output_file: str,
    silence_time: int = 400,
    threshold: int = -65,
) -> Path:
    audio = AudioSegment.from_file(audio_file)

    silences = silence.split_on_silence(
        audio,
        min_silence_len=silence_time,
        silence_thresh=threshold,
    )

    combined = AudioSegment.empty()
    for chunk in silences:
        combined += chunk

    combined.export(output_file, format='mp3')

    return Path(output_file)


@app.command()
def extract_audio(
    video_file: path_arg,
    output_file: Path = Argument(default='output.wav'),
):
    """Extracts the audio from a video."""
    console.print(_extract_audio(str(video_file), str(output_file)))


@app.command()
def cut_silences(
    audio_file: path_arg,
    output_file: path_arg,
    silence_time: int = silence_option,
    threshold: int = threshold_option,
):
    """Removes all silences from an audio file."""
    console.print(
        _cut_silences(
            str(audio_file),
            str(output_file),
            silence_time=silence_time,
            threshold=threshold,
        ),
    )

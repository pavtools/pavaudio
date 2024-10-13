from enum import Enum
from json import load
from pathlib import Path
from typing import Annotated

from appdirs import AppDirs
from pydub import AudioSegment
from pydub import silence
from rich.console import Console
from typer import Argument, Option, Typer
from pedalboard import Pedalboard, load_plugin
from pedalboard.io import AudioFile

app = Typer()
console = Console()
dirs = AppDirs('sigchain', 'pavtools')
path_arg = Annotated[Path, Argument()]
config_path = Path(dirs.user_config_dir)


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


@app.command()
def audio_processing(input_file: str, output_file: str):
    """Apply vst effects on audio."""
    # read plugins configuration
    with open(config_path / 'config.json', 'r') as config_file:
        config_data = load(config_file)

    chain = [
        load_plugin(plugin, parameter_values=config_data['plugins'][plugin])
        for plugin in config_data['plugin_chain']
    ]

    board = Pedalboard(chain)

    with AudioFile(input_file) as f:
        with AudioFile(output_file, 'w', f.samplerate, f.num_channels) as o:
            while f.tell() < f.frames:
                chunk = f.read(f.samplerate)
                effected = board(chunk, f.samplerate, reset=False)
                o.write(effected)

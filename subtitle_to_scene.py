import argparse
import csv
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Tuple

from timecode import Timecode


@dataclass
class Subtitle:
    begin: Timecode
    end: Timecode
    text: str


def parse_line(line: str) -> Subtitle:
    match = re.match(
        (
            r".*begin='(?P<begin>[0-9:]+)'"
            r".*end='(?P<end>[0-9:]+)'"
            r".*>(?P<subtitle>[^<]+)(</span>)?</p>"
        ),
        line,
    )
    if not match:
        raise ValueError(f"Could not parse line:\n{line}")
    return Subtitle(
        Timecode(30, match.group("begin")),
        Timecode(30, match.group("end")),
        match.group("subtitle"),
    )


EPISODE_TO_OFFSET: Dict[int, Tuple[int, Timecode]] = {
    1: (-1, Timecode(30, "00:00:03.500")),
    2: (+1, Timecode(30, "00:00:17.284") - Timecode(30, "00:00:14:03")),
    3: (+1, Timecode(30, "00:00:19.153") - Timecode(30, "00:00:09:01")),
    4: (+1, Timecode(30, "00:00:13.981") - Timecode(30, "00:00:13:21")),
    5: (+1, Timecode(30, "00:00:08.876") - Timecode(30, "00:00:08:18")),
    6: (+1, Timecode(30, "00:00:07.041") - Timecode(30, "00:00:06:21")),
}


def sync_with_video(subtitle: Subtitle, episode_number: int) -> Subtitle:
    (operation, offset) = EPISODE_TO_OFFSET[episode_number]
    if operation == -1:
        subtitle.begin -= offset
        subtitle.end -= offset
    else:
        subtitle.begin += offset
        subtitle.end += offset
    return subtitle


def get_all_subtitles() -> List[Subtitle]:
    episode_number = int(Path.cwd().name[0])
    subtitles_xml = Path("./subtitles.txt")
    subtitles: List[Subtitle] = []
    for line in subtitles_xml.read_bytes().splitlines():
        if not line.strip():
            continue
        subtitle = parse_line(line.decode())
        subtitle = sync_with_video(subtitle, episode_number)
        subtitles.append(subtitle)
    return subtitles


def get_timecode_range(scene: int) -> Tuple[Timecode, Timecode]:
    if scene == 0:
        raise ValueError("scenes are one-indexed")
    scenes_csv = Path("./scenes.csv")
    # The first line has all we need: the timecode list.
    timecodes = scenes_csv.read_text().splitlines()[0][len("Timecode List:,") :]
    timecode_list = ["00:00:00.000"] + timecodes.split(",")
    try:
        return (
            Timecode(30, timecode_list[scene - 1]),
            Timecode(30, timecode_list[scene]),
        )
    except IndexError:
        raise IndexError(f"the last valid scene is {len(timecode_list) - 1}") from None


def get_subtitle_for_scene(scene: int) -> str:
    (begin_scene, end_scene) = get_timecode_range(scene)
    # Introduce tolerance on either side, in frames:
    begin_limit = begin_scene - 30
    end_limit = end_scene + 30

    subtitles = get_all_subtitles()

    scene_subtitles: List[str] = []
    prev_subtitle = None
    for subtitle in subtitles:
        if (
            (subtitle.end > (begin_scene + 60) and subtitle.end < end_scene)
            or (subtitle.begin > begin_limit and subtitle.end < end_limit)
            or (subtitle.begin < (end_scene - 60) and subtitle.end > end_scene)
        ):
            if prev_subtitle and prev_subtitle.begin == subtitle.begin:
                scene_subtitles[-1] += " " + subtitle.text
            else:
                scene_subtitles.append(subtitle.text)
                prev_subtitle = subtitle

    return "\n".join(scene_subtitles)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("scene", type=int)
    args = parser.parse_args()
    print(get_subtitle_for_scene(args.scene))


if __name__ == "__main__":
    main()

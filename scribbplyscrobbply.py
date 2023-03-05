"""
scribbplyscrobbply
==================

a pure python script to process your spotify extended streaming history jsons into a
single last.fm scrubbler-friendly json file.

exit codes
    0
        success
    1
        invalid argument
    2X (X being the files positional index; e.g. 1st -> 10; 11th -> 110)
        file does not exist
    3X (X being the files positional index; see 1X)
        error when reading file
    4
        error during processing data
    -1
        unknown error

-----------------------------------------------------------------------------------------

This is free and unencumbered software released into the public domain.

Anyone is free to copy, modify, publish, use, compile, sell, or distribute this software,
either in source code form or as a compiled binary, for any purpose, commercial or
non-commercial, and by any means.

In jurisdictions that recognize copyright laws, the author or authors of this software
dedicate any and all copyright interest in the software to the public domain. We make
this dedication for the benefit of the public at large and to the detriment of our heirs
and successors. We intend this dedication to be an overt act of relinquishment in
perpetuity of all present and future rights to this software under copyright law.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED,
INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR
PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS BE LIABLE FOR ANY CLAIM,
DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

For more information, please refer to <http://unlicense.org/>
"""

from argparse import ArgumentParser
from bisect import insort_left as insort
from dataclasses import dataclass, field
from datetime import date, datetime, timedelta
from enum import Enum
from json import dumps, loads
from pathlib import Path
from sys import stderr
from typing import Final, NamedTuple

VERSION: Final[tuple[int, int, int]] = (1, 0, 0)


class TakeoutFormats(Enum):
    JSON_SCRUBBLER_WPF = "scrubblerwpf"


class Behaviour(NamedTuple):
    files: list[Path]
    output: Path | None = None
    db_get: bool = False
    db_start: date | None = None
    db_end: date | None = None
    min_s: int = 30
    output_format: TakeoutFormats = TakeoutFormats.JSON_SCRUBBLER_WPF


class Play(NamedTuple):
    """
    namedtuple representing a song play

    track: str
        track name (e.g., "TOKYO NEON")
    album: str
        album artist (e.g., "Key Ingredient")
    album_artist: str
        album artist (e.g., "Mili")
    time: datime.datetime
        timestamp of play
    duration: int
        duration in ms
    """

    track: str
    album: str | None
    album_artist: str
    time: datetime
    duration: int

    def export(self, format: TakeoutFormats = TakeoutFormats.JSON_SCRUBBLER_WPF) -> str:
        return dumps(
            obj={
                "trackName": self.track,
                "artistName": self.album_artist,
                "albumName": self.album,
                "time": self.time.isoformat() + "Z",
            },
            ensure_ascii=False,
        )


@dataclass
class ScribbplyScrobbply:
    """
    abstraction for handling with spotify extended streaming history endsong_*.json files

    methods
        .takein(self, ...)
        .takeout(self, ...)
    """

    plays: list[Play] = field(default_factory=list)
    db_start: date = datetime.fromtimestamp(0).date()
    db_end: date = datetime.now().date() + timedelta(1)

    def takein(self, endsongs: list[dict]) -> tuple[int, str, int, int]:
        """
        function for taking in (takein) and processing of a list of parsed json files

        endsongs: list[dict]
            a list of parsed json files

        returns tuple of (result code int, error msg str, processed count, failed count)
        non-zero result code is failure
        """
        failed: int = 0

        for endsong in endsongs:
            for entry in endsong:
                # print(entry)
                track: str | None = entry.get("master_metadata_track_name")
                album: str | None = entry.get("master_metadata_album_album_name")
                album_artist: str | None = entry.get("master_metadata_album_artist_name")
                duration: int | None = entry.get("ms_played")
                time: str | None = entry.get("ts")

                conditions: list[bool] = [
                    track is None,
                    # album is None,
                    album_artist is None,
                    duration is None,
                    time is None,
                ]

                if any(conditions):
                    # debug: stderr.write("".join(["_" if c is True else "X" for c in checks]) + f"\t{len(self.plays)} \n")
                    # debug: stderr.write(f"{entry}\n")
                    failed += 1
                    continue

                assert isinstance(track, str)
                # assert isinstance(album, str)
                assert isinstance(album_artist, str)
                assert isinstance(duration, int)
                assert isinstance(time, str)

                try:
                    insort(
                        a=self.plays,
                        x=Play(
                            track=track,
                            album=album,
                            album_artist=album_artist,
                            duration=duration,
                            time=datetime.fromisoformat(time.rstrip("Z")),
                        ),
                        key=lambda s: s.time,
                    )

                except Exception as err:
                    return (4, str(err), 0, 0)

        self.db_start = self.plays[0].time.date()
        self.db_end = self.plays[-1].time.date()

        return (0, "", len(self.plays), failed)

    def takeout(
        self,
        db_start: date | None = None,
        db_end: date | None = None,
        min_s: int = Behaviour([]).min_s,
        format: TakeoutFormats = TakeoutFormats.JSON_SCRUBBLER_WPF,
    ) -> tuple[int, int, str]:
        """
        exports self.plays into a string for writing out to external applications

        db_start: date | None = None
            specify start date boundary/when to start filtering
            (set 'None' to default to first seen timestamp in history)
        db_end: date | None = None
            specify end date boundary/when to stop filtering
            (set 'None' to default to last seen timestamp in history)
        min_s: int = Behaviour([]).min_s
            minimum number of seconds before counting an partially played track as a
            scrobble (defaults to Behaviour([]).min_s)
        format: TakeoutFormats = TakeoutFormats.JSON_SCRUBBLER_WPF
            format

        returns tuple of (exported_count, filtered_count, exported_string)
        """

        export: list[str] = []

        exported: int = 0
        filtered: int = 0

        if db_start is None:
            db_start = self.db_start - timedelta(1)

        if db_end is None:
            db_end = self.db_end + timedelta(1)

        match format:
            case TakeoutFormats.JSON_SCRUBBLER_WPF:
                export.append("[")

                for index, play in enumerate(self.plays, start=1):
                    conditions: list[bool] = [
                        db_start < play.time.date() < db_end,
                        (play.duration > (min_s * 1000)),
                    ]

                    if all(conditions):
                        export.append(
                            play.export(format=format)
                            + ("," if index != len(self.plays) else "")
                        )
                        exported += 1

                    else:
                        # print(play.duration, (min_s * 1000), (play.duration >= (min_s * 1000)))
                        filtered += 1

                export.append("]")

            case _:
                stderr.write(f"error: takeout: unimplemented format {format}\n")

        return (exported, filtered, "".join(export))


def handle_args() -> Behaviour:
    """
    argument parser to Behaviour helper function
    note: this function may exit()
    """
    parser = ArgumentParser(
        description=(
            f"({'.'.join([str(d) for d in VERSION])}) a python script to process your "
            "spotify extended streaming history into a last.fm scrubbler-friendly json "
            "file"
        ),
    )

    default = Behaviour([])

    ioargs = parser.add_argument_group("input/output options")
    ioargs.add_argument("files", nargs="*", help="endsong_*.json files", type=Path)
    ioargs.add_argument(
        "-o",
        "--output",
        type=Path,
        default=default.output,
        help="file to output to (defaults to stdout)",
    )
    ioargs.add_argument(
        "-f",
        "--format",
        type=str,
        default=default.output_format.value,
        choices=[f.value for f in TakeoutFormats],
        help=f"output format (defaults to '{default.output_format.value}')",
    )

    fargs = parser.add_argument_group("filtering options")
    fargs.add_argument(
        "--get-date-boundary",
        action="store_true",
        default=default.db_get,
        help="prints date boundaries to stdout",
    )
    fargs.add_argument(
        "--ds",
        type=str,
        default="",
        help="specify start iso 8601 date boundary/when to start filtering (defaults to first seen timestamp in history)",
    )
    fargs.add_argument(
        "--de",
        type=str,
        default="",
        help="specify end iso 8601 date boundary/when to stop filtering (defaults to last seen timestamp in history)",
    )
    fargs.add_argument(
        "--ms",
        type=int,
        default=default.min_s,
        help=f"minimum number of seconds before counting an partially played track as a scrobble ({default.min_s})",
    )

    args = parser.parse_args()

    files: list[Path] = args.files
    output: Path | None = args.output
    output_format: TakeoutFormats = TakeoutFormats(args.format)

    db_get: bool = args.get_date_boundary

    try:
        db_start: date | None = (
            date.fromisoformat(args.ds) if args.ds != "" else default.db_start
        )
    except Exception as err:
        exit(1)

    try:
        db_end: date | None = (
            date.fromisoformat(args.de) if args.de != "" else default.db_end
        )
    except Exception as err:
        exit(1)

    min_s: int = args.ms

    if len(files) == 0:
        stderr.write("error: specify at least one file\n")
        exit(1)

    for index, file in enumerate(files):
        if not file.exists():
            stderr.write(f"error: {file} does not exist\n")
            exit(int(f"2{index}"))

    return Behaviour(
        files=files,
        output=output,
        output_format=output_format,
        db_get=db_get,
        db_start=db_start,
        db_end=db_end,
        min_s=min_s,
    )


def cli(bev: Behaviour):
    """
    cli entry function
    note: this function may exit()
    """
    endsongs: list[dict] = []

    for index, file in enumerate(bev.files):
        try:
            data = loads(file.read_text(encoding="utf-8"))

        except Exception as err:
            stderr.write(f"error: {file} - '{err}'")
            exit(int(f"3{index}"))

        else:
            endsongs.append(data)

    ss = ScribbplyScrobbply()

    if (ti_result := ss.takein(endsongs=endsongs))[0] != 0:
        stderr.write(f"{ti_result[1]}\n")
        exit(ti_result[0])

    stderr.write(f"note: processed {ti_result[2]} ({ti_result[3]} failed)\n")

    if bev.db_get:
        stderr.write("note: is in format [earliest, latest]\n")
        print(f"['{ss.db_start.isoformat()}', '{ss.db_end.isoformat()}']")
        exit(0)

    exported, filtered, export_string = ss.takeout(
        db_start=bev.db_start,
        db_end=bev.db_end,
        min_s=bev.min_s,
        format=bev.output_format,
    )

    if bev.output is None:
        print(export_string)

    else:
        bev.output.write_text(export_string, encoding="utf-8")

    stderr.write(f"note: takeout: exported {exported} scrobbles (filtered {filtered})\n")

    exit(0)


def main():
    cli(handle_args())


if __name__ == "__main__":
    main()

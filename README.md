# scribbplyscrobbly

> **Note**  
>
> I made scribbplyscrobbply as I thought a) lilnasy's scribblyscrobbly wasn't processing
> all of the entries, and b) I wanted to filter by date without manually editing files.
>
> So I set out to do just that, with a working command-line program. This is where I
> learnt that no, scribblyscrobbly wasnt mysteriously skipping entries, but there was an
> error for extended history data requested in early 2023, resulting in many nulled
> entries.  
> <https://community.spotify.com/t5/Other-Podcasts-Partners-etc/Extended-data-been-sent-to-me-Missing-data-from-October-to/m-p/5514697>
>
> Furthermore, the Flet framework's internal file handling library didn't fully support
> the web, making efforts for a web frontend futile, evaporating the only reason to use
> my tool over lilnasy's as the non-technologically-inclined may not want to use a CLI.  
>
> **I may come back to this project to complete the GUI in the future**, but how long
> indeterminate said future is indeterminate at time of writing, as the file issue is not
> directly Flet's fault.
>
> tl;dr This project was an accident and a semi-failure, and unless you a) **need** date
> filtering and b) are comfortable with the command-line, use lilnasy's scribblyscrobbly.

A pure Python script to process your Spotify Extended Streaming History JSONs into a
single Last.fm Scrubbler-friendly JSON file.

---

Inspired by [lilnasy/scribblyscrobbly](https://github.com/lilnasy/scribblyscrobbly)

- [Usage](#usage)
    - [Command Line](#command-line)
- [Developing](#developing)
    - [Setup](#setup)
    - [Checking and Formatting](#checking-and-formatting)
- [Licence](#licence)

## Usage

<!-- 
### Static Web App

TODO
-->

### Command Line

> **Note**  
> You will need Python 3.10 or later.

1. Install scribbplyscrobbply as a package:

    ```
    pip install git+https://github.com/markjoshwel/scribbplyscrobbply
    ```

2. Get date boundary:

    ```
    $ scribbplyscrobbply path-to-files/endsong_*.json --get-date-boundary
    note: processed 74043 plays (22888 failed)
    note: is in format [earliest, latest]
    ['2021-11-04', '2022-10-14']
    ```

    Change the dates as needed, especially if you want to exclude already scrobbled
    tracks. The date boundaries are **inclusive**. This means if you set the end boundary
    to `2023-01-01`, scrobbles **will** filter out `2023-01-31` and beyond.

3. Generate a JSON:

    ```
    scribbplyscrobbply.py data/endsong_*.json --output export.json
    ```

    If your environment supports pipes:

    ```
    $ scribbplyscrobbply path-to-files/endsong_*.json > export.json
    note: processed 74043 (22888 failed)
    note: takeout: exported 43171 scrobbles (filtered 30872)
    ```

    And voilà!

## Developing

### Setup

1. **Environment Setup**

    You will need [Python](https://www.python.org/) >=3.10 and
    [Poetry](https://github.com/python-poetry/poetry).

    Also consider using [Devbox](https://github.com/jetpack-io/devbox) (which uses
    [Nix](https://nixos.org/)) to easily setup a reproducible development shell.

    ```
    [m@csp scribbplyscrobbply]$ devbox shell
    (scribbplyscrobbply-py3.10) [m@csp scribbplyscrobbply]$ which python
    /home/m/.cache/pypoetry/virtualenvs/scribbplyscrobbply-XkMn02HP-py3.10/bin/python
    (scribbplyscrobbply-py3.10) [m@csp scribbplyscrobbply]$ which poetry
    /nix/store/rad8y09y2dnn03igf053zwk3f0jmxczc-poetry-1.3.2/bin/poetry
    ```

2. **Project Setup**

    ```shell
    poetry shell  # if you used devbox, skip this!
    poetry install
    ```

3. **You're all set!**

### Checking and Formatting

scribbplyscrobbply uses [black](https://github.com/psf/black),
[mypy](https://github.com/python/mypy) and [isort](https://github.com/PyCQA/isort)
to check and format code.

```
isort scribbplyscrobbply*.py
black scribbplyscrobbply*.py
mypy scribbplyscrobbply*.py
```

<!-- 
### Deploying

1. **Build the static web app**
    
    ```
    flet publish scribbplyscrobbply-gui.py
    ```
-->

## Licence

scribbplyscrobbply is free and unencumbered software released into the public domain.
For more information, please refer to the [UNLICENCE](/UNLICENCE) file or
<http://unlicense.org/>.

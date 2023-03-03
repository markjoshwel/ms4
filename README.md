# scribbplyscrobbly

A pure Python script to process your Spotify Extended Streaming History JSONs into a
single Last.fm Scrubbler-friendly JSON file.

- [Usage](#usage)
    - [Static Web App](#static-web-app)
    - [Command Line](#command-line)
- [Developing](#developing)
    - [Setup](#setup)
    - [Checking and Formatting](#checking-and-formatting)
    - [Deploying](#deploying)
- [Licence](#licence)

## Usage

### Static Web App

TODO

### Command Line

> **Info**
>
> You will need Python 3.10 or later.

1. Install scribbplyscrobbply as a package:

    ```
    pip install git+https://github.com/markjoshwel/scribbplyscrobbply
    ```

2. Get the earliest and latest discovered timestamps:

    ```
    $ scribbplyscrobbply path-to-files/endsong_*.json
    ```

    Change the timestamps as needed, especially if you want to exclude already scrobbled
    tracks. Timestamps given to scribbplyscrobbply need not have time information. 

3. Generate a JSON:



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
isort scribbplyscrobbply.py
black scribbplyscrobbply.py
mypy scribbplyscrobbply.py
```

### Deploying

TODO

## Licence

scribbplyscrobbply is free and unencumbered software released into the public domain.
For more information, please refer to the [UNLICENCE](/UNLICENCE) file or
<http://unlicense.org/>.
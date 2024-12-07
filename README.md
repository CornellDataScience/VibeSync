# VibeSync

## Getting Started

Create a `.env` file in the root directory of the project and add the following environment variables (filled with valid credentials):
```
CHROME_USER=<put your email here>
CHROME_PASSWORD=<put your password here>
```

## Installation
First, install python 3.11. Then download the following requirements.

```shell
pip install uv
```

```shell
uv pip install -r pyproject.toml
```

Trying running `make db`

## Usage

To run `audio_classification.py`, simply run the following:

```shell
python audio_classification.py
```

To run `audio_caption.py`, simply run the following:

```shell
python audio_caption.py
```


**Reference:** https://github.com/microsoft/CLAP
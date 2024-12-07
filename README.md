# VibeSync

## Getting Started

First, install python 3.8 or higher (3.11 recommended). Then, install CLAP using the following:

```shell
pip install msclap
```
Second, create a `.env` file in the root directory of the project and add the following environment variables (filled with valid credentials):
```
CHROME_USER=<put your email here>
CHROME_PASSWORD=<put your password here>
```

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
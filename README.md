# VibeSync
## Problem Statement
Services like Spotify can generate personalized playlists by leveraging data on what songs their users like. Can we do the same without leveraging user data? In particular, can we build playlists leveraging only song metadata and audio content?
## Description
VibeSync is a research project which aims to explore the boundary of ML research with music. Inspired by recent advances with contrastive learning and joint language-audio embeddings, we aim to build a proof-of-concept system where a user specifies a playlist title and receives recommended songs. We want to see how far take this and what insights we can gain.

## Installation
To install uv and create a virtual environment just run:
```shell
pip install uv
uv sync -p 3.11.5
```
To start the virtual environment, run:
```shell
source .venv/bin/activate
```
To start the app, run `make app`
## Scraper
To use our scraper, create a `.env` file in the root directory of the project and add the following environment variables (filled with valid credentials for [Jamendo](https://jamendo.com/)):
```
CHROME_USER=<put your email here>
CHROME_PASSWORD=<put your password here>
CHROME_USER_2=<put your email here>
CHROME_PASSWORD_2=<put your password here>
```
Add more users as is needed. Then run `make scrape` to run our scraper.
## Who we are
VibeSync was made possible by Michael Ngo, Nancy Chen, Koji Kimura, Samantha Vaca, and Takuma Osaka.

**Reference:** https://github.com/microsoft/CLAP
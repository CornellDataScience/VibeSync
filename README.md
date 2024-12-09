# VibeSync
## Environment
To use our scraper, create a `.env` file in the root directory of the project and add the following environment variables (filled with valid credentials for [Jamendo](https://jamendo.com/)):
```
CHROME_USER=<put your email here>
CHROME_PASSWORD=<put your password here>
```

## Installation
To install uv and create a virtual environemnt just run:
```shell
pip install uv
uv sync -p 3.11.5
```
To start the virtual environment, run:
```shell
source .venv/bin/activate
```

## Usage
To run our scaper, run `make scraper`.

To run our app, run `make app`.

**Reference:** https://github.com/microsoft/CLAP
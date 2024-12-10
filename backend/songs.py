from typing import Set


class Song():
    def __init__(self, title: str, path: str, artist: str = "", url: str = "",
                 id: str = "", duration: float = 0.0, genre: Set[str] = set(),
                 instrument: Set[str] = set(), moodtheme: Set[str] = set(), description: str = "",):
        self.title = title
        self.path = path
        self.artist = artist
        self.url = url
        self.id = id
        self.duration = duration
        self.genre = genre
        self.instrument = instrument
        self.moodtheme = moodtheme
        self.description = description

    def get_metadata(self) -> dict:
        return vars(self)

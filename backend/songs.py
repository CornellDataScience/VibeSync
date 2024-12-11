from typing import Set


class Song():
    def __init__(self, title: str, path: str, id: str, artist: str = "", url: str = "",
                 duration: float = 0.0, genre: Set[str] = set(),
                 instrument: Set[str] = set(), moodtheme: Set[str] = set(), description: str = "",):
        self.title = title.lower()
        self.path = path
        self.artist = artist.lower()
        self.url = url
        self.id = str(id)
        self.duration = duration
        self.genre = MetaSet(set([g.lower() for g in genre]))
        self.instrument = MetaSet(set([i.lower() for i in instrument]))
        self.moodtheme = MetaSet(set([m.lower() for m in moodtheme]))
        self.description = description

    def get_metadata(self) -> dict:
        return vars(self)

# Set class for comparing sets of metadata where equality is


class MetaSet():
    def __init__(self, items: set = set()):
        self.items = items

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return len(self.items.intersection(other.items)) > 0
        else:
            return False

    def __len__(self):
        return len(self.items)

    def __str__(self):
        return "M"+str(self.items)

    def __repr__(self):
        return "M"+str(self.items)

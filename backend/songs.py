class Song():
    def __init__(self, title: str, path: str, artist:str = "", url: str = "", description: str = "",):
        self.title = title
        self.path = path
        self.artist = artist
        self.url = url
        self.description = description

    def get_metadata(self) -> dict:
        return vars(self)

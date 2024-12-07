class Song():
    def __init__(self, title: str, path: str, url: str = "", description: str = "",):
        self.title = title
        self.path = path
        self.url = url
        self.description = description

    def get_metadata(self) -> dict:
        return vars(self)

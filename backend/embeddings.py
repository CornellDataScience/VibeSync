from msclap import CLAP
from langchain_core.embeddings.embeddings import Embeddings


class TextEmbeddings(Embeddings):

    def __init__(self):
        self.model = CLAP(version='2023', use_cuda=False)

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        return self.model.get_text_embeddings(texts).tolist()

    def embed_query(self, query: str) -> list[float]:
        return self.model.get_text_embeddings([query])[0].tolist()


class AudioEmbeddings(Embeddings):

    def __init__(self):
        self.model = CLAP(version='2023', use_cuda=False)

    def embed_documents(self, files: list[str]) -> list[list[float]]:
        return self.model.get_audio_embeddings(files, resample=True).tolist()

    def embed_query(self, file: str) -> list[float]:
        return self.model.get_audio_embeddings([file], resample=True)[0].tolist()

import numpy as np
from msclap import CLAP
from langchain_core.embeddings.embeddings import Embeddings
import os


class TextEmbeddings(Embeddings):

    def __init__(self):
        self.model = CLAP(version='2023', use_cuda=False)

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        # print("Added Text Embedding")
        return self.model.get_text_embeddings(texts).tolist()

    def embed_query(self, query: str) -> list[float]:
        # print("Added Text Embedding")
        return self.model.get_text_embeddings([query])[0].tolist()


class AudioEmbeddings(Embeddings):

    def __init__(self):
        self.model = CLAP(version='2023', use_cuda=False)

    def embed_documents(self, files: list[str]) -> list[list[float]]:
        # print("Added Audio Embedding")
        return self.model.get_audio_embeddings(files, resample=True).tolist()

    def embed_query(self, file: str) -> list[float]:
        # print("Added Audio Embedding")
        return self.model.get_audio_embeddings([file], resample=True)[0].tolist()


class AudioTextEmbeddings(Embeddings):

    def __init__(self):
        self.model = CLAP(version='2023', use_cuda=False)

    def embed_documents(self, docs: list[str]) -> list[list[float]]:
        res = []
        for doc in docs:
            if not doc.lower().strip().endswith('.mp3'):
                res.append(self.model.get_text_embeddings([doc])[0])
                # print("Added Text Embedding")
                continue

            if not os.path.isfile(doc):
                print(f'{doc} does not exists!')
                continue

            res.append(self.model.get_audio_embeddings(
                [doc], resample=True)[0])
            # print("Added Audio Embedding")

        return res

    def embed_query(self, query: str) -> list[float]:
        if not query.lower().strip().endswith('.mp3'):
            # print("Added Text Embedding")
            return self.model.get_text_embeddings([query])[0].tolist()

        if not os.path.isfile(query):
            print(f'{query} does not exists!')
            return

        # print("Added Audio Embedding")
        return self.model.get_audio_embeddings([query], resample=True)[0].tolist()


def normalize_embedding(embedding):
    norm = np.linalg.norm(embedding)
    if norm == 0:
        return embedding
    return embedding / norm


def concat_embeddings(embedding1, embedding2):
    return normalize_embedding(np.concatenate((embedding1, embedding2))).tolist()


def average_embeddings(embedding1, embedding2):
    embedding1 = np.array(embedding1)
    embedding2 = np.array(embedding2)
    return normalize_embedding(((embedding1 + embedding2) / 2)).tolist()

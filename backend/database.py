import faiss
from langchain_community.docstore.in_memory import InMemoryDocstore
from langchain_community.vectorstores import FAISS
from langchain_community.vectorstores.faiss import DistanceStrategy
from langchain_core.documents import Document
import threading
from embeddings import TextEmbeddings, AudioEmbeddings, AudioTextEmbeddings
from embeddings import concat_embeddings, average_embeddings

from songs import Song

import os

import torch
from custom_similarity import CustomSimilarity


class Database():

    def __init__(self, path: str, include_text_embeddings: bool = False):
        self.path = os.path.join('vector_stores', path)

        self.include_text_embeddings = include_text_embeddings

        self.text_embeddings = TextEmbeddings()
        self.audio_embeddings = AudioEmbeddings()
        self.audio_text_embeddings = AudioTextEmbeddings()
        self.lock = threading.Lock()

        if os.path.isdir(self.path):
            self.db = FAISS.load_local(
                self.path, self.text_embeddings, allow_dangerous_deserialization=True)

            print(
                f'Loaded db from {self.path} with {self.db.index.ntotal} entries.')
            return

        index = faiss.IndexFlatIP(
            len(self.text_embeddings.embed_query("hello world")))

        self.db = FAISS(
            embedding_function=self.audio_text_embeddings,
            index=index,
            docstore=InMemoryDocstore(),
            normalize_L2=True,
            index_to_docstore_id={},
            distance_strategy=DistanceStrategy.COSINE
        )

        print(f'Created db from scratch.')

    def post_mixed_songs(self, songs: list[Song]) -> list[str]:
        """Add a song to the FAISS database."""

        files = [song.path for song in songs]
        titles = [song.title for song in songs]
        metadatas = [song.get_metadata() for song in songs]

        audio_embeddings = self.audio_embeddings.embed_documents(files)
        title_embeddings = self.text_embeddings.embed_documents(titles)

        # embeddings = concat_embeddings(audio_embeddings, title_embeddings)
        embeddings = average_embeddings(audio_embeddings, title_embeddings)

        text_embeddings = zip(titles, embeddings)

        audio_ids = self.db.add_embeddings(text_embeddings, metadatas)

        print(f'Uploaded {len(audio_ids)} songs to database.')

        return audio_ids

    def post_songs(self, songs: list[Song]) -> list[str]:
        """Add a song to the FAISS database."""

        files = [song.path for song in songs]
        titles = [song.title for song in songs]
        metadatas = [song.get_metadata() for song in songs]

        audio_metadatas = [{**metadata, "doc_type": "audio"}
                           for metadata in metadatas]

        ids = []

        with self.lock:
            audio_ids = self.db.add_texts(files, audio_metadatas)
            ids.extend(audio_ids)

            if self.include_text_embeddings:
                text_metadatas = [{**metadata, "doc_type": "text"}
                                  for metadata in metadatas]

                text_ids = self.db.add_texts(titles, text_metadatas)
                ids.extend(text_ids)

        print(f'Uploaded {len(audio_ids)} songs to database.')

        return ids

    def get_playlist(self, title: str, k: int = 3) -> list[tuple[Document, float]]:
        """Retrieve k-nearest songs from FAISS database."""

        songs_and_scores = self.db.similarity_search_with_relevance_scores(
            title, k)

        print(f'Retrieved playlist of name {title}.')

        return songs_and_scores

    def save_db(self):
        """Save the FAISS database to the specified path."""

        self.db.save_local(self.path)

        print(f'Saved db to {self.path}.')


if __name__ == '__main__':
    # Example workflow
    db = Database('faiss_index', False)

    folder_path = 'audio'
    if not os.path.isdir(folder_path):
        raise ValueError(f"The path '{folder_path}' is not a valid directory.")

    songs = []
    for root, _, filenames in os.walk(folder_path):
        for filename in filenames:
            if filename.lower().endswith(".mp3"):
                path = os.path.join(root, filename)
                title = os.path.splitext(filename)[0].lower().replace('_', " ")
                songs.append(Song(title, path))
                print((title, path))

    db.post_songs(songs)

    playlist_title = "classical instruments"

    playlist = db.get_playlist(playlist_title, k=3)
    print(playlist)

    db.save_db()

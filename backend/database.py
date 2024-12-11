import faiss
from langchain_community.docstore.in_memory import InMemoryDocstore
from langchain_community.vectorstores import FAISS
from langchain_community.vectorstores.faiss import DistanceStrategy
from langchain_core.documents import Document

from embeddings import TextEmbeddings, AudioEmbeddings, AudioTextEmbeddings
from embeddings import concat_embeddings, average_embeddings

from songs import Song
from songs import MetaSet

import threading
import os


class Database():

    def __init__(self, path: str, include_all_embeddings: bool = True):
        self.path = os.path.join('vector_stores', path)

        self.include_all_embeddings = include_all_embeddings

        self.text_embeddings = TextEmbeddings()
        self.audio_embeddings = AudioEmbeddings()
        self.audio_text_embeddings = AudioTextEmbeddings()
        self.lock = threading.Lock()

        if os.path.isdir(self.path):
            self.db = FAISS.load_local(
                self.path,
                self.audio_text_embeddings,
                normalize_L2=True,
                distance_strategy=DistanceStrategy.COSINE,
                allow_dangerous_deserialization=True,
                relevance_score_fn=self.score_normalizer
            )

            print(
                f'Loaded db from {self.path} with {self.db.index.ntotal} entries.')
            return

        # Inner Product
        index = faiss.IndexFlatIP(
            len(self.audio_text_embeddings.embed_query("hello world")))

        self.db = FAISS(
            embedding_function=self.audio_text_embeddings,
            index=index,
            docstore=InMemoryDocstore(),
            normalize_L2=True,
            index_to_docstore_id={},
            distance_strategy=DistanceStrategy.COSINE,
            relevance_score_fn=self.score_normalizer
        )

        print(f'Created db from scratch.')

    def score_normalizer(self, val: float) -> float:
        return val

    def post_songs(self, songs: list[Song]) -> list[str]:
        """Add a song to the FAISS database."""
        files = [song.path for song in songs]
        titles = [song.title for song in songs]
        metadatas = [song.get_metadata() for song in songs]

        audio_metadatas = [{**metadata, "doc_type": "audio"}
                           for metadata in metadatas]
        text_metadatas = [{**metadata, "doc_type": "text"}
                          for metadata in metadatas]
        mixed_metadatas = [{**metadata, "doc_type": "mixed"}
                           for metadata in metadatas]

        audio_embeddings = self.audio_embeddings.embed_documents(files)
        text_embeddings = self.text_embeddings.embed_documents(titles)
        mixed_embeddings = average_embeddings(
            audio_embeddings, text_embeddings)

        audio_ids = ["audio_" + metadata['id'] for metadata in metadatas]
        text_ids = ["text_" + metadata['id'] for metadata in metadatas]
        mix_ids = ["mixed_" + metadata['id'] for metadata in metadatas]
        ids = []

        with self.lock:
            try:
                # Audio
                ids.extend(self.db.add_embeddings(
                    zip(titles, audio_embeddings), audio_metadatas, audio_ids))

                if self.include_all_embeddings:
                    # Text
                    ids.extend(self.db.add_embeddings(
                        zip(titles, text_embeddings), text_metadatas, text_ids))

                    # Mixed
                    ids.extend(self.db.add_embeddings(
                        zip(titles, mixed_embeddings), mixed_metadatas, mix_ids))

                print(
                    f'Uploaded {len(audio_ids)} songs to database. Size is now {self.db.index.ntotal}')
            except Exception as e:
                print(e)

        return ids

    def get_playlist(self, title: str, k: int = 3, filter: dict = None) -> list[tuple[Document, float]]:
        """Retrieve k-nearest songs from FAISS database."""
        songs_and_scores = self.db.similarity_search_with_relevance_scores(
            title, k, fetch_k=self.db.index.ntotal, filter=filter)

        print(f'Retrieved playlist of name {title}.')

        return songs_and_scores

    def save_db(self):
        """Save the FAISS database to the specified path."""

        self.db.save_local(self.path)

        print(f'Saved db to {self.path}.')


if __name__ == '__main__':
    # Example workflow

    db = Database('faiss_index', True)
    folder_path = 'audio'
    if not os.path.isdir(folder_path):
        raise ValueError(f"The path '{folder_path}' is not a valid directory.")

    songs = []
    genre1 = {"rOck", "edm"}
    genre2 = {"eMo", "HaPPY"}
    for root, _, filenames in os.walk(folder_path):
        for i, filename in enumerate(filenames):
            if filename.lower().endswith(".mp3"):
                path = os.path.join(root, filename)
                title = os.path.splitext(filename)[0].lower().replace('_', " ")

                if i % 2 == 0:
                    songs.append(Song(title, path, id=str(
                        i), genre=genre1))
                if i % 2 == 1:
                    songs.append(Song(title, path, id=str(
                        i), genre=genre2))
                print((title, path))

    db.post_songs(songs)

    playlist_title = "classical instruments"

    playlist = db.get_playlist(playlist_title, k=3, filter={
                               'genre': MetaSet({'emo'}), 'doc_type': "audio"})
    print(playlist)

    # db.save_db()

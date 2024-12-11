import streamlit as st
from songs import Song, MetaSet
from database import Database
import os

# Initialize database
if 'db' not in st.session_state:
    st.session_state.db = Database(
        'first_100', include_all_embeddings=True)

genres = [
    "alternative", "ambient", "atmospheric", "chillout", "classical",
    "dance", "downtempo", "easylistening", "electronic", "experimental",
    "folk", "funk", "hiphop", "house", "indie", "instrumentalpop",
    "jazz", "lounge", "metal", "newage", "orchestral", "pop",
    "popfolk", "poprock", "reggae", "rock", "soundtrack", "techno",
    "trance", "triphop", "world"
]

instruments = [
    "acousticguitar", "bass", "computer", "drummachine", "drums",
    "electricguitar", "electricpiano", "guitar", "keyboard", "piano",
    "strings", "synthesizer", "violin", "voice"
]

moods_themes = [
    "happy", "energetic", "relaxing", "film", "dark", "epic", "melodic",
    "inspiring", "emotional", "dream", "love", "uplifting", "deep",
    "soundscape", "background", "positive", "sad", "meditative",
    "motivational", "christmas", "advertising", "romantic", "space",
    "corporate", "documentary", "action", "slow", "calm", "adventure",
    "summer", "drama", "melancholic", "fun", "upbeat", "soft", "movie",
    "sport", "dramatic", "ballad", "commercial", "cool", "game",
    "trailer", "children", "retro", "hopeful", "nature", "party", "funny",
    "powerful", "heavy", "holiday", "travel", "groovy", "fast", "sexy"
]


def main():
    st.title("Vibesync's Playlist Generator 🎵")

    playlist()


def playlist():
    st.subheader("Retrieve Playlist")

    playlist_name = st.text_input("Enter Playlist Name")

    k = st.number_input("Number of Songs to Retrieve",
                        min_value=1, max_value=20, value=3)

    doc_type = st.selectbox('Choose a vector type to search by:',
                            ['audio', 'text', 'mixed'], index=0)

    # Create dropdowns with multi-select functionality
    selected_genres = st.multiselect("Select Genres", genres, default=None)

    selected_instruments = st.multiselect(
        "Select Instruments", instruments, default=None)

    selected_moods = st.multiselect(
        "Select Moods/Themes", moods_themes, default=None)

    if st.button("Get Playlist"):
        if playlist_name:
            try:
                # set up filter
                filter = {'doc_type': doc_type}
                if len(selected_genres) > 0:
                    filter['genre'] = MetaSet(set(selected_genres))
                if len(selected_instruments) > 0:
                    filter['instrument'] = MetaSet(set(selected_instruments))
                if len(selected_moods) > 0:
                    filter['moodtheme'] = MetaSet(set(selected_moods))
                print("Filter:", filter)
                # request playlist
                playlist = st.session_state.db.get_playlist(
                    playlist_name, k, filter=filter)

                # show results
                st.write(f"Songs in '{playlist_name}':")
                print(f"Retrieved {len(playlist)} songs!")
                for song, score in playlist:
                    metadata = song.metadata
                    pretty_print_audio_metadata(metadata)
                    display_song(metadata, score)
                    # st.write(
                    # f"- [{metadata['artist']} - {metadata['title']}]({metadata['url']})\n (Score: {score:.2f}) - {metadata['doc_type']}")
            except Exception as e:
                st.error(f"Error retrieving playlist: {e}")
        else:
            st.error("Please enter a playlist name.")


def display_song(metadata: dict, score: float):
    st.subheader(metadata['title'].title(), divider=True)
    st.write(f"**Artist:** {metadata['artist'].title()}")
    st.write(f"**Type:** {metadata['doc_type']}")
    st.write(f"**Score:** {score:.2f}")

    st.link_button("**Play Song** ▶️", metadata['url'])


def pretty_print_audio_metadata(metadata):
    """
    Pretty-prints audio metadata in a structured and readable format.

    Args:
        metadata (dict): A dictionary containing audio metadata.
    """
    print("Audio Metadata:")
    print("=" * 40)

    for key, value in metadata.items():
        if isinstance(value, set):
            # Sort and convert set to a string for better readability
            value = ", ".join(sorted(value))
        print(f"{key.capitalize():<15}: {value}")


if __name__ == "__main__":
    main()

import streamlit as st
from songs import Song
from database import Database
import os

# Initialize database
if 'db' not in st.session_state:
    st.session_state.db = Database(
        'first_32_000', include_text_embeddings=True)


def main():
    st.title("Music Playlist Generator")

    # Sidebar for navigation
    menu = ["Retrieve Playlist", "Upload Songs"]
    choice = st.sidebar.selectbox("Menu", menu)

    if choice == "Retrieve Playlist":
        st.subheader("Retrieve Playlist")
        playlist_name = st.text_input("Enter Playlist Name")
        k = st.number_input("Number of Songs to Retrieve",
                            min_value=1, max_value=10, value=3)

        if st.button("Get Playlist"):
            if playlist_name:
                try:
                    playlist = st.session_state.db.get_playlist(
                        playlist_name, k)
                    st.write(f"Songs in '{playlist_name}':")
                    for song, score in playlist:
                        metadata = song.metadata
                        print(metadata)
                        st.write(
                            f"- [{metadata['artist']} - {song.page_content}]({metadata['url']}) (Score: {score:.2f}) ")
                except Exception as e:
                    st.error(f"Error retrieving playlist: {e}")
            else:
                st.error("Please enter a playlist name.")

    elif choice == "Upload Songs":
        st.subheader("Upload Songs")
        uploaded_files = st.file_uploader(
            "Upload MP3 Files", type="mp3", accept_multiple_files=True)

        if uploaded_files:
            songs = []
            for uploaded_file in uploaded_files:
                try:
                    # Save uploaded file temporarily
                    temp_path = os.path.join(
                        "temp_uploads", uploaded_file.name)
                    with open(temp_path, "wb") as f:
                        f.write(uploaded_file.getbuffer())

                    title = os.path.splitext(uploaded_file.name)[
                        0].lower().replace('_', " ")
                    songs.append(Song(title, temp_path))
                except Exception as e:
                    st.error(
                        f"Error processing file {uploaded_file.name}: {e}")

            if songs:
                try:
                    st.session_state.db.post_songs(songs)
                    st.success(f"Uploaded {len(songs)} songs successfully!")

                    # Clean up temporary files
                    for song in songs:
                        os.remove(song.path)
                except Exception as e:
                    st.error(f"Error uploading songs: {e}")


if __name__ == "__main__":
    main()

import os
import streamlit as st
from mutagen.mp3 import MP3
from mutagen.easyid3 import EasyID3
import tempfile
import sys

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from utils.metaDataUtils import searchAppleMetaData, updateSong, find_cover_art, get_current_cover, embed_coverart
from utils.downloadUtils import downloadSong

import streamlit as st
from PIL import Image
import io

title, artist, album, track_num, genre, year = "", "", "", "", "", ""
file_path_present = False
save_path = os.getcwd()+"\\Downloads\\"
downloadCoverArt = "No"

def process_url(url: str):
    if downloadSong(url, save_path):
        st.session_state["result_image"] = Image.new("RGB", (300, 200), color="lightblue")

def process_uploaded_file(file: str):
    audiofile = MP3(file, ID3=EasyID3)
    global title, artist, album, track_num, genre, year
    title = audiofile.get('title')[0]
    artist = audiofile.get('artist')[0]
    album = audiofile.get('album')[0]
    track_num = audiofile.get('tracknumber')[0]
    genre = audiofile.get('genre')[0]
    year = str(audiofile.get('date')[0])

    st.session_state["result_image"] = get_current_cover(file)

st.set_page_config(page_title="Media Processor", layout="wide")

left, right = st.columns([1, 1.5], gap="large")

with left:
    st.header("Input Source")

    url = st.text_input("Enter a URL:")
    if st.button("Search URL"):
        if url:
            process_url(url)
            file_path_present = True
        else:
            st.warning("Please enter a valid URL.")

    st.markdown("### or Upload a File")
    uploaded_file = st.file_uploader("Drag and drop a file here", type=["mp3", "mp4", "webm"])
    if uploaded_file:
        with tempfile.NamedTemporaryFile(delete=False) as tmp_file:
            tmp_file.write(uploaded_file.read())
            temp_path = tmp_file.name
        print(temp_path)
        process_uploaded_file(temp_path)
        file_path_present = True

with right:
    st.header("Metadata Updater")

    metadata_query = st.text_input("Search song for metadata")
    if st.button("Search and Populate Song information and Cover Art") and file_path_present:
        title, artist, album, track_number, track_total, genre, year = searchAppleMetaData(metadata_query)
        track_num = str(track_number) + "/" + str(track_total) if track_number else ""
        if downloadCoverArt == "Yes":
            find_cover_art(temp_path)
            st.session_state["result_image"] = get_current_cover(save_path)
    
    downloadCoverArt = st.radio("Download cover art", ("Yes", "No"))

    if "result_image" not in st.session_state:
        st.session_state.result_image = None

    with st.container():
        st.markdown("#### Preview Cover Art (Drag and drop to replace)")

        uploaded_img = st.file_uploader(
            "Drop new cover art here", type=["jpg", "jpeg", "png", "webp"], label_visibility="collapsed"
        )

        if uploaded_img:
            # Convert uploaded image (even .webp) to standard PIL image
            st.session_state.result_image = Image.open(io.BytesIO(uploaded_img.read()))

        if st.session_state.result_image:
            preview_img = st.session_state.result_image.resize((300, 300))
            st.image(preview_img, width=300)
        else:
            placeholder = Image.new("RGB", (300, 300), color="gray")
            st.image(placeholder, width=300, caption="No image loaded")

    # Text inputs (5 boxes)
    st.markdown("#### Metadata Fields")
    metacol1, metacol2 = st.columns(2)
    with metacol1:
        title_input = st.text_input("Title", value=title)
        artist_input = st.text_input("Artist", value=artist)
        album_input = st.text_input("Album", value=album)
    with metacol2:
        genre_input = st.text_input("Genre", value=genre)
        year_input = st.text_input("Year", value=year)
        track_num = st.text_input("Track Number / Total Number of Tracks (separated by /)", value=track_num)

    # Example action button
    if st.button("Save / Update") and file_path_present:
        embed_coverart(temp_path, st.session_state.result_image, uploaded_file.name.split(".")[1])
        updateSong(temp_path, title_input, artist_input, album_input, year_input, genre_input, track_num)
        os.rename(temp_path, save_path + title_input + " - " + artist_input + ".mp3") # assumes mp3
        st.success("Data submitted successfully!")
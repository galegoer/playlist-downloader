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

default_fields = {
    "title": "",
    "artist": "",
    "album": "",
    "track_num": "",
    "genre": "",
    "year": "",
}

for key, default in default_fields.items():
    if key not in st.session_state:
        st.session_state[key] = default

if "url" not in st.session_state:
    st.session_state.url = ""

if "save_path" not in st.session_state:
    st.session_state.save_path = os.getcwd()+"\\Downloads\\"

if "metadata_loaded" not in st.session_state:
    st.session_state.metadata_loaded = False

if "downloadCoverArt" not in st.session_state:
    st.session_state.downloadCoverArt = "No"

if "metadata_query" not in st.session_state:
    st.session_state.metadata_query = None

if "last_uploaded_name" not in st.session_state:
    st.session_state.last_uploaded_name = None

if "cover_art_image" not in st.session_state:
    st.session_state.cover_art_image = None

if "result_image" not in st.session_state:
    st.session_state.result_image = None

def process_url():
    try:
        download_path = downloadSong(st.session_state.url, st.session_state.save_path)
        find_cover_art(download_path)
        update_metadata_view(download_path)
        return download_path
    except Exception as e:
        raise e

def update_metadata_view(file: str):
    audiofile = MP3(file, ID3=EasyID3)

    st.session_state.title = audiofile.get('title')[0]
    st.session_state.artist = audiofile.get('artist')[0]
    st.session_state.album = audiofile.get('album')[0]
    st.session_state.track_num = audiofile.get('tracknumber')[0]
    st.session_state.genre = audiofile.get('genre')[0]
    st.session_state.year = str(audiofile.get('date')[0])

    st.session_state["result_image"], st.session_state["image_bytes"], st.session_state["image_name"] = get_current_cover(file)

st.set_page_config(page_title="Media Processor", layout="wide")

left, right = st.columns([1, 1.5], gap="large")

with left:
    st.header("Input Source")

    st.text_input("Enter a YouTube URL:", key="url")
    if st.button("Download Song"):
        if st.session_state.url:
            try:
                st.session_state.file_path = process_url()
                st.success("Your song has been downloaded! Its metadata can be found on the right hand side.")
            except Exception as e:
                st.warning("Error downloading url: " + str(e))
        else:
            st.warning("Please enter a valid URL.")

    st.markdown("### or Upload a File")
    uploaded_file = st.file_uploader("Drag and drop a file here", type=["mp3", "mp4", "webm"])
    if uploaded_file and uploaded_file.name != st.session_state.last_uploaded_name:
        st.session_state.last_uploaded_name = uploaded_file.name
        with tempfile.NamedTemporaryFile(delete=False) as tmp_file:
            tmp_file.write(uploaded_file.read())
            temp_path = tmp_file.name
        print(temp_path)
        update_metadata_view(temp_path)
        st.session_state.file_path = temp_path

with right:
    st.header("Metadata Updater")

    st.text_input("Search song for metadata", key="metadata_query")
    if st.button("Search and Populate Song information") and st.session_state.file_path:
        try:
            title, artist, album, track_number, track_total, genre, year = searchAppleMetaData(st.session_state.metadata_query)
            st.session_state.title = title
            st.session_state.artist = artist
            st.session_state.album = album
            st.session_state.genre = genre
            st.session_state.year = year

            st.session_state.track_num = str(track_number) + "/" + str(track_total) if track_number else ""
            if st.session_state.downloadCoverArt == "Yes":
                find_cover_art(st.session_state.file_path)
                st.session_state["result_image"], st.session_state["image_bytes"], st.session_state["image_name"] = get_current_cover(st.session_state.file_path)
        except:
            st.warning("Could not find song information for: " + st.session_state.metadata_query)
    
    st.radio("Download cover art", ("Yes", "No"), key="downloadCoverArt")

    with st.container():
        st.markdown("#### Preview Cover Art (Drag and drop to replace)")

        cover_art_image = st.file_uploader(
            "Drop new cover art here", type=["jpg", "jpeg", "png", "webp"],
            label_visibility="collapsed"
        )

        if cover_art_image:
            # Convert uploaded image (even .webp) to standard PIL image
            bytes = io.BytesIO(cover_art_image.read())
            st.session_state.result_image = Image.open(bytes)
            st.session_state.image_bytes = bytes
            st.session_state.image_name = cover_art_image.name.split(".")[1]

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
        st.text_input("Title", key="title")
        st.text_input("Artist", key="artist")
        st.text_input("Album", key="album")
    with metacol2:
        st.text_input("Genre", key="genre")
        st.text_input("Year", key="year")
        st.text_input("Track Number / Total Number of Tracks (separated by /)", key="track_num")

    # Example action button
    if st.button("Save / Update") and st.session_state.file_path:
        st.write(st.session_state.title, st.session_state.artist, st.session_state.album)
        print(st.session_state.title)
        updateSong(st.session_state.file_path, st.session_state.title, st.session_state.artist, st.session_state.album, st.session_state.year, st.session_state.genre, st.session_state.track_num)
        embed_coverart(st.session_state.file_path, st.session_state.image_bytes, st.session_state["image_name"])
        os.rename(st.session_state.file_path, st.session_state.save_path + st.session_state.title + " - " + st.session_state.artist + ".mp3") # assumes mp3
        st.success(f"File saved successfully to {st.session_state.save_path} !")
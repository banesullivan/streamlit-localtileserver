import argparse
import json
import sys
from json.decoder import JSONDecodeError
from pathlib import Path

import folium
import streamlit as st
from appdirs import user_data_dir
from folium.plugins import Fullscreen
from localtileserver import TileClient, get_folium_tile_layer
from localtileserver.validate import (
    ValidateCloudOptimizedGeoTIFFException,
    validate_cog,
)
from streamlit_folium import folium_static

st.set_page_config(page_title="streamlit-localtileserver")

"# streamlit-localtileserver"

# TODO: set `"LOCALTILESERVER_CLIENT_PREFIX"`


def parse_args(args):
    parser = argparse.ArgumentParser("Data Diagnostics")
    parser.add_argument("-f", "--filename", help="Local path or URL", required=False)
    return parser.parse_args(args)


def upload_file_to_path(uploaded_file):
    path = Path(user_data_dir("localtileserver"), uploaded_file.name)
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "wb") as f:
        f.write(uploaded_file.getvalue())
    return str(path.absolute())


args = parse_args(sys.argv[1:])
uploaded_file = st.file_uploader("Upload a raster")
url = st.text_input(
    "Or input a URL, try: https://data.kitware.com/api/v1/file/626854a14acac99f42126a74/download",
    placeholder="https://data.kitware.com/api/v1/file/626854a14acac99f42126a74/download",
)
arg_path = args.filename

with st.expander("Styling"):
    style_text = st.text_area(
        "Style dictionary",
        help="https://girder.github.io/large_image/tilesource_options.html#style",
    )
style = None
if style_text:
    try:
        style = json.loads(style_text)
    except JSONDecodeError:
        st.warning("Style is not valid JSON")


if uploaded_file or url or arg_path:
    if uploaded_file:
        path = upload_file_to_path(uploaded_file)
    elif url:
        path = url
    elif arg_path:
        path = arg_path

    client = TileClient(path)
    layer = get_folium_tile_layer(client, style=style)

    try:
        is_valid = validate_cog(client)
    except ValidateCloudOptimizedGeoTIFFException:
        is_valid = False
    st.write(f"Is valid Cloud Optimized GeoTiff?: {is_valid}")

    m = folium.Map(location=client.center(), zoom_start=client.default_zoom)
    m.add_child(layer)

    with st.sidebar:
        st.image(client.thumbnail())
        st.write("Metadata")
        st.json(client.metadata())
else:
    with st.sidebar:
        pass
    m = folium.Map()

Fullscreen().add_to(m)

# call to render Folium map in Streamlit
folium_static(m)

import argparse
from pathlib import Path
import sys

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

"# streamlit-localtileserver"

# TODO: set `"LOCALTILESERVER_CLIENT_PREFIX"`


def parse_args(args):
    parser = argparse.ArgumentParser('Data Diagnostics')
    parser.add_argument('-f', '--filename', help='Local path or URL', required=False)
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
    "Or input a URL (try https://data.kitware.com/api/v1/file/626854a14acac99f42126a74/download)"
)
arg_path = args.filename

if uploaded_file or url or arg_path:
    if uploaded_file:
        client = TileClient(upload_file_to_path(uploaded_file))
    elif url:
        client = TileClient(url)
    elif arg_path:
        client = TileClient(arg_path)
    layer = get_folium_tile_layer(client)

    try:
        is_valid = validate_cog(client)
    except ValidateCloudOptimizedGeoTIFFException:
        is_valid = False
    st.write(f"Is valid Cloud Optimized GeoTiff?: {is_valid}")

    m = folium.Map(location=client.center(), zoom_start=client.default_zoom)
    m.add_child(layer)
else:
    m = folium.Map()

Fullscreen().add_to(m)

# call to render Folium map in Streamlit
folium_static(m)

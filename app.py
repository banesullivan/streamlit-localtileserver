import os
from pathlib import Path

import folium
import streamlit as st
from appdirs import user_data_dir
from localtileserver import TileClient, get_folium_tile_layer
from localtileserver.validate import (
    ValidateCloudOptimizedGeoTIFFException,
    validate_cog,
)
from streamlit_folium import folium_static

"# streamlit-localtileserver"

if os.environ.get("JUPYTERHUB_SERVICE_PREFIX") is not None:
    os.environ[
        "LOCALTILESERVER_CLIENT_PREFIX"
    ] = f"{os.environ['JUPYTERHUB_SERVICE_PREFIX'].lstrip('/')}/proxy/{{port}}"


def upload_file_to_path(uploaded_file):
    path = Path(user_data_dir("localtileserver"), uploaded_file.name)
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "wb") as f:
        f.write(uploaded_file.getvalue())
    return str(path.absolute())

st.write(os.environ)


uploaded_file = st.file_uploader("Upload a raster")
url = st.text_input("Or input a URL (try https://data.kitware.com/api/v1/file/626854a14acac99f42126a74/download)")
if uploaded_file or url:
    if uploaded_file is not None:
        client = TileClient(upload_file_to_path(uploaded_file))
    elif url is not None:
        client = TileClient(url)
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

# call to render Folium map in Streamlit
folium_static(m)

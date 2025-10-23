import os
import zipfile
import io
import pyodide
import js
import base64
import mimetypes
from urllib.parse import quote
from IPython.display import display_html


def zip_folder_bytes(folder_path="/files"):
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, "w") as zipf:
        for root, dirs, files in os.walk(folder_path):
            for file in files:
                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, start=folder_path)
                zipf.write(file_path, arcname=arcname)
    zip_buffer.seek(0)
    return zip_buffer.getvalue()


def download_folder(folder_path='.', filename="jupyterlite_files.zip"):
    zip_bytes = zip_folder_bytes(folder_path)
    
    uint8 = pyodide.ffi.to_js(zip_bytes)
    
    blob = js.Blob.new([uint8], {"type": "application/zip"})
    url = js.URL.createObjectURL(blob)
    
    # create HTML link
    html = f'<a download="{filename}" href="{url}">Download {filename}</a>'
    display_html(html, raw=True)


def file_to_data_url(path: str, site_url=None) -> str:
    if site_url is None:
        site_url = str(js.location).split('/extensions')[0]

    mime_type, _ = mimetypes.guess_type(path)
    if not mime_type:
        mime_type = "application/json"
    
    with open(path, "rb") as f:
        data = f.read()
    b64_data = quote(base64.b64encode(data).decode("ascii"))
    
    filename = path.split("/")[-1]
    filename_quoted = quote(filename)
    
    url = f"data:{mime_type};name={filename_quoted};base64,{b64_data}"
    return f"{site_url}/lab?fromURL={url}"
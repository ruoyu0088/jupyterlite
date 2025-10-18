import os
import zipfile
import io
import pyodide
import js
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

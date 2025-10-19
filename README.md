# JupyterLite Demo

[![lite-badge](https://jupyterlite.rtfd.io/en/latest/_static/badge.svg)](https://jupyterlite.github.io/demo)

JupyterLite deployed as a static site to GitHub Pages, for demo purposes.

This is a customized JupyterLite build that can load Python packages from three locations:

1. The official Pyodide hosted on [jsDelivr](https://cdn.jsdelivr.net)
2. Pure Python packages from [pythonhosted.org](https://files.pythonhosted.org)
3. Your own packages from the local `static/pyodide` directory

`pyodide.tar.bz2` is a minimized version of Pyodide v0.27.7 that excludes all built-in packages.

## Adding Packages

* **From PythonHosted:**
  Edit `utils.py`, append your package information to the list returned by `get_pypi_packages()`, then run:

  ```bash
  python utils.py create
  ```

  This command will generate the `pypi_packages.json` file.

* **Local `.whl` packages:**
  Place your `.whl` files into the `whl_packages` folder.

* **Local source packages:**
  Place your package folder under the `packages` directory.
  Each folder in `packages` will be compressed into a `.whl` file and copied to the local `static` directory.

* **Notebooks:**
  Copy your Jupyter notebooks into the `content` folder.

## Download Notebooks

In a JupyterLite notebook, you can use the following code to compress a folder into a zip file and download it:

```python
from helper.jupyterlite import download_folder
download_folder('your_folder_name')
```

## ✨ Try it in your browser ✨

➡️ **https://ruoyu0088.github.io/jupyterlite**

![github-pages](https://user-images.githubusercontent.com/591645/120649478-18258400-c47d-11eb-80e5-185e52ff2702.gif)

## Requirements

JupyterLite is being tested against modern web browsers:

- Firefox 90+
- Chromium 89+

## Deploy your JupyterLite website on GitHub Pages

Check out the guide on the JupyterLite documentation: https://jupyterlite.readthedocs.io/en/latest/quickstart/deploy.html

## Further Information and Updates

For more info, keep an eye on the JupyterLite documentation:

- How-to Guides: https://jupyterlite.readthedocs.io/en/latest/howto/index.html
- Reference: https://jupyterlite.readthedocs.io/en/latest/reference/index.html

This template provides the Pyodide kernel (`jupyterlite-pyodide-kernel`), the JavaScript kernel (`jupyterlite-javascript-kernel`), and the p5 kernel (`jupyterlite-p5-kernel`), along with other
optional utilities and extensions to make the JupyterLite experience more enjoyable. See the
[`requirements.txt` file](requirements.txt) for a list of all the dependencies provided.

For a template based on the Xeus kernel, see the [`jupyterlite/xeus-python-demo` repository](https://github.com/jupyterlite/xeus-python-demo)
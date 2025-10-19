import base64
import zipfile
import json
import hashlib
import shutil
from dataclasses import dataclass, field
from pathlib import Path
import requests

PYODIDE_FOLDER = Path("./dist/static/pyodide")
WHL_PACKAGE_FOLDER = Path("./whl_packages")
PACKAGE_FOLDER = Path("./packages")
PYODIDE_LOCK_FILE = PYODIDE_FOLDER / "pyodide-lock.json"
PYODIDE_VERSION = "v0.27.7"


def find_pythonhosted_info(pkg_name: str, version: str) -> dict:
    cache_folder = Path("./request_cach")
    if not cache_folder.exists():
        cache_folder.mkdir()

    pkg_file_name = cache_folder / pkg_name
    if pkg_file_name.exists():
        with open(pkg_file_name, encoding="utf-8") as f:
            data = json.load(f)
    else:
        resp = requests.get(f"https://pypi.org/pypi/{pkg_name}/json", timeout=10)
        if resp.status_code != 200:
            return None
        with open(pkg_file_name, "w", encoding="utf-8") as f:
            f.write(resp.text)
        data = resp.json()

    file_infos = data["releases"].get(version, [])
    for info in file_infos:
        if info["filename"].endswith(".whl"):
            return info
    return None


def sha256sum(path):
    """Compute SHA256 checksum for the given file."""
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()


def record_entry(path):
    """Generate a RECORD entry with sha256 and size."""
    with open(path, "rb") as f:
        data = f.read()
    digest = hashlib.sha256(data).digest()
    hash_b64 = base64.urlsafe_b64encode(digest).rstrip(b"=").decode()
    size = len(data)
    return f"{path},sha256={hash_b64},{size}"


def make_wheel(
    package_dir,
    package_name,
    version,
    target_dir=".",
    py_tag="py3",
    abi_tag="none",
    platform_tag="any",
    ignore_files=[],
):
    package_dir = Path(package_dir)
    # Verify package_dir exists
    if not package_dir.is_dir():
        print(f"Error: directory '{package_dir}' does not exist.")
        return

    dist_info_dir = Path(f"{package_name}-{version}.dist-info")
    dist_info_dir.mkdir(exist_ok=True)

    # Create WHEEL file
    wheel_text = f"""Wheel-Version: 1.0
Generator: manual
Root-Is-Purelib: true
Tag: {py_tag}-{abi_tag}-{platform_tag}
"""
    with open(dist_info_dir / "WHEEL", "w") as f:
        f.write(wheel_text)

    # Create METADATA file
    metadata_text = f"""Metadata-Version: 2.1
Name: {package_name}
Version: {version}
Summary: {package_name} packaged manually
"""
    with open(dist_info_dir / "METADATA", "w") as f:
        f.write(metadata_text)

    # Gather all files
    all_files = []
    for root, _, files in package_dir.walk():
        for file in files:
            all_files.append(root / file)
    for root, _, files in dist_info_dir.walk():
        for file in files:
            all_files.append(root / file)

    # Create RECORD file
    record_path = dist_info_dir / "RECORD"
    with open(record_path, "w") as f:
        for file in all_files:
            f.write(record_entry(file) + "\n")
        f.write(f"{dist_info_dir}/RECORD,,\n")

    # Name the wheel file
    wheel_filename = f"{package_name}-{version}-{py_tag}-{abi_tag}-{platform_tag}.whl"

    # Zip everything
    with zipfile.ZipFile(
        Path(target_dir) / wheel_filename, "w", zipfile.ZIP_DEFLATED
    ) as zf:
        for file in all_files:
            file_path = Path(file)
            if file_path.name in ignore_files:
                continue

            if file_path.is_relative_to(package_dir):
                arcname = file_path.relative_to(package_dir.parent)
            else:
                arcname = file
            zf.write(file, arcname=arcname)

    shutil.rmtree(dist_info_dir)

    print(f"Wheel file created: {wheel_filename}")


@dataclass
class Package:
    name: str
    version: str
    imports: list[str]
    depends: list[str] = field(default_factory=list)
    sha256: str = ""
    file_name: str = ""

    def __post_init__(self):
        if not self.file_name:
            info = find_pythonhosted_info(self.name, self.version)
            self.sha256 = info["digests"]["sha256"]
            self.file_name = info["url"]
        else:
            self.sha256 = sha256sum(WHL_PACKAGE_FOLDER / self.file_name)

    @property
    def json(self):
        return {
            "depends": self.depends,
            "file_name": self.file_name,
            "imports": self.imports,
            "install_dir": "site",
            "name": self.name,
            "package_type": "package",
            "sha256": self.sha256,
            "unvendored_tests": False,
            "version": self.version,
        }


def get_pypi_packages():
    return [
        Package(name="param", version="2.2.1", imports=["param"]),
        Package(name="psygnal", version="0.15.0", imports=["psygnal"]),
        Package(
            name="anywidget",
            version="0.9.18",
            imports=["anywidget"],
            depends=["psygnal"],
        ),
        Package(
            name="plotly",
            version="6.3.1",
            imports=["plotly"],
            depends=["anywidget", "numpy", "pandas", "narwhals", "nbformat"],
        ),
        Package(
            name="narwhals",
            version="2.8.0",
            imports=["narwhals"],
        ),
        Package(
            name="nbformat",
            version="5.10.4",
            imports=["nbformat"],
            depends=[
                "fastjsonschema",
                "jsonschema",
                "attrs",
                "referencing",
                "jsonschema_specifications",
            ],
        ),
        Package(
            name="ipywidgets",
            version="8.1.7",
            imports=["ipywidgets"],
            depends=["jupyterlab-widgets"],
        ),
        Package(
            name="ipycanvas",
            version="0.14.1",
            imports=["ipycanvas"],
            depends=["numpy", "ipywidgets", "pillow"],
        ),
        Package(name="pythreejs", version="2.4.2", imports=["pythreejs"], depends=[]),
        Package(
            name="ipydatawidgets",
            version="4.3.5",
            imports=["ipydatawidgets"],
            depends=["ipywidgets"],
        ),
        Package(
            name="jupyterlab-widgets", version="3.0.15", imports=["jupyterlab_widgets"]
        ),
        Package(
            name="panel",
            version="1.8.2",
            imports=["panel"],
            depends=["bokeh", "param", "pyviz-comms"],
        ),
        Package(
            name="pyviz-comms",
            version="3.0.6",
            imports=["pyviz_comms"],
        ),
        Package(
            name="holoviews",
            version="1.21.0",
            imports=["holoviews"],
            depends=["panel", "pyparsing", "narwhals", "tqdm"],
        ),
        Package(
            name="hvplot",
            version="0.12.1",
            imports=["hvplot"],
            depends=["holoviews", "pandas", "colorcet"],
        ),
        Package(name="colorcet", version="3.1.0", imports=["colorcet"]),
        Package(
            name="openpyxl",
            version="3.1.5",
            imports=["openpyxl"],
            depends=["et-xmlfile"],
        ),
        Package(name="et-xmlfile", version="2.0.0", imports=["et_xmlfile"]),
        Package(
            name="altair",
            version="5.5.0",
            imports=["altair"],
            depends=[
                "typing-extensions",
                "jinja2",
                "jsonschema",
                "packaging",
                "narwhals",
            ],
        ),
        Package(
            name="bokeh",
            version="3.8.0",
            depends=[
                "contourpy",
                "numpy",
                "jinja2",
                "pandas",
                "pillow",
                "python-dateutil",
                "six",
                "typing-extensions",
                "pyyaml",
                "xyzservices",
            ],
            imports=["bokeh"],
        ),
        Package(
            name="sympy",
            version="1.14.0",
            imports=["sympy"],
            depends=["mpmath"],
        ),
        Package(
            name="geoviews",
            version="1.14.1",
            imports=["geoviews"],
            depends=[
                "shapely",
                "pyproj",
                "certifi",
                "cartopy",
                "pyshp",
                "geos",
                "cycler",
                "fonttools",
                "kiwisolver",
            ],
        ),
        Package(
            name="ipyevents",
            version="2.0.4",
            imports=["ipyevents"],
        ),
        Package(
            name="fastjsonschema",
            version="2.21.2",
            imports=["fastjsonschema"],
        )
    ]


def get_local_packages():
    return [
        Package(
            name="z3",
            version="4.14.2.0",
            imports=["z3"],
            file_name="z3-4.14.2.0-py3-none-pyodide_2024_0_wasm32.whl",
        ),
        # Package(
        #     name="polars",
        #     version="1.33.1",
        #     imports=["polars"],
        #     file_name="polars-1.33.1-cp39-abi3-emscripten_4_0_14_wasm32.whl",
        #     depends=["numpy", "pyarrow", "openpyxl"],
        # ),
        Package(
            name="matplotlib",
            version="3.8.4",
            imports=["pylab", "mpl_toolkits", "matplotlib"],
            depends=[
                "contourpy",
                "cycler",
                "fonttools",
                "kiwisolver",
                "numpy",
                "packaging",
                "pillow",
                "pyparsing",
                "python-dateutil",
                "pytz",
                "matplotlib-pyodide",
            ],
            file_name="matplotlib-3.8.4-cp312-cp312-pyodide_2024_0_wasm32.whl",
        ),
        Package(
            name="helper",
            version="1.0.0",
            imports=["helper"],
            file_name="helper-1.0.0-py3-none-any.whl",
        ),
    ]


def patch_pyodide_lock_file_names():
    with open(PYODIDE_LOCK_FILE) as f:
        data = json.load(f)

    for name, info in data["packages"].items():
        file_name = info["file_name"]
        if not file_name.startswith("https://"):
            info["file_name"] = (
                f"https://cdn.jsdelivr.net/pyodide/{PYODIDE_VERSION}/full/{file_name}"
            )

    for json_name in ["pypi", "local"]:
        extra_packages_file_name = Path(f"./{json_name}_packages.json")
        if extra_packages_file_name.exists():
            with open(extra_packages_file_name, "r", encoding="utf-8") as f:
                packages = json.load(f)
                data["packages"].update(packages)

    data["packages"]["polars"]["depends"] = ["numpy", "pyarrow", "openpyxl"]

    with open(PYODIDE_LOCK_FILE, "w") as f:
        json.dump(data, f, indent=4)


def create_pypi_packages():
    packages = {}
    for pack in get_pypi_packages():
        packages[pack.name] = pack.json

    with open("./pypi_packages.json", "w", encoding="utf-8") as f:
        json.dump(packages, f, indent=4)


def create_local_packages():
    packages = {}
    for pack in get_local_packages():
        packages[pack.name] = pack.json

    with open("./local_packages.json", "w", encoding="utf-8") as f:
        json.dump(packages, f, indent=4)


if __name__ == "__main__":
    import sys

    if sys.argv[1] == "patch":
        for folder in PACKAGE_FOLDER.iterdir():
            if folder.is_dir():
                print(f"make whl: {folder}")
                make_wheel(folder, folder.name, "1.0.0", target_dir=WHL_PACKAGE_FOLDER)

        print("create local packages")
        create_local_packages()

        print("patch pyodide_lock.json")
        patch_pyodide_lock_file_names()
        for src_fn in WHL_PACKAGE_FOLDER.glob("*.whl"):
            dst_fn = PYODIDE_FOLDER / src_fn.name
            print(f"copy {src_fn} to {dst_fn}")
            shutil.copy(src_fn, dst_fn)

    elif sys.argv[1] == "create":
        print("create extra packages")
        create_pypi_packages()

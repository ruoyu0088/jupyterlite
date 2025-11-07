import nbformat
from bs4 import BeautifulSoup, Tag
from markdownify import markdownify


def split_interactive_code(code: str):
    """Split >>> style code into blocks when an output appears."""
    lines = code.splitlines()
    blocks = []
    current = []

    for line in lines:
        stripped = line.strip()
        if stripped.startswith(">>>"):
            # new command
            current.append(stripped[4:])
        elif stripped.startswith("..."):
            current.append(stripped[4:])
        elif stripped == "":
            continue
        else:
            # output line => split here
            if current:
                blocks.append("\n".join(current))
                current = []
    if current:
        blocks.append("\n".join(current))
    return blocks


def sphinx_html_to_notebook(html: str, output_path: str):
    soup = BeautifulSoup(html, "html.parser")
    nb = nbformat.v4.new_notebook()
    cells = []

    def process_section(section: Tag):
        markdown_parts = []

        for child in section.children:
            if not isinstance(child, Tag):
                continue
            if child.name == "section":
                continue

            # detect code
            highlight_div = child.select_one("div.highlight > pre")
            if highlight_div:
                # flush markdown
                if markdown_parts:
                    md = markdownify("".join(str(x) for x in markdown_parts), heading_style="ATX")
                    if md.strip():
                        cells.append(nbformat.v4.new_markdown_cell(md))
                    markdown_parts.clear()

                code = highlight_div.get_text()

                if ">>>" in code:
                    blocks = split_interactive_code(code)
                    for b in blocks:
                        b = b.strip()
                        if b:
                            cells.append(nbformat.v4.new_code_cell(b))
                else:
                    code = code.strip()
                    if code:
                        cells.append(nbformat.v4.new_code_cell(code))
            else:
                markdown_parts.append(str(child))

        if markdown_parts:
            md = markdownify("".join(str(x) for x in markdown_parts), heading_style="ATX")
            if md.strip():
                cells.append(nbformat.v4.new_markdown_cell(md))

    # process all sections (recursively)
    for section in soup.find_all("section", recursive=True):
        process_section(section)

    nb.cells = cells
    with open(output_path, "w", encoding="utf-8") as f:
        nbformat.write(nb, f)


def convert_ui():
    import ipywidgets as widgets

    text_html = widgets.Textarea(placeholder="Paste HTML here")
    name = widgets.Text(description="name", value="demo")
    convert_button = widgets.Button(description="Convert")

    def convert(b):
        html = text_html.value
        sphinx_html_to_notebook(html, f'{name.value}.ipynb')

    convert_button.on_click(convert)
    return widgets.VBox([text_html, name, convert_button])
"""Export saved notebook narrative and results to readable HTML without execution."""

import os
from pathlib import Path

from execute_notebook import add_local_jupyter_deps


def strip_css_comments(css):
    import tinycss2

    def clean(tokens):
        kept = []
        for token in tokens:
            if token.type == "comment" and not any(
                marker in token.value.lower() for marker in ("copyright", "license", "spdx")
            ):
                continue
            for attribute in ("prelude", "content", "arguments"):
                nested = getattr(token, attribute, None)
                if isinstance(nested, list):
                    setattr(token, attribute, clean(nested))
            kept.append(token)
        return kept

    return tinycss2.serialize(clean(tinycss2.parse_stylesheet(css)))


def main():
    deps = add_local_jupyter_deps(Path.cwd())
    data = deps / "share" / "jupyter"
    if data.is_dir():
        paths = [str(data.resolve())]
        if os.environ.get("JUPYTER_PATH"):
            paths.append(os.environ["JUPYTER_PATH"])
        os.environ["JUPYTER_PATH"] = os.pathsep.join(paths)
    import nbformat
    from bs4 import BeautifulSoup, Comment
    from nbconvert import HTMLExporter

    path = Path("Climate_ODER_Verification.ipynb")
    notebook = nbformat.read(path, as_version=4)
    exporter = HTMLExporter(template_name="lab", exclude_input=True)
    html, _ = exporter.from_notebook_node(notebook)
    document = BeautifulSoup(html, "html.parser")
    # These outputs are static tables and prose; no JavaScript is required.
    for script in document.find_all("script"):
        script.decompose()
    for comment in document.find_all(string=lambda value: isinstance(value, Comment)):
        comment.extract()
    # Preserve upstream license notices and CSS strings while removing template notes.
    for style in document.find_all("style"):
        if style.string is not None:
            style.string.replace_with(strip_css_comments(str(style.string)))
    document.title.string = "Climate ODER Computational Supplement"
    path.with_suffix(".html").write_text(str(document), encoding="utf-8")
    print("wrote", path.with_suffix(".html"))


if __name__ == "__main__":
    main()

"""Execute the supplement notebook through a fresh Jupyter kernel."""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path


def add_local_jupyter_deps(root):
    deps = root / ".jupyter_deps"
    if deps.exists():
        sys.path.insert(0, str(deps.resolve()))
    return deps


def write_local_kernel(root, python_exe, deps):
    kernel_dir = root / ".jupyter_data" / "kernels" / "climate-oder-supplement"
    kernel_dir.mkdir(parents=True, exist_ok=True)
    existing_pythonpath = os.environ.get("PYTHONPATH", "")
    paths = [str(root.resolve())]
    if deps.exists():
        paths.insert(0, str(deps.resolve()))
    if existing_pythonpath:
        paths.append(existing_pythonpath)
    kernel = {
        "argv": [str(Path(python_exe).resolve()), "-m", "ipykernel_launcher", "-f", "{connection_file}"],
        "display_name": "Climate ODER Supplement",
        "language": "python",
        "env": {"PYTHONPATH": os.pathsep.join(paths)},
    }
    (kernel_dir / "kernel.json").write_text(json.dumps(kernel, indent=2), encoding="utf-8")
    return kernel_dir


def execute_notebook(path):
    from oder_supplement import __version__

    root = Path.cwd()
    deps = add_local_jupyter_deps(root)
    from nbclient.client import NotebookClient
    import nbformat

    write_local_kernel(root, sys.executable, deps)
    os.environ["JUPYTER_PATH"] = str((root / ".jupyter_data").resolve())

    notebook_path = Path(path)
    nb = nbformat.read(notebook_path, as_version=4)
    nb.metadata.pop("source_manuscript", None)
    for cell in nb.cells:
        cell.metadata.pop("execution", None)
    client = NotebookClient(
        nb,
        timeout=120,
        kernel_name="climate-oder-supplement",
        resources={"metadata": {"path": str(root.resolve())}},
        allow_errors=False,
        record_timing=False,
    )
    client.execute()
    nb.metadata["supplement_version"] = __version__
    nbformat.write(nb, notebook_path)

    errors = [
        output
        for cell in nb.cells
        if cell.cell_type == "code"
        for output in cell.get("outputs", [])
        if output.get("output_type") == "error"
    ]
    if errors:
        raise RuntimeError(f"notebook contains {len(errors)} error outputs")
    code_cells = [cell for cell in nb.cells if cell.cell_type == "code"]
    unexecuted = [i + 1 for i, cell in enumerate(code_cells) if cell.get("execution_count") is None]
    if unexecuted:
        raise RuntimeError(f"unexecuted code cells: {unexecuted}")
    return {"code_cells": len(code_cells), "error_outputs": len(errors)}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("notebook", nargs="?", default="Climate_ODER_Verification.ipynb")
    args = parser.parse_args()
    result = execute_notebook(args.notebook)
    print(f"executed {args.notebook}")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()

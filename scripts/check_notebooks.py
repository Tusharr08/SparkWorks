import json
import subprocess

def get_changed_files():
    result = subprocess.run(
        ["git", "diff", "--name-only", "origin/main...HEAD"],
        capture_output=True, text=True, check=False
    )
    return result.stdout.strip().splitlines()

def check_notebooks():
    errors = []
    changed = get_changed_files()

    for file in changed:
        if not file.endswith(".ipynb"):
            continue

        try:
            with open(file, "r", encoding="utf-8") as f:
                nb = json.load(f)
        except Exception:
            errors.append(f"Could not parse notebook JSON: {file}")
            continue

        # Rule 1: Must not contain credentials (simple keyword scan)
        bad_keywords = ["password", "secret", "key=", "token"]
        for cell in nb.get("cells", []):
            if cell.get("cell_type") == "code":
                src = " ".join(cell.get("source", []))
                for kw in bad_keywords:
                    if kw in src.lower():
                        errors.append(f"Notebook {file} contains forbidden keyword '{kw}'")

        # Rule 2: Must not use %run (avoid chaining notebooks)
        for cell in nb.get("cells", []):
            if cell.get("cell_type") == "code":
                for line in cell.get("source", []):
                    if line.strip().startswith("%run"):
                        errors.append(f"Notebook {file} uses forbidden '%run'")

        # Rule 3: Imports must be explicit (example rule: no wildcard imports)
        for cell in nb.get("cells", []):
            if cell.get("cell_type") == "code":
                for line in cell.get("source", []):
                    if "import *" in line:
                        errors.append(f"Notebook {file} uses wildcard import: {line.strip()}")

    return errors

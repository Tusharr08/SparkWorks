import re
import subprocess

def get_changed_files():
    """Get list of changed files in PR branch vs main."""
    result = subprocess.run(
        ["git", "diff", "--name-only", "origin/main...HEAD"],
        capture_output=True, text=True, check=False
    )
    return result.stdout.strip().splitlines()

def check_naming():
    errors = []
    changed = get_changed_files()

    for file in changed:
        fname = file.split("/")[-1]

        # Notebook check -> nb_<3 letters>_<desc>.ipynb
        if fname.endswith(".ipynb"):
            if not re.match(r"^nb_[a-z]{3}_.+\.ipynb$", fname):
                errors.append(
                    f"Invalid notebook name: {file} (expected nb_<3-letter>_<desc>.ipynb)"
                )

        # Job check -> jb_<3 letters>_<desc>.(py|yml|yaml)
        elif fname.endswith((".yml", ".yaml", ".py")):
            if not re.match(r"^jb_[a-z]{3}_.+\.(py|yml|yaml)$", fname):
                errors.append(
                    f"Invalid job file name: {file} (expected jb_<3-letter>_<desc>.(py|yml|yaml))"
                )
    return errors

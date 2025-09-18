import sys
from check_naming import check_naming
from check_notebooks import check_notebooks
from check_jobs import check_jobs

def main():
    errors = []
    errors += check_naming()
    errors += check_notebooks()
    errors += check_jobs()

    if errors:
        print("❌ Compliance check failed:")
        for e in errors:
            print("   -", e)
        sys.exit(1)
    else:
        print("✅ All compliance checks passed!")

if __name__ == "__main__":
    main()

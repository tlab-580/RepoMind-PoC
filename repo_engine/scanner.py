from pathlib import Path


SUPPORTED_EXTENSIONS = {
    ".py",
    ".js",
    ".jsx",
    ".ts",
    ".tsx",
    ".java",
    ".cpp",
    ".c",
    ".h",
    ".html",
    ".css",
    ".json",
    ".pkl",
    ".joblib",
}


IGNORED_DIRECTORIES = {
    ".git",
    "node_modules",
    "venv",
    "__pycache__",
    ".next",
    "dist",
    "build",
}


def scan_repository(repo_path: str):

    repo = Path(repo_path)

    files = []

    for path in repo.rglob("*"):

        if not path.is_file():
            continue

        if any(
            ignored in path.parts
            for ignored in IGNORED_DIRECTORIES
        ):
            continue

        if path.suffix.lower() not in SUPPORTED_EXTENSIONS:
            continue

        relative_path = path.relative_to(repo)

        files.append(
            {
                "path": str(relative_path),
                "extension": path.suffix.lower(),
            }
        )

    return files


if __name__ == "__main__":

    repository = input(
        "Enter repository path: "
    ).strip()

    results = scan_repository(repository)

    print("\nRepoMind Scanner")
    print("=" * 50)

    print(
        f"Files found: {len(results)}"
    )

    for file_data in results:

        print(
            f"📄 {file_data['path']}"
        )
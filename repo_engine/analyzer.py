from pathlib import Path

from repo_engine.scanner import scan_repository
from repo_engine.parser import parse_python_file
from repo_engine.graph import (
    build_code_graph,
    print_code_graph,
    find_related_files
)


def analyze_repository(repo_path: str):
    """
    Analyze supported files in a repository.
    """

    root = Path(repo_path)

    all_files = scan_repository(repo_path)

    repository_data = []

    for file_data in all_files:

        relative_path = file_data["path"]

        full_path = root / relative_path

        extension = file_data["extension"]

        # ---------------------------------------------
        # Python analysis
        # ---------------------------------------------

        if extension == ".py":

            try:

                parsed_data = parse_python_file(
                    str(full_path)
                )

                parsed_data["relative_path"] = str(
                    relative_path
                )

                parsed_data["file_type"] = "python"

                parsed_data["source_code"] = full_path.read_text(
                    encoding="utf-8",
                    errors="ignore"
                )

                repository_data.append(
                    parsed_data
                 )  

            except Exception as error:

                print(
                    f"Could not parse "
                    f"{relative_path}: {error}"
                )

        # ---------------------------------------------
        # JavaScript / JSX analysis
        # ---------------------------------------------

        elif extension in {
            ".js",
            ".jsx",
            ".ts",
            ".tsx"
        }:

            try:

                source_code = full_path.read_text(
                    encoding="utf-8",
                    errors="ignore"
                )

                repository_data.append(
                    {
                        "relative_path": str(
                            relative_path
                        ),
                        "file_type": "javascript",
                        "source_code": source_code,
                        "imports": [],
                        "functions": [],
                        "classes": [],
                        "calls": []
                    }
                )

            except Exception as error:

                print(
                    f"Could not read "
                    f"{relative_path}: {error}"
                )
                    # ---------------------------------------------
        # ML model files
        # ---------------------------------------------

                # ---------------------------------------------
        # ML model files
        # ---------------------------------------------

        elif extension in {
            ".pkl",
            ".joblib"
        }:

            repository_data.append(
                {
                    "relative_path": str(
                        relative_path
                    ),
                    "file_type": "model",
                    "source_code": "",
                    "imports": [],
                    "functions": [],
                    "classes": [],
                    "calls": []
                }
            )

    return repository_data


if __name__ == "__main__":

    repository = input(
        "Enter repository path: "
    ).strip()

    try:

        results = analyze_repository(
            repository
        )

        print(
            "\nRepoMind Repository Analyzer"
        )

        print(
            "=" * 50
        )

        print(
            f"\nFiles analyzed: {len(results)}"
        )

        python_count = sum(
            1
            for file in results
            if file["file_type"] == "python"
        )

        javascript_count = sum(
            1
            for file in results
            if file["file_type"] == "javascript"
        )

        model_count = sum(
            1
            for file in results
            if file["file_type"] == "model"
        )

        print(
            f"Python files: {python_count}"
        )

        print(
            f"JavaScript/JSX files: "
            f"{javascript_count}"
        )

        print(
            f"ML model files: {model_count}"
        )

        for file in results:

            print(
                f"\n📄 {file['relative_path']}"
            )

            if file["file_type"] == "python":

                print(
                    f"   Imports: "
                    f"{len(file['imports'])}"
                )

                print(
                    f"   Functions: "
                    f"{len(file['functions'])}"
                )

                print(
                    f"   Classes: "
                    f"{len(file['classes'])}"
                )

                print(
                    f"   Calls: "
                    f"{len(file['calls'])}"
                )

            elif file["file_type"] == "javascript":

                print(
                    "   Type: JavaScript/JSX"
                )

            elif file["file_type"] == "model":

                print(
                    "   Type: ML Model"
                )

        graph = build_code_graph(
            results
        )

        print_code_graph(
            graph
        )

        print(
            "\nRelated Files"
        )

        print(
            "=" * 50
        )

        for file in results:

            file_path = file[
                "relative_path"
            ]

            related = find_related_files(
                graph,
                file_path
            )

            if related:

                print(
                    f"\n📄 {file_path}"
                )

                for item in related:

                    print(
                        f"   → "
                        f"{item['relationship']}: "
                        f"{item['file']}"
                    )

    except Exception as error:

        print(
            f"\nError: {error}"
        )
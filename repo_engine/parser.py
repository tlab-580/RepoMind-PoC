import ast
from pathlib import Path


def parse_python_file(file_path: str):
    """
    Parse a Python file and extract:
    - imports
    - functions
    - classes
    - function calls
    """

    path = Path(file_path)

    if not path.exists():
        raise FileNotFoundError(
            f"File not found: {file_path}"
        )

    source_code = path.read_text(
        encoding="utf-8",
        errors="ignore"
    )

    tree = ast.parse(source_code)

    imports = []
    functions = []
    classes = []
    calls = []

    for node in ast.walk(tree):

        # Imports
        if isinstance(node, ast.Import):

            for name in node.names:
                imports.append(name.name)

        elif isinstance(node, ast.ImportFrom):

            module = node.module or ""

            for name in node.names:
                imports.append(
                    f"{module}.{name.name}"
                )

        # Functions
        elif isinstance(node, ast.FunctionDef):

            functions.append({
                "name": node.name,
                "line": node.lineno,
            })

        # Classes
        elif isinstance(node, ast.ClassDef):

            classes.append({
                "name": node.name,
                "line": node.lineno,
            })

        # Function calls
        elif isinstance(node, ast.Call):

            if isinstance(node.func, ast.Name):

                calls.append({
                    "name": node.func.id,
                    "line": node.lineno,
                })

            elif isinstance(node.func, ast.Attribute):

                calls.append({
                    "name": node.func.attr,
                    "line": node.lineno,
                })

    return {
        "file": str(path),
        "imports": imports,
        "functions": functions,
        "classes": classes,
        "calls": calls,
    }


if __name__ == "__main__":

    file_path = input(
        "Enter Python file path: "
    ).strip()

    try:

        result = parse_python_file(file_path)

        print("\nRepoMind Code Parser")
        print("=" * 40)

        print("\nImports:")
        for item in result["imports"]:
            print(f"  - {item}")

        print("\nFunctions:")
        for item in result["functions"]:
            print(
                f"  - {item['name']} "
                f"(line {item['line']})"
            )

        print("\nClasses:")
        for item in result["classes"]:
            print(
                f"  - {item['name']} "
                f"(line {item['line']})"
            )

        print("\nFunction Calls:")
        for item in result["calls"]:
            print(
                f"  - {item['name']} "
                f"(line {item['line']})"
            )

    except Exception as error:

        print(f"\nError: {error}")
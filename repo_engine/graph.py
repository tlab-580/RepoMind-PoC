import re
import networkx as nx


def normalize_module_name(path):
    """
    Convert a repository file path into a Python-style module name.
    """

    path = path.replace("\\", "/")

    if path.endswith(".py"):
        path = path[:-3]

    return path.replace("/", ".")


def detect_api_calls(source_code):
    """
    Detect API endpoints referenced in JavaScript/JSX code.
    """

    endpoints = []

    patterns = [
        r"['\"](/predict-[^'\"]+)['\"]",
        r"`[^`]*(/predict-[^`]+)`",
    ]

    for pattern in patterns:

        matches = re.findall(
            pattern,
            source_code
        )

        for match in matches:

            if match not in endpoints:
                endpoints.append(match)

    return endpoints


def detect_model_paths(source_code):
    """
    Detect ML model filenames loaded by backend code.
    """

    model_paths = []

    patterns = [
        r"['\"]([^'\"]+\.pkl)['\"]",
        r"['\"]([^'\"]+\.joblib)['\"]",
    ]

    for pattern in patterns:

        matches = re.findall(
            pattern,
            source_code
        )

        for match in matches:

            if match not in model_paths:
                model_paths.append(match)

    return model_paths


def build_code_graph(repository_data):
    """
    Build a repository-level knowledge graph.

    Relationships:
        Python imports
        Frontend API calls
        Backend ML model loading
    """

    graph = nx.DiGraph()

    # --------------------------------------------------
    # 1. Add all repository files
    # --------------------------------------------------

    for file_data in repository_data:

        file_path = file_data["relative_path"]

        graph.add_node(
             file_path,
             file_type=file_data["file_type"],
             source_code=file_data.get("source_code", "")
         )

    # --------------------------------------------------
    # 2. Python module lookup
    # --------------------------------------------------

    module_lookup = {}

    for file_data in repository_data:

        if file_data["file_type"] != "python":
            continue

        file_path = file_data["relative_path"]

        module_name = normalize_module_name(
            file_path
        )

        module_lookup[module_name] = file_path

    # --------------------------------------------------
    # 3. Python import relationships
    # --------------------------------------------------

    for file_data in repository_data:

        if file_data["file_type"] != "python":
            continue

        source_file = file_data["relative_path"]

        for imported_module in file_data["imports"]:

            imported_module = imported_module.strip()

            for module_name, target_file in module_lookup.items():

                if (
                    imported_module == module_name
                    or imported_module.startswith(
                        module_name + "."
                    )
                ):

                    graph.add_edge(
                        source_file,
                        target_file,
                        relationship="imports"
                    )

    # --------------------------------------------------
    # 4. JavaScript API relationships
    # --------------------------------------------------

    for file_data in repository_data:

        if file_data["file_type"] != "javascript":
            continue

        source_file = file_data["relative_path"]

        source_code = file_data.get(
            "source_code",
            ""
        )

        endpoints = detect_api_calls(
            source_code
        )

        for endpoint in endpoints:

            if endpoint == "/predict-risk":

                backend_file = None

                for candidate in repository_data:

                    candidate_path = (
                        candidate["relative_path"]
                        .replace("\\", "/")
                    )

                    if candidate_path == "backend/main.py":

                        backend_file = (
                            candidate["relative_path"]
                        )

                        break

                if backend_file:

                    graph.add_edge(
                        source_file,
                        backend_file,
                        relationship="calls_api",
                        endpoint=endpoint
                    )

    # --------------------------------------------------
    # 5. Backend → ML model relationships
    # --------------------------------------------------

    for file_data in repository_data:

        if file_data["file_type"] != "python":
            continue

        source_file = file_data["relative_path"]

        if (
            source_file.replace("\\", "/")
            != "backend/main.py"
        ):
            continue

        source_code = file_data.get(
            "source_code",
            ""
        )

        model_paths = detect_model_paths(
            source_code
        )

        for model_path in model_paths:

            normalized_model_path = (
                model_path
                .replace("\\", "/")
            )

            for candidate in repository_data:

                candidate_path = (
                    candidate["relative_path"]
                    .replace("\\", "/")
                )

                if candidate_path.endswith(
                    normalized_model_path
                ):

                    graph.add_edge(
                        source_file,
                        candidate["relative_path"],
                        relationship="loads_model"
                    )

    return graph


def print_code_graph(graph):
    """
    Print the repository knowledge graph.
    """

    print("\nRepoMind Code Knowledge Graph")
    print("=" * 50)

    print(
        f"Nodes: {graph.number_of_nodes()}"
    )

    print(
        f"Relationships: {graph.number_of_edges()}"
    )

    print("\nFiles:")

    for node in graph.nodes:

        print(
            f"  📄 {node}"
        )

    print("\nRelationships:")

    if graph.number_of_edges() == 0:

        print(
            "  No file relationships detected."
        )

    else:

        for source, target, data in graph.edges(
            data=True
        ):

            relationship = data[
                "relationship"
            ]

            if "endpoint" in data:

                print(
                    f"  {source} "
                    f"--[{relationship}: "
                    f"{data['endpoint']}]--> "
                    f"{target}"
                )

            else:

                print(
                    f"  {source} "
                    f"--[{relationship}]--> "
                    f"{target}"
                )
def find_related_files(graph, file_path):
    """
    Find files directly connected to a given repository file.
    """

    related = []

    if file_path not in graph:
        return related

    for source, target, data in graph.edges(
        data=True
    ):

        if source == file_path:

            related.append(
                {
                    "file": target,
                    "relationship": data.get(
                        "relationship"
                    )
                }
            )

        elif target == file_path:

            related.append(
                {
                    "file": source,
                    "relationship": data.get(
                        "relationship"
                    )
                }
            )

    return related
def detect_api_mismatches(graph):

    mismatches = []

    backend_routes = []

    # Find all backend API routes
    for node, data in graph.nodes(data=True):

        source_code = data.get(
            "source_code",
            ""
        )

        if not source_code:
            continue

        routes = re.findall(
            r'@app\.(?:get|post|put|delete|patch)\(["\']([^"\']+)',
            source_code
        )

        if routes:

            backend_routes.append(
                {
                    "file": node,
                    "routes": routes,
                }
            )

    # Find API calls made by frontend files
    for node, data in graph.nodes(data=True):

        source_code = data.get(
            "source_code",
            ""
        )

        if not source_code:
            continue

        if not node.lower().endswith(
            (".js", ".jsx", ".ts", ".tsx")
        ):
            continue

        api_calls = re.findall(
            r'VITE_API_URL\}(/[^"`\']+)',
            source_code
        )

        for api_path in api_calls:

            if not api_path.startswith("/"):
                continue

            matched = False

            for backend in backend_routes:

                if api_path in backend["routes"]:

                    matched = True

            if not matched:

                mismatches.append(
                    {
                        "frontend": node,
                        "called_api": api_path,
                        "backend_routes": backend_routes,
                    }
                )

    return mismatches
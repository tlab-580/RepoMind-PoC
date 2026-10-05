from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from pathlib import Path
import sys
import shutil
import subprocess
import tempfile
from urllib.parse import urlparse

# Allow imports from the RepoMind project root
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from ai.agent import RepoMindAgent


app = FastAPI(
    title="RepoMind API",
    description="Repository-level AI coding agent",
    version="1.0.0",
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173","https://repo-mind-po-pjwhwj7mn-tad10.vercel.app",],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class AnalyzeRequest(BaseModel):
    repository: str
    query: str


@app.get("/")
def root():
    return {
        "name": "RepoMind",
        "status": "running",
        "description": "Repository-level AI coding agent",
    }


@app.get("/health")
def health():
    return {
        "status": "healthy",
        "service": "RepoMind API",
    }



@app.post("/analyze")
def analyze(request: AnalyzeRequest):
    repository = request.repository.strip()
    query = request.query.strip()

    if not repository or not query:
        return {
            "success": False,
            "error": "Repository and query are required.",
        }

    original_repository = repository

    try:
        # ---------------------------------------------------------
        # Resolve repository
        # ---------------------------------------------------------
        if repository.startswith(("https://", "http://")):
            parsed = urlparse(repository)

            # Accept only ordinary public GitHub repository URLs.
            if (
                parsed.scheme != "https"
                or parsed.hostname != "github.com"
                or parsed.port not in (None, 443)
                or parsed.username
                or parsed.password
                or parsed.query
                or parsed.fragment
            ):
                return {
                    "success": False,
                    "error": "Use a valid HTTPS URL for a public GitHub repository.",
                }

            parts = parsed.path.strip("/").split("/")

            if (
                len(parts) != 2
                or not parts[0]
                or not parts[1]
                or parts[1].endswith(".git.git")
            ):
                return {
                    "success": False,
                    "error": (
                        "Enter a GitHub URL in the format "
                        "https://github.com/owner/repository"
                    ),
                }

            owner, repo_name = parts

            if repo_name.endswith(".git"):
                repo_name = repo_name[:-4]

            import re

            if not all(
                re.fullmatch(r"[A-Za-z0-9_.-]+", part)
                for part in (owner, repo_name)
            ):
                return {
                    "success": False,
                    "error": "Invalid GitHub repository URL.",
                }

            clone_url = f"https://github.com/{owner}/{repo_name}.git"

            # Keep the temporary repository alive for the entire
            # analysis operation.
            with tempfile.TemporaryDirectory(prefix="repomind-") as temp_dir:
                repo_path = Path(temp_dir) / "repository"

                # Clone only the latest commit.
                subprocess.run(
                    [
                        "git",
                        "clone",
                        "--depth",
                        "1",
                        "--single-branch",
                        clone_url,
                        str(repo_path),
                    ],
                    check=True,
                    capture_output=True,
                    text=True,
                    timeout=90,
                )

                # Analyze while the temporary clone still exists.
                agent = RepoMindAgent(str(repo_path))

                results = agent.search(query)
                mismatches = agent.api_mismatches
                memory_results = agent.search_memory(query)

                relationships = []

                for file_path in agent.graph.nodes:
                    for target in agent.graph.successors(file_path):
                        edge_data = agent.graph.get_edge_data(
                            file_path,
                            target,
                        )

                        if edge_data:
                            relationships.append(
                                {
                                    "source": str(file_path),
                                    "target": str(target),
                                    "relationship": edge_data.get(
                                        "relationship",
                                        "",
                                    ),
                                }
                            )

                return {
                    "success": True,
                    "repository": original_repository,
                    "query": query,
                    "files": [
                        {
                            "path": item["file"],
                            "score": round(item["score"], 4),
                            "related_files": item["related_files"],
                        }
                        for item in results[:5]
                    ],
                    "relationships": relationships,
                    "mismatches": mismatches,
                    "memory": memory_results,
                }

        else:
            # Retain support for paths available on the backend machine.
            repo_path = Path(repository).resolve()

            if not repo_path.is_dir():
                return {
                    "success": False,
                    "error": (
                        f"Repository directory not found: {repository}. "
                        "For a deployed repository, enter a public GitHub URL."
                    ),
                }

            agent = RepoMindAgent(str(repo_path))

            results = agent.search(query)
            mismatches = agent.api_mismatches
            memory_results = agent.search_memory(query)

            relationships = []

            for file_path in agent.graph.nodes:
                for target in agent.graph.successors(file_path):
                    edge_data = agent.graph.get_edge_data(
                        file_path,
                        target,
                    )

                    if edge_data:
                        relationships.append(
                            {
                                "source": str(file_path),
                                "target": str(target),
                                "relationship": edge_data.get(
                                    "relationship",
                                    "",
                                ),
                            }
                        )

            return {
                "success": True,
                "repository": original_repository,
                "query": query,
                "files": [
                    {
                        "path": item["file"],
                        "score": round(item["score"], 4),
                        "related_files": item["related_files"],
                    }
                    for item in results[:5]
                ],
                "relationships": relationships,
                "mismatches": mismatches,
                "memory": memory_results,
            }

    except subprocess.TimeoutExpired:
        return {
            "success": False,
            "error": "Cloning timed out. Try a smaller public repository.",
        }

    except subprocess.CalledProcessError:
        return {
            "success": False,
            "error": (
                "Could not clone the repository. Check that the GitHub "
                "URL is correct and the repository is public."
            ),
        }

    except Exception as e:
        return {
            "success": False,
            "error": str(e),
        }

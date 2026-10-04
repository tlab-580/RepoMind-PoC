from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from pathlib import Path
import sys

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

    repository = request.repository
    query = request.query

    repo_path = Path(repository)

    if not repo_path.exists():
        return {
            "success": False,
            "error": f"Repository not found: {repository}",
        }

    try:
        agent = RepoMindAgent(repository)

        # Repository-aware retrieval
        results = agent.search(query)

        # Detect API mismatches
        mismatches = agent.graph.detect_api_mismatches()

        # Previous debugging memory
        memory_results = agent.search_memory(query)

        relationships = []

        for file_path in agent.graph.graph.nodes:

            node_data = agent.graph.graph.nodes[file_path]

            for target in agent.graph.graph.successors(file_path):

                edge_data = agent.graph.graph.get_edge_data(
                    file_path,
                    target
                )

                if edge_data:

                    relationships.append({
                        "source": file_path,
                        "target": target,
                        "relationship": edge_data.get("relationship", "")
                    })

        return {
            "success": True,
            "repository": repository,
            "query": query,
            "files": [
                {
                    "path": path,
                    "score": round(score, 4)
                }
                for path, score in results[:5]
            ],
            "relationships": relationships,
            "mismatches": mismatches,
            "memory": memory_results,
        }

    except Exception as e:

        return {
            "success": False,
            "error": str(e),
        }
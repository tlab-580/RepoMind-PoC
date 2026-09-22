from pathlib import Path

from rank_bm25 import BM25Okapi

from repo_engine.scanner import scan_repository


class RepositoryRetriever:

    def __init__(self, repo_path: str):

        self.repo_path = Path(repo_path)

        self.documents = []

        self._build_index()

    def _build_index(self):

        files = scan_repository(
            str(self.repo_path)
        )

        for file_data in files:

            relative_path = file_data["path"]

            full_path = (
                self.repo_path / relative_path
            )

            try:

                source_code = full_path.read_text(
                    encoding="utf-8",
                    errors="ignore"
                )

            except Exception:

                continue

            self.documents.append(
                {
                    "path": relative_path,
                    "content": source_code
                }
            )

        tokenized_documents = []

        for document in self.documents:

            text = (
                document["path"]
                + " "
                + document["content"]
            )

            tokenized_documents.append(
                text.lower().split()
            )

        self.bm25 = BM25Okapi(
            tokenized_documents
        )

    def search(
        self,
        query: str,
        top_k: int = 5
    ):

        query_tokens = query.lower().split()

        scores = self.bm25.get_scores(
            query_tokens
        )

        ranked_indices = sorted(
            range(len(scores)),
            key=lambda index: scores[index],
            reverse=True
        )

        results = []

        for index in ranked_indices[:top_k]:

            document = self.documents[index]

            results.append(
                {
                    "path": document["path"],
                    "score": float(
                        scores[index]
                    ),
                    "content": document["content"]
                }
            )

        return results

    def get_relevant_snippets(
        self,
        content: str,
        query: str,
        max_snippets: int = 3
    ):

        lines = content.splitlines()

        query_terms = [
            term
            for term in query.lower().split()
            if len(term) >= 4
        ]

        matched_snippets = []

        for line_number, line in enumerate(
            lines,
            start=1
        ):

            line_lower = line.lower()

            # Ignore comments when selecting
            # the most relevant executable code.
            is_comment = (
                line_lower.strip().startswith("//")
                or line_lower.strip().startswith("#")
                or line_lower.strip().startswith("/*")
                or line_lower.strip().startswith("*")
            )

            if is_comment:
                continue

            if any(
                term in line_lower
                for term in query_terms
            ):

                start = max(
                    0,
                    line_number - 3
                )

                end = min(
                    len(lines),
                    line_number + 2
                )

                snippet = []

                for number in range(
                    start,
                    end
                ):

                    snippet.append(
                        {
                            "line": number + 1,
                            "content": lines[number]
                        }
                    )

                matched_snippets.append(
                    {
                        "start": start + 1,
                        "end": end,
                        "lines": snippet
                    }
                )

                if len(
                    matched_snippets
                ) >= max_snippets:

                    break

        return matched_snippets


if __name__ == "__main__":

    repository = input(
        "Enter repository path: "
    ).strip()

    retriever = RepositoryRetriever(
        repository
    )

    query = input(
        "Enter search query: "
    ).strip()

    results = retriever.search(
        query,
        top_k=3
    )

    print(
        "\nRepoMind Repository Search"
    )

    print(
        "=" * 50
    )

    for result in results:

        print(
            f"\n📄 {result['path']}"
        )

        print(
            f"Score: {result['score']:.4f}"
        )

        snippets = (
            retriever.get_relevant_snippets(
                result["content"],
                query
            )
        )

        for snippet in snippets:

            print(
                f"\nLines "
                f"{snippet['start']}-"
                f"{snippet['end']}:"
            )

            for line in snippet["lines"]:

                print(
                    f"{line['line']}: "
                    f"{line['content']}"
                )
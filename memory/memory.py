
import json
from pathlib import Path
from datetime import datetime


class RepoMemory:

    def __init__(self, memory_file="memory/repo_memory.json"):

        self.memory_file = Path(memory_file)

        self.memory_file.parent.mkdir(
            parents=True,
            exist_ok=True
        )

        if self.memory_file.exists():

            try:

                with open(
                    self.memory_file,
                    "r",
                    encoding="utf-8"
                ) as file:

                    self.memories = json.load(file)

            except (json.JSONDecodeError, OSError):

                self.memories = []

        else:

            self.memories = []

    def add_memory(
        self,
        repository,
        problem,
        root_cause,
        fix
    ):

        # Prevent duplicate memories
        for existing in self.memories:

            if (
                existing.get("repository") == repository
                and existing.get("problem") == problem
                and existing.get("root_cause") == root_cause
                and existing.get("fix") == fix
            ):
                return False

        memory = {
            "timestamp": datetime.now().isoformat(
                timespec="seconds"
            ),
            "repository": repository,
            "problem": problem,
            "root_cause": root_cause,
            "fix": fix,
        }

        self.memories.append(memory)

        self._save()

        return True

    def search(self, query):

        query_words = set(
            query.lower().split()
        )

        results = []

        for memory in self.memories:

            searchable_text = " ".join(
                [
                    memory["problem"],
                    memory["root_cause"],
                    memory["fix"],
                ]
            ).lower()

            score = sum(
                word in searchable_text
                for word in query_words
            )

            if score > 0:

                results.append(
                    {
                        "score": score,
                        "memory": memory,
                    }
                )

        results.sort(
            key=lambda item: item["score"],
            reverse=True
        )

        return results

    def get_all(self):

        return self.memories

    def _save(self):

        with open(
            self.memory_file,
            "w",
            encoding="utf-8"
        ) as file:

            json.dump(
                self.memories,
                file,
                indent=2
            )


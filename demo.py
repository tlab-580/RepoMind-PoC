import subprocess
import sys

REPOSITORY = r"C:\Users\DELL\LANDGUARD-AI"

print("=" * 60)
print("🚀 RepoMind Hackathon Demo")
print("=" * 60)
print()
print("Repository:")
print(REPOSITORY)
print()
print("Starting RepoMind...")
print()

subprocess.run(
    [
        sys.executable,
        "-m",
        "ai.agent",
    ],
    input=f"{REPOSITORY}\nFix the API bug\n",
    text=True,
)

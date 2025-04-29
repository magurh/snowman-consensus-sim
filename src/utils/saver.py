import json
from pathlib import Path


def save_json(results: list[dict], filename: str) -> None:
    """Save results to a JSON file."""
    output_path = Path("outputs") / filename
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with Path.open(output_path, "w") as f:
        json.dump(results, f, indent=2)

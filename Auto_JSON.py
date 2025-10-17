import argparse
import os
from pathlib import Path
import sys
from typing import Optional

import requests

try:
    from config import get_data_dir
except ImportError:  # pragma: no cover - config should always be available
    get_data_dir = None  # type: ignore


DEFAULT_BASE_URL = "http://127.0.0.1:5001"
ANALYZE_ENDPOINT = f"{DEFAULT_BASE_URL}/api/analyze"
EXPORT_STATS_ENDPOINT = f"{DEFAULT_BASE_URL}/api/export_stats_json"
REQUEST_TIMEOUT = 30000


def normalize_folder_argument(folder_argument: str) -> str:
    """
    Convert a folder argument into the value expected by the analysis API.

    The web server resolves folders relative to its configured data directory,
    so we primarily need the terminal folder name (or nested relative path).
    """
    trimmed_argument = folder_argument.strip()
    if not trimmed_argument:
        raise ValueError("Folder argument cannot be empty.")

    folder_path = Path(trimmed_argument)

    # Try to normalise against the configured data directory when possible.
    if get_data_dir is not None:
        try:
            data_dir = Path(get_data_dir()).resolve()
        except Exception:
            data_dir = None
    else:
        data_dir = None

    if folder_path.exists():
        try:
            folder_path_resolved = folder_path.resolve()
            if data_dir and folder_path_resolved.is_relative_to(data_dir):
                relative_path = folder_path_resolved.relative_to(data_dir)
                folder_key = str(relative_path).replace("\\", "/")
            else:
                folder_key = folder_path.name
        except Exception:
            folder_key = folder_path.name
    else:
        folder_key = trimmed_argument.replace("\\", "/")

    folder_key = folder_key.strip("/\\")
    if not folder_key:
        raise ValueError(f"Could not determine a valid folder name from '{folder_argument}'.")

    return folder_key


def resolve_output_directory(folder_key: str, explicit_dir: Optional[str]) -> Path:
    """
    Determine where the statistics JSON should be written locally.
    """
    if explicit_dir:
        output_dir = Path(explicit_dir).expanduser().resolve()
    else:
        output_dir = None
        if get_data_dir is not None:
            try:
                data_dir = Path(get_data_dir()).resolve()
                candidate = (data_dir / folder_key).resolve()
                if candidate.is_dir():
                    output_dir = candidate
            except Exception:
                output_dir = None

        if output_dir is None:
            output_dir = Path.cwd()

    output_dir.mkdir(parents=True, exist_ok=True)
    return output_dir


def generate_statistics_json(
    folder_key: str,
    output_dir: Path,
    filename: Optional[str],
    timeout: int,
) -> Path:
    """
    Trigger analysis for the requested folder and download its statistics JSON.
    """
    analyze_payload = {"folder": folder_key}

    analyze_response = requests.post(ANALYZE_ENDPOINT, json=analyze_payload, timeout=timeout)
    if analyze_response.status_code != 200:
        raise RuntimeError(
            f"Analysis failed with status {analyze_response.status_code}: {analyze_response.text}"
        )

    target_name = filename or f"{Path(folder_key).name}_stats.json"
    if not target_name.lower().endswith(".json"):
        target_name += ".json"

    export_params = {"filename": target_name}
    export_response = requests.get(EXPORT_STATS_ENDPOINT, params=export_params, timeout=timeout)
    if export_response.status_code != 200:
        raise RuntimeError(
            f"JSON export failed with status {export_response.status_code}: {export_response.text}"
        )

    output_path = output_dir / target_name
    with open(output_path, "wb") as file_handle:
        file_handle.write(export_response.content)

    return output_path


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate only the statistics JSON for a given measurement folder."
    )
    parser.add_argument(
        "folder",
        help="Folder name or path containing measurement files (relative to the server's data directory).",
    )
    parser.add_argument(
        "--output-dir",
        help="Directory to store the downloaded JSON (defaults to the data/<folder> directory when available).",
    )
    parser.add_argument(
        "--filename",
        help="Optional output filename for the JSON. '.json' will be appended if missing.",
    )
    parser.add_argument(
        "--timeout",
        type=int,
        default=REQUEST_TIMEOUT,
        help=f"Timeout in seconds for each API request (default: {REQUEST_TIMEOUT}).",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_arguments()

    try:
        folder_key = normalize_folder_argument(args.folder)
        output_dir = resolve_output_directory(folder_key, args.output_dir)
        output_path = generate_statistics_json(
            folder_key=folder_key,
            output_dir=output_dir,
            filename=args.filename,
            timeout=args.timeout,
        )
        print(f"Statistics JSON saved to: {output_path}")
        return 0
    except Exception as exc:
        print(f"Error: {exc}")
        return 1


if __name__ == "__main__":
    sys.exit(main())


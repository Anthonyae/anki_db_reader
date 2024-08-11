# noqa: D100
import json
import os

__DATA_DIR = os.path.join(os.path.dirname(__file__), "data")


class UtilityFile:
    """Class for handling files."""

    def save_json(self, data_obj: dict, filename: str) -> None:
        """Saves dict to json filename."""
        filename = filename.replace(".json", "") + ".json"
        data_file_path = os.path.join(__DATA_DIR, filename)
        os.makedirs(os.path.dirname(data_file_path), exist_ok=True)

        with open(data_file_path, "w", encoding="utf-8") as f:
            json.dump(data_obj, f, indent=4)

    def open_json(self, filename: str, create_if_not_exits=False) -> dict:
        """Returns dict of given filename."""
        filename = str(filename).replace(".json", "") + ".json"
        data_file_path = os.path.join(__DATA_DIR, filename)

        try:
            with open(data_file_path, encoding="utf-8") as f:
                return json.load(f)
        except FileNotFoundError as e:
            if create_if_not_exits:
                os.makedirs(os.path.dirname(data_file_path), exist_ok=True)
                with open(data_file_path, "w", encoding="utf-8") as f:
                    json.dump({}, f, indent=4)
                return {}
            raise FileNotFoundError(
                f"File '{filename}' not found and create_if_not_exists is False."
            ) from e

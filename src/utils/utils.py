"""Utils file."""

import yaml
from pathlib import Path

__all__ = ['truthy_to_printable', 'clean_string', 'JUST_L_WIDTH', 'load_yaml']

JUST_L_WIDTH: int = 24
"""Left-justify characters"""

CONSOLE_DIVIDER: str = f"{'-' * 32}\n"


def truthy_to_printable(truthy: bool) -> str:

    """Return yes/no instead of True/False from a boolean."""
    return "Yes" if truthy else "No"


def clean_string(name: str) -> str:
    """Turn 'my_ship_name' into 'My Ship Name'."""
    msg = [s.capitalize() for s in name.split("_")]
    msg = " ".join(msg)

    return msg


def load_yaml(
        filename: str,
        *,
        safe_mode: bool = True,
) -> dict:
    filepath = Path(filename).resolve()
    loader = yaml.SafeLoader if safe_mode else yaml.FullLoader
    contents = yaml.load(filepath.read_text(), Loader=loader)
    return contents


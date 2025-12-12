from dataclasses import dataclass

from metacode.typing import Arguments


@dataclass
class ParsedComment:
    key: str
    command: str
    arguments: Arguments

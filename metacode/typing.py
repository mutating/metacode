from ast import AST
from typing import List, Optional, Union

# TODO: delete this catch blocks and "type: ignore" if minimum supported version of Python is > 3.9.
try:
    from typing import TypeAlias  # type: ignore[attr-defined, unused-ignore]
except ImportError:  # pragma: no cover
    from typing_extensions import TypeAlias

try:
    from types import EllipsisType  # type: ignore[attr-defined, unused-ignore]
except ImportError:  # pragma: no cover
    EllipsisType = type(...)  # type: ignore[misc, unused-ignore]


Argument: TypeAlias = Union[str, int, float, complex, bool, EllipsisType, AST]
Arguments: TypeAlias = List[Optional[Argument]]

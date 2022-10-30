from collections import defaultdict
from collections.abc import Callable
from typing import Union

from mypy.nodes import Node

from refurb.error import Error
from refurb.settings import Settings

Check = Union[
    Callable[[Node, list[Error]], None],
    Callable[[Node, list[Error], Settings], None],
]

Checks = defaultdict[type[Node], list[Check]]

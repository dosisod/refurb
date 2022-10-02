import os
import sys
from contextlib import suppress
from pathlib import Path
from subprocess import PIPE, run

from ._visitor_mappings import MAPPINGS

FILE_TEMPLATE = '''\
from dataclasses import dataclass

from {module} import {node}

from refurb.error import Error


@dataclass
class ErrorInfo(Error):
    """
    TODO: fill this in

    Bad:

    ```
    # TODO: fill this in
    ```

    Good:

    ```
    # TODO: fill this in
    ```
    """

    prefix = "XYZ"
    code = 999
    msg: str = "Your message here"


def check(node: {node}, errors: list[Error]) -> None:
    match node:
        case {node}():
            errors.append(ErrorInfo(node.line, node.column))
'''


def fzf(data: list[str] | None, args: list[str] = []) -> str:
    env = os.environ | {
        "SHELL": "/bin/bash",
        "FZF_DEFAULT_COMMAND": "find refurb -name '*.py' -not -path '*__*' 2> /dev/null || true",  # noqa: E501
    }

    process = run(
        ["fzf", "--height=20"] + args,
        env=env,
        stdout=PIPE,
        input=bytes("\n".join(data), "utf8") if data else None,
    )

    fzf_error_codes = (2, 130)

    if process.returncode in fzf_error_codes:
        sys.exit(1)

    return process.stdout[:-1].decode()


def folders_needing_init_file(path: Path) -> list[Path]:
    path = path.resolve()
    cwd = Path.cwd().resolve()

    if path.is_relative_to(cwd):
        to_remove = len(cwd.parents) + 1

        return [path, *list(path.parents)[:-to_remove]]

    return []


def main() -> None:
    nodes: dict[str, type] = {x.__name__: x for x in MAPPINGS.values()}

    selected = fzf(list(nodes.keys()))

    file = Path(
        fzf(
            None, args=["--print-query", "--query", "refurb/checks/"]
        ).splitlines()[0]
    )

    if file.suffix != ".py":
        print('refurb: File must end in ".py"')
        sys.exit(1)

    template = FILE_TEMPLATE.format(
        node=selected, module=nodes[selected].__module__
    )

    with suppress(FileExistsError):
        file.parent.mkdir(parents=True, exist_ok=True)

        for folder in folders_needing_init_file(file.parent):
            (folder / "__init__.py").touch(exist_ok=True)

    file.write_text(template)

    print(f"Generated {file}")


if __name__ == "__main__":
    main()

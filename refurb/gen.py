import os
import sys
from collections import defaultdict
from contextlib import suppress
from pathlib import Path
from subprocess import PIPE, run

from .error import ErrorCode
from .loader import get_error_class, get_modules
from .visitor import METHOD_NODE_MAPPINGS

FILE_TEMPLATE = '''\
from dataclasses import dataclass

{imports}

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

    prefix = "{prefix}"
    code = {id}
    msg: str = "Your message here"


def check(node: {accept_type}, errors: list[Error]) -> None:
    match node:
        case {pattern}:
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


def get_next_error_id(prefix: str) -> int:
    highest = 0

    for module in get_modules([]):
        if error := get_error_class(module):
            error_code = ErrorCode.from_error(error)

            if error_code.prefix == prefix:
                highest = max(highest, error_code.id + 1)

    return highest


NODES: dict[str, type] = {x.__name__: x for x in METHOD_NODE_MAPPINGS.values()}


def node_type_prompt() -> list[str]:
    return sorted(
        fzf(
            list(NODES.keys()), args=["--prompt", "type> ", "--multi"]
        ).splitlines()
    )


def filename_prompt() -> Path:
    return Path(
        fzf(
            None,
            args=[
                "--prompt",
                "filename> ",
                "--print-query",
                "--query",
                "refurb/checks/",
            ],
        ).splitlines()[0]
    )


def prefix_prompt() -> str:
    return fzf(
        [""], args=["--prompt", "prefix> ", "--print-query", "--query", "FURB"]
    )


def build_imports(names: list[str]) -> str:
    modules: defaultdict[str, list[str]] = defaultdict(list)

    for name in names:
        modules[NODES[name].__module__].append(name)

    return "\n".join(
        f"from {module} import {', '.join(names)}"
        for module, names in sorted(modules.items(), key=lambda x: x[0])
    )


def main() -> None:
    selected = node_type_prompt()
    file = filename_prompt()

    if file.suffix != ".py":
        print('refurb: File must end in ".py"')
        sys.exit(1)

    prefix = prefix_prompt()

    template = FILE_TEMPLATE.format(
        accept_type=" | ".join(selected),
        imports=build_imports(selected),
        prefix=prefix,
        id=get_next_error_id(prefix) or 100,
        pattern=" | ".join(f"{x}()" for x in selected),
    )

    with suppress(FileExistsError):
        file.parent.mkdir(parents=True, exist_ok=True)

        for folder in folders_needing_init_file(file.parent):
            (folder / "__init__.py").touch(exist_ok=True)

    file.write_text(template, "utf8")

    print(f"Generated {file}")


if __name__ == "__main__":
    main()

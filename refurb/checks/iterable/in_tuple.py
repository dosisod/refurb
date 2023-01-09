from dataclasses import dataclass

from mypy.nodes import ComparisonExpr, ForStmt, GeneratorExpr, ListExpr

from refurb.error import Error


@dataclass
class ErrorInfo(Error):
    """
    Since tuple, list, and set literals can be used with the `in` operator, it
    is best to pick one and stick with it.

    Bad:

    ```
    for x in [1, 2, 3]:
        pass

    nums = [str(x) for x in [1, 2, 3]]
    ```

    Good:

    ```
    for x in (1, 2, 3):
        pass

    nums = [str(x) for x in (1, 2, 3)]
    ```
    """

    # Currently this check is hard-coded for tuples, but once we have the
    # ability to pass parameters into checks this check will be able to work
    # with a variety of bracket types.
    name = "use-consistent-in-bracket"
    code = 109
    categories = ["iterable", "readability"]


def error_msg(oper: str) -> str:
    return f"Replace `{oper} [x, y, z]` with `{oper} (x, y, z)`"


def check(
    node: ComparisonExpr | ForStmt | GeneratorExpr, errors: list[Error]
) -> None:
    match node:
        case ComparisonExpr(
            operators=["in" | "not in" as oper],
            operands=[_, ListExpr() as expr],
        ):
            errors.append(ErrorInfo(expr.line, expr.column, error_msg(oper)))

        case ForStmt(expr=ListExpr() as expr):
            errors.append(ErrorInfo(expr.line, expr.column, error_msg("in")))

        case GeneratorExpr():
            for expr in node.sequences:  # type: ignore
                if isinstance(expr, ListExpr):
                    errors.append(
                        ErrorInfo(expr.line, expr.column, error_msg("in"))
                    )

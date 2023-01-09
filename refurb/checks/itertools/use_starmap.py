from dataclasses import dataclass

from mypy.nodes import ArgKind, CallExpr, GeneratorExpr, NameExpr, TupleExpr

from refurb.error import Error


@dataclass
class ErrorInfo(Error):
    """
    If you only want to iterate and unpack values so that you can pass them
    to a function (in the same order and with no modifications), you should
    use the more performant `starmap` function:

    Bad:

    ```
    scores = [85, 100, 60]
    passing_scores = [60, 80, 70]

    def passed_test(score: int, passing_score: int) -> bool:
        return score >= passing_score

    passed_all_tests = all(
        passed_test(score, passing_score)
        for score, passing_score
        in zip(scores, passing_scores)
    )
    ```

    Good:

    ```
    from itertools import starmap

    scores = [85, 100, 60]
    passing_scores = [60, 80, 70]

    def passed_test(score: int, passing_score: int) -> bool:
        return score >= passing_score

    passed_all_tests = all(starmap(passed_test, zip(scores, passing_scores)))
    ```
    """

    name = "use-starmap"
    code = 140
    msg: str = "Replace `f(...) for ... in x` with `starmap(f, x)`"
    categories = ["itertools", "performance"]


def check(node: GeneratorExpr, errors: list[Error]) -> None:
    match node:
        case GeneratorExpr(
            left_expr=CallExpr(args=args, arg_kinds=arg_kinds),
            indices=[TupleExpr(items=names)],
        ) if (
            names
            and len(names) == len(args)
            and all(kind == ArgKind.ARG_POS for kind in arg_kinds)
        ):
            for lhs, rhs in zip(args, names):
                if not (
                    isinstance(lhs, NameExpr)
                    and isinstance(rhs, NameExpr)
                    and lhs.name == rhs.name
                ):
                    return

            errors.append(ErrorInfo(node.line, node.column))

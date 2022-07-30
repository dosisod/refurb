from mypy.nodes import (
    CallExpr,
    IndexExpr,
    NameExpr,
    OpExpr,
    SliceExpr,
    StrExpr,
    TypeInfo,
    Var,
)

from refurb.error import Error


def slice_then_concat(node: OpExpr, errors: list[Error]) -> None:
    match node:
        case OpExpr(
            op="+",
            left=IndexExpr(
                base=CallExpr(
                    callee=NameExpr(name="str"),
                    args=[possibly_path],
                ),
                index=SliceExpr(begin_index=None),
            ),
            right=StrExpr(),
        ):
            match possibly_path:
                case CallExpr(
                    callee=NameExpr(node=TypeInfo() as ty),
                ) if ty.fullname == "pathlib.Path":
                    pass

                case NameExpr(node=Var(type=ty)) if str(ty) == "pathlib.Path":
                    pass

                case _:
                    return

            # TODO: create an error subclass for every error code
            errors.append(
                Error(
                    100,
                    node.line,
                    node.column,
                    "Use `Path(x).with_suffix(y)` instead of slice and concat",
                )
            )

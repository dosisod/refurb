from dataclasses import dataclass

from mypy.nodes import (
    AssignmentStmt,
    CallExpr,
    ConditionalExpr,
    Expression,
    IfStmt,
    IndexExpr,
    IntExpr,
    MemberExpr,
    RefExpr,
    SliceExpr,
    StrExpr,
    UnaryExpr,
)

from refurb.checks.common import is_equivalent, stringify
from refurb.error import Error
from refurb.settings import Settings
from refurb.visitor.traverser import TraverserVisitor


@dataclass
class ErrorInfo(Error):
    """
    Don't explicitly check a string prefix/suffix if you're only going to
    remove it, use `.removeprefix()` or `.removesuffix()` instead.

    Bad:

    ```
    def strip_txt_extension(filename: str) -> str:
        return filename[:-4] if filename.endswith(".txt") else filename
    ```

    Good:

    ```
    def strip_txt_extension(filename: str) -> str:
        return filename.removesuffix(".txt")
    ```
    """

    name = "remove-prefix-or-suffix"
    categories = ("performance", "readability", "string")
    code = 188


def does_expr_match_slice_amount(str_func: str, lhs: Expression, rhs: Expression) -> bool:
    match str_func, lhs, rhs:
        case (
            "startswith",
            StrExpr(value=value),
            SliceExpr(begin_index=IntExpr(value=str_len), end_index=None),
        ) if len(value) == str_len:
            return True

        case (
            "startswith",
            value,
            SliceExpr(
                begin_index=CallExpr(callee=RefExpr(fullname="builtins.len"), args=[len_arg]),
                end_index=None,
            ),
        ) if is_equivalent(value, len_arg):
            return True

        case (
            "endswith",
            StrExpr(value=value),
            SliceExpr(
                begin_index=None,
                end_index=UnaryExpr(op="-", expr=IntExpr(value=str_len)),
            ),
        ) if len(value) == str_len:
            return True

        case (
            "endswith",
            value,
            SliceExpr(
                begin_index=None,
                end_index=UnaryExpr(
                    op="-",
                    expr=CallExpr(callee=RefExpr(fullname="builtins.len"), args=[len_arg]),
                ),
            ),
        ) if is_equivalent(value, len_arg):
            return True

    return False


STR_FUNC_TO_REMOVE_FUNC = {"endswith": "removesuffix", "startswith": "removeprefix"}


ignored_nodes = set[int]()


class IgnoreElifNodes(TraverserVisitor):
    def visit_if_stmt(self, o: IfStmt) -> None:
        ignored_nodes.add(id(o))

        if o.else_body:
            if o.else_body.body:
                else_body = o.else_body.body[0]

                if isinstance(else_body, IfStmt):
                    ignored_nodes.add(id(else_body))

                    self.accept(else_body)


def check(node: ConditionalExpr | IfStmt, errors: list[Error], settings: Settings) -> None:
    if settings.get_python_version() < (3, 9):
        return  # pragma: no cover

    if id(node) in ignored_nodes:
        return

    if isinstance(node, IfStmt):
        if node.else_body:
            IgnoreElifNodes().accept(node.else_body)

            return

        expr = node.expr[0]
        body = node.body[0].body

        if len(body) != 1:
            return

        match expr:
            case CallExpr(
                callee=MemberExpr(
                    expr=func_lhs,
                    name="endswith" | "startswith" as func_name,
                ),
                args=[func_arg],
            ):
                pass

            case _:
                return

        match body[0]:
            case AssignmentStmt(
                lvalues=[lvalue],
                rvalue=IndexExpr(
                    base=slice_lhs,
                    index=SliceExpr(stride=None) as slice_expr,
                ),
            ) if (
                is_equivalent(slice_lhs, func_lhs)
                and is_equivalent(lvalue, slice_lhs)
                and does_expr_match_slice_amount(func_name, func_arg, slice_expr)
            ):
                parts = [
                    f"{stringify(slice_lhs)} = {stringify(slice_lhs)}.",
                    STR_FUNC_TO_REMOVE_FUNC[func_name],
                    f"({stringify(func_arg)})",
                ]

                msg = f"Replace `{stringify(node)}` with `{''.join(parts)}`"

                errors.append(ErrorInfo.from_node(node, msg))

    if isinstance(node, ConditionalExpr):
        match node:
            case ConditionalExpr(
                if_expr=IndexExpr(
                    base=slice_lhs,
                    index=SliceExpr(stride=None) as slice_expr,
                ),
                cond=CallExpr(
                    callee=MemberExpr(
                        expr=func_lhs,
                        name="endswith" | "startswith" as func_name,
                    ),
                    args=[func_arg],
                ),
                else_expr=if_false,
            ) if (
                is_equivalent(slice_lhs, func_lhs)
                and is_equivalent(func_lhs, if_false)
                and does_expr_match_slice_amount(func_name, func_arg, slice_expr)
            ):
                parts = [
                    f"{stringify(slice_lhs)}.",
                    STR_FUNC_TO_REMOVE_FUNC[func_name],
                    f"({stringify(func_arg)})",
                ]

                msg = f"Replace `{stringify(node)}` with `{''.join(parts)}`"

                errors.append(ErrorInfo.from_node(node, msg))

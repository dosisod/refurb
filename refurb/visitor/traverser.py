# This work is substantially derived from mypy (https://mypy-lang.org/), and
# is licensed under the same terms
# (https://github.com/python/mypy/blob/master/LICENSE) with all credits to the
# original author(s) and contributor(s), reproduced below.
#
# = = = = =
#
# The MIT License
#
# Copyright (c) 2012-2023 Jukka Lehtosalo and contributors
# Copyright (c) 2015-2023 Dropbox, Inc.
#
# Permission is hereby granted, free of charge, to any person obtaining a
# copy of this software and associated documentation files (the "Software"),
# to deal in the Software without restriction, including without limitation
# the rights to use, copy, modify, merge, publish, distribute, sublicense,
# and/or sell copies of the Software, and to permit persons to whom the
# Software is furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
# DEALINGS IN THE SOFTWARE.
#
# = = = = =

from __future__ import annotations

import functools

import mypy.nodes
import mypy.traverser
from mypy.nodes import AssertStmt as AssertStmt
from mypy.nodes import AssertTypeExpr as AssertTypeExpr
from mypy.nodes import AssignmentExpr as AssignmentExpr
from mypy.nodes import AssignmentStmt as AssignmentStmt
from mypy.nodes import AwaitExpr as AwaitExpr
from mypy.nodes import Block as Block
from mypy.nodes import BreakStmt as BreakStmt
from mypy.nodes import BytesExpr as BytesExpr
from mypy.nodes import CallExpr as CallExpr
from mypy.nodes import CastExpr as CastExpr
from mypy.nodes import ClassDef as ClassDef
from mypy.nodes import ComparisonExpr as ComparisonExpr
from mypy.nodes import ComplexExpr as ComplexExpr
from mypy.nodes import ConditionalExpr as ConditionalExpr
from mypy.nodes import Context as Context
from mypy.nodes import ContinueStmt as ContinueStmt
from mypy.nodes import Decorator as Decorator
from mypy.nodes import DelStmt as DelStmt
from mypy.nodes import DictExpr as DictExpr
from mypy.nodes import DictionaryComprehension as DictionaryComprehension
from mypy.nodes import EllipsisExpr as EllipsisExpr
from mypy.nodes import EnumCallExpr as EnumCallExpr
from mypy.nodes import ExpressionStmt as ExpressionStmt
from mypy.nodes import FloatExpr as FloatExpr
from mypy.nodes import ForStmt as ForStmt
from mypy.nodes import FuncDef as FuncDef
from mypy.nodes import GeneratorExpr as GeneratorExpr
from mypy.nodes import GlobalDecl as GlobalDecl
from mypy.nodes import IfStmt as IfStmt
from mypy.nodes import Import as Import
from mypy.nodes import ImportAll as ImportAll
from mypy.nodes import ImportFrom as ImportFrom
from mypy.nodes import IndexExpr as IndexExpr
from mypy.nodes import IntExpr as IntExpr
from mypy.nodes import LambdaExpr as LambdaExpr
from mypy.nodes import ListComprehension as ListComprehension
from mypy.nodes import ListExpr as ListExpr
from mypy.nodes import MatchStmt as MatchStmt
from mypy.nodes import MemberExpr as MemberExpr
from mypy.nodes import MypyFile as MypyFile
from mypy.nodes import NamedTupleExpr as NamedTupleExpr
from mypy.nodes import NameExpr as NameExpr
from mypy.nodes import NewTypeExpr as NewTypeExpr
from mypy.nodes import NonlocalDecl as NonlocalDecl
from mypy.nodes import OperatorAssignmentStmt as OperatorAssignmentStmt
from mypy.nodes import OpExpr as OpExpr
from mypy.nodes import OverloadedFuncDef as OverloadedFuncDef
from mypy.nodes import ParamSpecExpr as ParamSpecExpr
from mypy.nodes import PassStmt as PassStmt
from mypy.nodes import PlaceholderNode as PlaceholderNode
from mypy.nodes import PromoteExpr as PromoteExpr
from mypy.nodes import RaiseStmt as RaiseStmt
from mypy.nodes import ReturnStmt as ReturnStmt
from mypy.nodes import RevealExpr as RevealExpr
from mypy.nodes import SetComprehension as SetComprehension
from mypy.nodes import SetExpr as SetExpr
from mypy.nodes import SliceExpr as SliceExpr
from mypy.nodes import StarExpr as StarExpr
from mypy.nodes import StrExpr as StrExpr
from mypy.nodes import SuperExpr as SuperExpr
from mypy.nodes import TempNode as TempNode
from mypy.nodes import TryStmt as TryStmt
from mypy.nodes import TupleExpr as TupleExpr
from mypy.nodes import TypeAlias as TypeAlias
from mypy.nodes import TypeAliasExpr as TypeAliasExpr
from mypy.nodes import TypeApplication as TypeApplication
from mypy.nodes import TypedDictExpr as TypedDictExpr
from mypy.nodes import TypeVarExpr as TypeVarExpr
from mypy.nodes import TypeVarTupleExpr as TypeVarTupleExpr
from mypy.nodes import UnaryExpr as UnaryExpr
from mypy.nodes import Var as Var
from mypy.nodes import WhileStmt as WhileStmt
from mypy.nodes import WithStmt as WithStmt
from mypy.nodes import YieldExpr as YieldExpr
from mypy.nodes import YieldFromExpr as YieldFromExpr
from mypy.patterns import AsPattern as AsPattern
from mypy.patterns import ClassPattern as ClassPattern
from mypy.patterns import MappingPattern as MappingPattern
from mypy.patterns import OrPattern as OrPattern
from mypy.patterns import SequencePattern as SequencePattern
from mypy.patterns import SingletonPattern as SingletonPattern
from mypy.patterns import StarredPattern as StarredPattern
from mypy.patterns import ValuePattern as ValuePattern
from mypy.types import RequiredType as RequiredType


class TraverserVisitor:
    """A parse tree visitor that traverses the parse tree during visiting.

    It does not perform any actions outside the traversal. Subclasses
    should override visit methods to perform actions during
    traversal. Calling the superclass method allows reusing the
    traversal implementation.
    """

    def __init__(self) -> None:
        pass

    def accept(self, o: Context) -> None:
        return accept(o, self)

    def visit_func(self, o: mypy.nodes.FuncItem) -> None:
        if o.arguments is not None:
            for arg in o.arguments:
                init = arg.initializer
                if init is not None:
                    accept(init, self)
            for arg in o.arguments:
                self.visit_var(arg.variable)
        accept(o.body, self)

    def visit_mypy_file(self, o: MypyFile) -> None:
        for d in o.defs:
            accept(d, self)

    def visit_var(self, o: Var) -> None:
        pass

    def visit_type_alias(self, o: TypeAlias) -> None:
        pass

    def visit_placeholder_node(self, o: PlaceholderNode) -> None:
        pass

    def visit_int_expr(self, o: IntExpr) -> None:
        pass

    def visit_str_expr(self, o: StrExpr) -> None:
        pass

    def visit_bytes_expr(self, o: BytesExpr) -> None:
        pass

    def visit_float_expr(self, o: FloatExpr) -> None:
        pass

    def visit_complex_expr(self, o: ComplexExpr) -> None:
        pass

    def visit_ellipsis(self, o: EllipsisExpr) -> None:
        pass

    def visit_star_expr(self, o: StarExpr) -> None:
        accept(o.expr, self)

    def visit_name_expr(self, o: NameExpr) -> None:
        pass

    def visit_member_expr(self, o: MemberExpr) -> None:
        accept(o.expr, self)

    def visit_yield_from_expr(self, o: YieldFromExpr) -> None:
        accept(o.expr, self)

    def visit_yield_expr(self, o: YieldExpr) -> None:
        if o.expr:
            accept(o.expr, self)

    def visit_call_expr(self, o: CallExpr) -> None:
        accept(o.callee, self)
        for a in o.args:
            accept(a, self)
        if o.analyzed:
            accept(o.analyzed, self)

    def visit_op_expr(self, o: OpExpr) -> None:
        accept(o.left, self)
        accept(o.right, self)
        if o.analyzed is not None:
            accept(o.analyzed, self)

    def visit_comparison_expr(self, o: ComparisonExpr) -> None:
        for operand in o.operands:
            accept(operand, self)

    def visit_cast_expr(self, o: CastExpr) -> None:
        accept(o.expr, self)

    def visit_assert_type_expr(self, o: AssertTypeExpr) -> None:
        accept(o.expr, self)

    def visit_reveal_expr(self, o: RevealExpr) -> None:
        if o.kind == mypy.nodes.REVEAL_TYPE:
            assert o.expr is not None
            accept(o.expr, self)
        else:
            pass

    def visit_super_expr(self, o: SuperExpr) -> None:
        accept(o.call, self)

    def visit_unary_expr(self, o: UnaryExpr) -> None:
        accept(o.expr, self)

    def visit_assignment_expr(self, o: AssignmentExpr) -> None:
        accept(o.target, self)
        accept(o.value, self)

    def visit_list_expr(self, o: ListExpr) -> None:
        for item in o.items:
            accept(item, self)

    def visit_dict_expr(self, o: DictExpr) -> None:
        for k, v in o.items:
            if k is not None:
                accept(k, self)
            accept(v, self)

    def visit_tuple_expr(self, o: TupleExpr) -> None:
        for item in o.items:
            accept(item, self)

    def visit_set_expr(self, o: SetExpr) -> None:
        for item in o.items:
            accept(item, self)

    def visit_index_expr(self, o: IndexExpr) -> None:
        accept(o.base, self)
        accept(o.index, self)
        if o.analyzed:
            accept(o.analyzed, self)

    def visit_type_application(self, o: TypeApplication) -> None:
        accept(o.expr, self)

    def visit_lambda_expr(self, o: LambdaExpr) -> None:
        self.visit_func(o)

    def visit_list_comprehension(self, o: ListComprehension) -> None:
        accept(o.generator, self)

    def visit_set_comprehension(self, o: SetComprehension) -> None:
        accept(o.generator, self)

    def visit_dictionary_comprehension(self, o: DictionaryComprehension) -> None:
        for index, sequence, conditions in zip(o.indices, o.sequences, o.condlists):
            accept(sequence, self)
            accept(index, self)
            for cond in conditions:
                accept(cond, self)
        accept(o.key, self)
        accept(o.value, self)

    def visit_generator_expr(self, o: GeneratorExpr) -> None:
        for index, sequence, conditions in zip(o.indices, o.sequences, o.condlists):
            accept(sequence, self)
            accept(index, self)
            for cond in conditions:
                accept(cond, self)
        accept(o.left_expr, self)

    def visit_slice_expr(self, o: SliceExpr) -> None:
        if o.begin_index is not None:
            accept(o.begin_index, self)
        if o.end_index is not None:
            accept(o.end_index, self)
        if o.stride is not None:
            accept(o.stride, self)

    def visit_conditional_expr(self, o: ConditionalExpr) -> None:
        accept(o.cond, self)
        accept(o.if_expr, self)
        accept(o.else_expr, self)

    def visit_type_var_expr(self, o: TypeVarExpr) -> None:
        pass

    def visit_paramspec_expr(self, o: ParamSpecExpr) -> None:
        pass

    def visit_type_var_tuple_expr(self, o: TypeVarTupleExpr) -> None:
        pass

    def visit_type_alias_expr(self, o: TypeAliasExpr) -> None:
        pass

    def visit_namedtuple_expr(self, o: NamedTupleExpr) -> None:
        pass

    def visit_enum_call_expr(self, o: EnumCallExpr) -> None:
        pass

    def visit_typeddict_expr(self, o: TypedDictExpr) -> None:
        pass

    def visit_newtype_expr(self, o: NewTypeExpr) -> None:
        pass

    def visit__promote_expr(self, o: PromoteExpr) -> None:
        pass

    def visit_await_expr(self, o: AwaitExpr) -> None:
        accept(o.expr, self)

    def visit_temp_node(self, o: TempNode) -> None:
        pass

    def visit_assignment_stmt(self, o: AssignmentStmt) -> None:
        accept(o.rvalue, self)
        for l in o.lvalues:
            accept(l, self)

    def visit_for_stmt(self, o: ForStmt) -> None:
        accept(o.index, self)
        accept(o.expr, self)
        accept(o.body, self)
        if o.else_body:
            accept(o.else_body, self)

    def visit_with_stmt(self, o: WithStmt) -> None:
        for i in range(len(o.expr)):
            accept(o.expr[i], self)
            targ = o.target[i]
            if targ is not None:
                accept(targ, self)
        accept(o.body, self)

    def visit_del_stmt(self, o: DelStmt) -> None:
        if o.expr is not None:
            accept(o.expr, self)

    def visit_func_def(self, o: FuncDef) -> None:
        self.visit_func(o)

    def visit_overloaded_func_def(self, o: OverloadedFuncDef) -> None:
        for item in o.items:
            accept(item, self)
        if o.impl:
            accept(o.impl, self)

    def visit_class_def(self, o: ClassDef) -> None:
        for d in o.decorators:
            accept(d, self)
        for base in o.base_type_exprs:
            accept(base, self)
        if o.metaclass:
            accept(o.metaclass, self)
        for v in o.keywords.values():
            accept(v, self)
        accept(o.defs, self)
        if o.analyzed:
            accept(o.analyzed, self)

    def visit_global_decl(self, o: GlobalDecl) -> None:
        pass

    def visit_nonlocal_decl(self, o: NonlocalDecl) -> None:
        pass

    def visit_decorator(self, o: Decorator) -> None:
        accept(o.func, self)
        accept(o.var, self)
        for decorator in o.decorators:
            accept(decorator, self)

    def visit_import(self, o: Import) -> None:
        for a in o.assignments:
            accept(a, self)

    def visit_import_from(self, o: ImportFrom) -> None:
        for a in o.assignments:
            accept(a, self)

    def visit_import_all(self, o: ImportAll) -> None:
        pass

    def visit_block(self, block: Block) -> None:
        for s in block.body:
            accept(s, self)

    def visit_expression_stmt(self, o: ExpressionStmt) -> None:
        accept(o.expr, self)

    def visit_operator_assignment_stmt(self, o: OperatorAssignmentStmt) -> None:
        accept(o.rvalue, self)
        accept(o.lvalue, self)

    def visit_while_stmt(self, o: WhileStmt) -> None:
        accept(o.expr, self)
        accept(o.body, self)
        if o.else_body:
            accept(o.else_body, self)

    def visit_return_stmt(self, o: ReturnStmt) -> None:
        if o.expr is not None:
            accept(o.expr, self)

    def visit_assert_stmt(self, o: AssertStmt) -> None:
        if o.expr is not None:
            accept(o.expr, self)
        if o.msg is not None:
            accept(o.msg, self)

    def visit_if_stmt(self, o: IfStmt) -> None:
        for e in o.expr:
            accept(e, self)
        for b in o.body:
            accept(b, self)
        if o.else_body:
            accept(o.else_body, self)

    def visit_break_stmt(self, o: BreakStmt) -> None:
        pass

    def visit_continue_stmt(self, o: ContinueStmt) -> None:
        pass

    def visit_pass_stmt(self, o: PassStmt) -> None:
        pass

    def visit_raise_stmt(self, o: RaiseStmt) -> None:
        if o.expr is not None:
            accept(o.expr, self)
        if o.from_expr is not None:
            accept(o.from_expr, self)

    def visit_try_stmt(self, o: TryStmt) -> None:
        accept(o.body, self)
        for i in range(len(o.types)):
            tp = o.types[i]
            if tp is not None:
                accept(tp, self)
            accept(o.handlers[i], self)
        for v in o.vars:
            if v is not None:
                accept(v, self)
        if o.else_body is not None:
            accept(o.else_body, self)
        if o.finally_body is not None:
            accept(o.finally_body, self)

    def visit_match_stmt(self, o: MatchStmt) -> None:
        accept(o.subject, self)
        for i in range(len(o.patterns)):
            accept(o.patterns[i], self)
            guard = o.guards[i]
            if guard is not None:
                accept(guard, self)
            accept(o.bodies[i], self)

    def visit_as_pattern(self, o: AsPattern) -> None:
        if o.pattern is not None:
            accept(o.pattern, self)
        if o.name is not None:
            accept(o.name, self)

    def visit_or_pattern(self, o: OrPattern) -> None:
        for p in o.patterns:
            accept(p, self)

    def visit_value_pattern(self, o: ValuePattern) -> None:
        accept(o.expr, self)

    def visit_singleton_pattern(self, o: SingletonPattern) -> None:
        pass

    def visit_sequence_pattern(self, o: SequencePattern) -> None:
        for p in o.patterns:
            accept(p, self)

    def visit_starred_pattern(self, o: StarredPattern) -> None:
        if o.capture is not None:
            accept(o.capture, self)

    def visit_mapping_pattern(self, o: MappingPattern) -> None:
        for key in o.keys:
            accept(key, self)
        for value in o.values:
            accept(value, self)
        if o.rest is not None:
            accept(o.rest, self)

    def visit_class_pattern(self, o: ClassPattern) -> None:
        accept(o.class_ref, self)
        for p in o.positionals:
            accept(p, self)
        for v in o.keyword_values:
            accept(v, self)


@functools.singledispatch
def accept(node: Context, visitor: TraverserVisitor) -> None:
    raise NotImplementedError(f"No `visit_*` overload available for `{type(node).__qualname__}`")


@accept.register
def _(node: MypyFile, visitor: TraverserVisitor) -> None:
    return visitor.visit_mypy_file(node)


@accept.register
def _(node: Import, visitor: TraverserVisitor) -> None:
    return visitor.visit_import(node)


@accept.register
def _(node: ImportFrom, visitor: TraverserVisitor) -> None:
    return visitor.visit_import_from(node)


@accept.register
def _(node: ImportAll, visitor: TraverserVisitor) -> None:
    return visitor.visit_import_all(node)


@accept.register
def _(node: OverloadedFuncDef, visitor: TraverserVisitor) -> None:
    return visitor.visit_overloaded_func_def(node)


@accept.register
def _(node: FuncDef, visitor: TraverserVisitor) -> None:
    return visitor.visit_func_def(node)


@accept.register
def _(node: Decorator, visitor: TraverserVisitor) -> None:
    return visitor.visit_decorator(node)


@accept.register
def _(node: Var, visitor: TraverserVisitor) -> None:
    return visitor.visit_var(node)


@accept.register
def _(node: ClassDef, visitor: TraverserVisitor) -> None:
    return visitor.visit_class_def(node)


@accept.register
def _(node: GlobalDecl, visitor: TraverserVisitor) -> None:
    return visitor.visit_global_decl(node)


@accept.register
def _(node: NonlocalDecl, visitor: TraverserVisitor) -> None:
    return visitor.visit_nonlocal_decl(node)


@accept.register
def _(node: Block, visitor: TraverserVisitor) -> None:
    return visitor.visit_block(node)


@accept.register
def _(node: ExpressionStmt, visitor: TraverserVisitor) -> None:
    return visitor.visit_expression_stmt(node)


@accept.register
def _(node: AssignmentStmt, visitor: TraverserVisitor) -> None:
    return visitor.visit_assignment_stmt(node)


@accept.register
def _(node: OperatorAssignmentStmt, visitor: TraverserVisitor) -> None:
    return visitor.visit_operator_assignment_stmt(node)


@accept.register
def _(node: WhileStmt, visitor: TraverserVisitor) -> None:
    return visitor.visit_while_stmt(node)


@accept.register
def _(node: ForStmt, visitor: TraverserVisitor) -> None:
    return visitor.visit_for_stmt(node)


@accept.register
def _(node: ReturnStmt, visitor: TraverserVisitor) -> None:
    return visitor.visit_return_stmt(node)


@accept.register
def _(node: AssertStmt, visitor: TraverserVisitor) -> None:
    return visitor.visit_assert_stmt(node)


@accept.register
def _(node: DelStmt, visitor: TraverserVisitor) -> None:
    return visitor.visit_del_stmt(node)


@accept.register
def _(node: BreakStmt, visitor: TraverserVisitor) -> None:
    return visitor.visit_break_stmt(node)


@accept.register
def _(node: ContinueStmt, visitor: TraverserVisitor) -> None:
    return visitor.visit_continue_stmt(node)


@accept.register
def _(node: PassStmt, visitor: TraverserVisitor) -> None:
    return visitor.visit_pass_stmt(node)


@accept.register
def _(node: IfStmt, visitor: TraverserVisitor) -> None:
    return visitor.visit_if_stmt(node)


@accept.register
def _(node: RaiseStmt, visitor: TraverserVisitor) -> None:
    return visitor.visit_raise_stmt(node)


@accept.register
def _(node: TryStmt, visitor: TraverserVisitor) -> None:
    return visitor.visit_try_stmt(node)


@accept.register
def _(node: WithStmt, visitor: TraverserVisitor) -> None:
    return visitor.visit_with_stmt(node)


@accept.register
def _(node: MatchStmt, visitor: TraverserVisitor) -> None:
    return visitor.visit_match_stmt(node)


@accept.register
def _(node: IntExpr, visitor: TraverserVisitor) -> None:
    return visitor.visit_int_expr(node)


@accept.register
def _(node: StrExpr, visitor: TraverserVisitor) -> None:
    return visitor.visit_str_expr(node)


@accept.register
def _(node: BytesExpr, visitor: TraverserVisitor) -> None:
    return visitor.visit_bytes_expr(node)


@accept.register
def _(node: FloatExpr, visitor: TraverserVisitor) -> None:
    return visitor.visit_float_expr(node)


@accept.register
def _(node: ComplexExpr, visitor: TraverserVisitor) -> None:
    return visitor.visit_complex_expr(node)


@accept.register
def _(node: EllipsisExpr, visitor: TraverserVisitor) -> None:
    return visitor.visit_ellipsis(node)


@accept.register
def _(node: StarExpr, visitor: TraverserVisitor) -> None:
    return visitor.visit_star_expr(node)


@accept.register
def _(node: NameExpr, visitor: TraverserVisitor) -> None:
    return visitor.visit_name_expr(node)


@accept.register
def _(node: MemberExpr, visitor: TraverserVisitor) -> None:
    return visitor.visit_member_expr(node)


@accept.register
def _(node: CallExpr, visitor: TraverserVisitor) -> None:
    return visitor.visit_call_expr(node)


@accept.register
def _(node: YieldFromExpr, visitor: TraverserVisitor) -> None:
    return visitor.visit_yield_from_expr(node)


@accept.register
def _(node: YieldExpr, visitor: TraverserVisitor) -> None:
    return visitor.visit_yield_expr(node)


@accept.register
def _(node: IndexExpr, visitor: TraverserVisitor) -> None:
    return visitor.visit_index_expr(node)


@accept.register
def _(node: UnaryExpr, visitor: TraverserVisitor) -> None:
    return visitor.visit_unary_expr(node)


@accept.register
def _(node: AssignmentExpr, visitor: TraverserVisitor) -> None:
    return visitor.visit_assignment_expr(node)


@accept.register
def _(node: OpExpr, visitor: TraverserVisitor) -> None:
    return visitor.visit_op_expr(node)


@accept.register
def _(node: ComparisonExpr, visitor: TraverserVisitor) -> None:
    return visitor.visit_comparison_expr(node)


@accept.register
def _(node: SliceExpr, visitor: TraverserVisitor) -> None:
    return visitor.visit_slice_expr(node)


@accept.register
def _(node: CastExpr, visitor: TraverserVisitor) -> None:
    return visitor.visit_cast_expr(node)


@accept.register
def _(node: AssertTypeExpr, visitor: TraverserVisitor) -> None:
    return visitor.visit_assert_type_expr(node)


@accept.register
def _(node: RevealExpr, visitor: TraverserVisitor) -> None:
    return visitor.visit_reveal_expr(node)


@accept.register
def _(node: SuperExpr, visitor: TraverserVisitor) -> None:
    return visitor.visit_super_expr(node)


@accept.register
def _(node: LambdaExpr, visitor: TraverserVisitor) -> None:
    return visitor.visit_lambda_expr(node)


@accept.register
def _(node: ListExpr, visitor: TraverserVisitor) -> None:
    return visitor.visit_list_expr(node)


@accept.register
def _(node: DictExpr, visitor: TraverserVisitor) -> None:
    return visitor.visit_dict_expr(node)


@accept.register
def _(node: TupleExpr, visitor: TraverserVisitor) -> None:
    return visitor.visit_tuple_expr(node)


@accept.register
def _(node: SetExpr, visitor: TraverserVisitor) -> None:
    return visitor.visit_set_expr(node)


@accept.register
def _(node: GeneratorExpr, visitor: TraverserVisitor) -> None:
    return visitor.visit_generator_expr(node)


@accept.register
def _(node: ListComprehension, visitor: TraverserVisitor) -> None:
    return visitor.visit_list_comprehension(node)


@accept.register
def _(node: SetComprehension, visitor: TraverserVisitor) -> None:
    return visitor.visit_set_comprehension(node)


@accept.register
def _(node: DictionaryComprehension, visitor: TraverserVisitor) -> None:
    return visitor.visit_dictionary_comprehension(node)


@accept.register
def _(node: ConditionalExpr, visitor: TraverserVisitor) -> None:
    return visitor.visit_conditional_expr(node)


@accept.register
def _(node: TypeApplication, visitor: TraverserVisitor) -> None:
    return visitor.visit_type_application(node)


@accept.register
def _(node: TypeVarExpr, visitor: TraverserVisitor) -> None:
    return visitor.visit_type_var_expr(node)


@accept.register
def _(node: ParamSpecExpr, visitor: TraverserVisitor) -> None:
    return visitor.visit_paramspec_expr(node)


@accept.register
def _(node: TypeVarTupleExpr, visitor: TraverserVisitor) -> None:
    return visitor.visit_type_var_tuple_expr(node)


@accept.register
def _(node: TypeAliasExpr, visitor: TraverserVisitor) -> None:
    return visitor.visit_type_alias_expr(node)


@accept.register
def _(node: NamedTupleExpr, visitor: TraverserVisitor) -> None:
    return visitor.visit_namedtuple_expr(node)


@accept.register
def _(node: TypedDictExpr, visitor: TraverserVisitor) -> None:
    return visitor.visit_typeddict_expr(node)


@accept.register
def _(node: EnumCallExpr, visitor: TraverserVisitor) -> None:
    return visitor.visit_enum_call_expr(node)


@accept.register
def _(node: PromoteExpr, visitor: TraverserVisitor) -> None:
    return visitor.visit__promote_expr(node)


@accept.register
def _(node: NewTypeExpr, visitor: TraverserVisitor) -> None:
    return visitor.visit_newtype_expr(node)


@accept.register
def _(node: AwaitExpr, visitor: TraverserVisitor) -> None:
    return visitor.visit_await_expr(node)


@accept.register
def _(node: TempNode, visitor: TraverserVisitor) -> None:
    return visitor.visit_temp_node(node)


@accept.register
def _(node: TypeAlias, visitor: TraverserVisitor) -> None:
    return visitor.visit_type_alias(node)


@accept.register
def _(node: PlaceholderNode, visitor: TraverserVisitor) -> None:
    return visitor.visit_placeholder_node(node)


@accept.register
def _(node: AsPattern, visitor: TraverserVisitor) -> None:
    return visitor.visit_as_pattern(node)


@accept.register
def _(node: OrPattern, visitor: TraverserVisitor) -> None:
    return visitor.visit_or_pattern(node)


@accept.register
def _(node: ValuePattern, visitor: TraverserVisitor) -> None:
    return visitor.visit_value_pattern(node)


@accept.register
def _(node: SingletonPattern, visitor: TraverserVisitor) -> None:
    return visitor.visit_singleton_pattern(node)


@accept.register
def _(node: SequencePattern, visitor: TraverserVisitor) -> None:
    return visitor.visit_sequence_pattern(node)


@accept.register
def _(node: StarredPattern, visitor: TraverserVisitor) -> None:
    return visitor.visit_starred_pattern(node)


@accept.register
def _(node: MappingPattern, visitor: TraverserVisitor) -> None:
    return visitor.visit_mapping_pattern(node)


@accept.register
def _(node: ClassPattern, visitor: TraverserVisitor) -> None:
    return visitor.visit_class_pattern(node)


@accept.register
def _(node: RequiredType, visitor: TraverserVisitor) -> None:
    return accept(node.item, visitor)

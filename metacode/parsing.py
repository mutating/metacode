from ast import AST, AnnAssign, Constant, Name, Subscript, Tuple
from ast import parse as ast_parse
from dataclasses import dataclass
from typing import Generator, List, Optional, Union

from libcst import SimpleStatementLine
from libcst import parse_module as cst_parse
from libcst._exceptions import ParserSyntaxError as CSTSyntaxError

from metacode.errors import UnknownArgumentTypeError


@dataclass
class ParsedComment:
    key: str
    command: str
    arguments: List[Optional[Union[str, int, float, bool, AST]]]


def get_right_part(comment: str) -> str:
    return '#'.join(comment.split('#')[1:])


def get_commment_from_cst(comment: str) -> Optional[str]:
    comment = comment.lstrip()

    if not comment:
        return None

    try:
        module = cst_parse(comment)
    except CSTSyntaxError:
        return get_right_part(comment)

    try:
        statement = next(s for s in module.body if isinstance(s, SimpleStatementLine))
    except StopIteration:
        return get_right_part(comment)

    trailing_whitespace = statement.trailing_whitespace
    comment_of_comment = trailing_whitespace.comment.value if trailing_whitespace.comment is not None else None

    if comment_of_comment is None:
        return get_right_part(comment)

    return comment_of_comment.lstrip("#").lstrip()


def get_candidates(comment: str) -> Generator[ParsedComment, None, None]:
    comment = comment.lstrip()
    try:
        parsed_ast = ast_parse(comment)
        if not (len(parsed_ast.body) != 1 or not isinstance(parsed_ast.body[0], AnnAssign) or not isinstance(parsed_ast.body[0].target, Name) or not isinstance(parsed_ast.body[0].annotation, (Name, Subscript))):

            assign = parsed_ast.body[0]
            key = assign.target.id

            arguments = []
            if isinstance(assign.annotation, Name):
                command = assign.annotation.id

            else:
                command = assign.annotation.value.id

                if isinstance(assign.annotation.slice, Tuple):
                    slice_content = assign.annotation.slice.elts
                else:
                    slice_content = [assign.annotation.slice]

                for argument in slice_content:
                    if isinstance(argument, Name):
                        arguments.append(argument.id)
                    elif isinstance(argument, Constant):
                        arguments.append(argument.value)
                    else:
                        arguments.append(argument)

            yield ParsedComment(
                key=key,
                command=command,
                arguments=arguments,
            )

        sub_comment = get_commment_from_cst(comment)
        if sub_comment is not None:
            yield from get_candidates(sub_comment)

    except SyntaxError:
        splitted_comment = comment.split('#')
        if len(splitted_comment) > 1:
            yield from get_candidates(get_right_part(comment))


def parse(comment: str, key: str, allow_ast: bool = False, ignore_case: bool = False) -> List[ParsedComment]:
    if not key.isidentifier():
        raise ValueError('The key must be valid Python identifier.')

    result = []

    comment = comment.lstrip()

    if not comment:
        return result

    for candidate in get_candidates(comment):
        if candidate.key == key or (candidate.key.lower() == key.lower() and ignore_case):
            for argument in candidate.arguments:
                if isinstance(argument, AST) and not allow_ast:
                    raise UnknownArgumentTypeError(f'An argument of unknown type was found in the comment {comment!r}.')
            result.append(candidate)

    return result

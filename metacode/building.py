from ast import AST

from metacode.comment import ParsedComment
from metacode.typing import EllipsisType  # type: ignore[attr-defined]


def build(comment: ParsedComment) -> str:
    if not comment.key.isidentifier():
        raise ValueError('The key must be valid Python identifier.')
    if not comment.command.isidentifier():
        raise ValueError('The command must be valid Python identifier.')

    result = f'# {comment.key}: {comment.command}'

    if comment.arguments:
        arguments_representations = []

        for argument in comment.arguments:
            if isinstance(argument, AST):
                raise TypeError('AST nodes are read-only and cannot be written to.')
            if isinstance(argument, EllipsisType):
                arguments_representations.append('...')
            elif isinstance(argument, str) and argument.isidentifier():
                arguments_representations.append(argument)
            else:
                arguments_representations.append(repr(argument))

        result += f'[{", ".join(arguments_representations)}]'

    return result


def insert(comment: ParsedComment, existing_comment: str, at_end: bool = False) -> str:
    if not existing_comment:
        return build(comment)

    if not existing_comment.lstrip().startswith('#'):
        raise ValueError('The existing part of the comment should start with a #.')

    if at_end:
        if existing_comment.endswith(' '):
            return existing_comment + build(comment)
        return f'{existing_comment} {build(comment)}'

    if existing_comment.startswith(' '):
        return f'{build(comment)}{existing_comment}'
    return f'{build(comment)} {existing_comment}'

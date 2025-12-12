<details>
  <summary>ⓘ</summary>

[![Downloads](https://static.pepy.tech/badge/metacode/month)](https://pepy.tech/project/metacode)
[![Downloads](https://static.pepy.tech/badge/metacode)](https://pepy.tech/project/metacode)
[![Coverage Status](https://coveralls.io/repos/github/pomponchik/metacode/badge.svg?branch=main)](https://coveralls.io/github/pomponchik/metacode?branch=main)
[![Lines of code](https://sloc.xyz/github/pomponchik/metacode/?category=code)](https://github.com/boyter/scc/)
[![Hits-of-Code](https://hitsofcode.com/github/pomponchik/metacode?branch=main&label=Hits-of-Code&exclude=docs/)](https://hitsofcode.com/github/pomponchik/metacode/view?branch=main)
[![Test-Package](https://github.com/pomponchik/metacode/actions/workflows/tests_and_coverage.yml/badge.svg)](https://github.com/pomponchik/metacode/actions/workflows/tests_and_coverage.yml)
[![Python versions](https://img.shields.io/pypi/pyversions/metacode.svg)](https://pypi.python.org/pypi/metacode)
[![PyPI version](https://badge.fury.io/py/metacode.svg)](https://badge.fury.io/py/metacode)
[![Checked with mypy](http://www.mypy-lang.org/static/mypy_badge.svg)](http://mypy-lang.org/)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![DeepWiki](https://deepwiki.com/badge.svg)](https://deepwiki.com/pomponchik/metacode)

</details>


![logo](https://raw.githubusercontent.com/pomponchik/metacode/develop/docs/assets/logo_3.svg)

Many source code analysis tools use comments in a special format to mark it up. This is an important part of the Python ecosystem, but there is still no single standard around it. This library offers such a standard.


## Table of contents

- [**Why?**](#why)
- [**The language**](#the-language)
- [**Installation**](#installation)
- [**Usage**](#usage)
- [**What about other languages?**](#what-about-other-languages)


## Why?

In the Python ecosystem, there are many tools dealing with source code: linters, test coverage collection systems, and many others. Many of them use special comments, and as a rule, the style of these comments is very similar. Here are some examples:

- [`Ruff`](https://docs.astral.sh/ruff/linter/#error-suppression), [`Vulture`](https://github.com/jendrikseipp/vulture?tab=readme-ov-file#flake8-noqa-comments) —> `# noqa`, `# noqa: E741, F841`.
- [`Black`](https://black.readthedocs.io/en/stable/usage_and_configuration/the_basics.html#ignoring-sections) and [`Ruff`](https://docs.astral.sh/ruff/formatter/#format-suppression) —> `# fmt: on`, `# fmt: off`.
- [`Mypy`](https://discuss.python.org/t/ignore-mypy-specific-type-errors/58535) —> `# type: ignore`, `type: ignore[error-code]`.
- [`Coverage`](https://coverage.readthedocs.io/en/7.13.0/excluding.html#default-exclusions) —> `# pragma: no cover`, `# pragma: no branch`.
- [`Isort`](https://pycqa.github.io/isort/docs/configuration/action_comments.html) —> `# isort: skip`, `# isort: off`.
- [`Bandit`](https://bandit.readthedocs.io/en/latest/config.html#suppressing-individual-lines) —> `# nosec`.

But you know what? *There is no single standard for such comments*.

The internal implementation of reading such comments is also different. Someone uses regular expressions, someone uses even more primitive string processing tools, and someone uses full-fledged parsers, including the Python parser or even written from scratch.

As a result, as a user, you need to remember the rules by which comments are written for each specific tool. And at the same time, you can't be sure that things like double comments (when you want to leave 2 comments for different tools in one line of code) will work in principle. And as the creator of such tools, you are faced with a seemingly simple task — just to read a comment — and find out for yourself that it suddenly turns out to be quite difficult, and there are many possible mistakes.

This is exactly the problem that this library solves. It describes a [simple and intuitive standard](https://xkcd.com/927/) for action comments, and also offers a ready-made parser that creators of other tools can use. The standard offered by this library is based entirely on a subset of the Python syntax and can be easily reimplemented even if you do not want to use this library directly.


## The language

So, this library offers a language for action comments. Its syntax is a subset of Python syntax, but without Python semantics, as full-fledged execution does not occur. The purpose of the language is simply to provide the developer with the content of the comment in a convenient way, if it is written in a compatible format. If the comment format is not compatible with the parser, it is ignored.

From the point of view of the language, any meaningful comment can consist of 3 elements:

- **Key**. This is usually the name of the specific tool for which this comment is intended, but in some cases it may be something else. This can be any string allowed as an [identifier](https://docs.python.org/3/reference/lexical_analysis.html#identifiers) in Python.
- **Action**. The short name of the action that you want to link to this line. Also, only the allowed Python identifier.
- **List of arguments**. These are often some kind of identifiers of specific linting rules or other arguments associated with this action. The list of possible data types described below.

Consider a comment designed to ignore a specific mypy rule:

```
# type: ignore[error-code]
└-key-┘└action┴-arguments┘
```

> ↑ The key here is the word `type`, that is, what you see before the colon. The action is the `ignore` word, that is, what comes before the square brackets, but after the colon. Finally, the list of arguments is what is in square brackets, in this case, there is only one argument in it: `error-code`.

Simplified writing is also possible, without a list of arguments:

```
# type: ignore
└-key-┘└action┘
```

> ↑ In this case, the parser assumes that there is an argument list, but it is empty.

The number of arguments in the list is unlimited, they can be separated by commas. Here are the valid data types for arguments:

- [Valid Python identifiers](https://docs.python.org/3/reference/lexical_analysis.html#identifiers). They are interpreted as strings.
- Two valid Python identifiers, separated by the `-` symbol, like this: `error-code`. There can also be any number of spaces between them, they will be ignored. Interpreted as a single string.
- String literals.
- Numeric literals (`int`, `float`, `complex`).
- Boolean literals (`True` and `False`).
- `None`.
- `...` ([ellipsis](https://docs.python.org/dev/library/constants.html#Ellipsis)).
- Any other Python-compatible code. This is disabled by default, but you can force the mode of reading such code and get descriptions for any inserts of such code in the form of [`AST` objects](https://docs.python.org/3/library/ast.html#ast.AST), after which you can somehow process it yourself.

The syntax of all these data types is completely similar to the Python original (except that you can't use multi-line writing options). Over time, it is possible to extend the possible syntax of `metacode`, but this template will always be supported.

There can be several comments in the `metacode` format. In this case, they should be interspersed with the `#` symbol, as if each subsequent comment is a comment on the previous one. You can also add regular text comments, they will just be ignored by the parser if they are not in `metacode` format:

``` python
# type: ignore # <- This is a comment for mypy! # fmt: off # <- And this is a comment for Ruff!
```

If you scroll through this text [above](#why) to the examples of action comments from various tools, you may notice that the syntax of most of them (but not all) is it can be described using `metacode`, and if not, it can be easily adapted to `metacode`. Read on to learn how to use a ready-made parser in practice.


## Installation

Install it:

```bash
pip install metacode
```

You can also quickly try out this and other packages without having to install using [instld](https://github.com/pomponchik/instld).


## Usage

The parser offered by this library is just one function that is imported like this:

```python
from metacode import parse
```

To use it, you need to extract the text of the comment in some third-party way (preferably, but not necessarily, without the `#` symbol at the beginning) and pass it, and the expected key must also be passed as the second argument. As a result, you will receive a list of the contents of all the comments that were parsed:

```python
print(parse('type: ignore[error-code]', 'type'))
#> [ParsedComment(key='type', command='ignore', arguments=['error-code'])]
print(parse('type: ignore[error-code] # type: not_ignore[another-error]', 'type'))
#> [ParsedComment(key='type', command='ignore', arguments=['error-code']), ParsedComment(key='type', command='not_ignore', arguments=['another-error'])]
```

As you can see, the `parse()` function returns a list of `ParsedComment` objects. Here are the fields of this type's objects and their expected types:

```python
key: str 
command: str
arguments: List[Optional[Union[str, int, float, complex, bool, EllipsisType, AST]]]
```

> ↑ Please note that you are transmitting a key, which means that the result is returned filtered by this key. This way you can read only those comments that relate to your tool, ignoring the rest.

By default, an argument in a comment must be of one of the strictly allowed types. However, you can enable reading of arbitrary other types, in which case they will be transmitted in the [`AST` node](https://docs.python.org/3/library/ast.html#ast.AST) format. To do this, pass `allow_ast=True`:

```python
print(parse('key: action[a + b]', 'key', allow_ast=True))
#> [ParsedComment(key='key', command='action', arguments=[<ast.BinOp object at 0x102e44eb0>])]
```

> ↑ If you do not pass `allow_ast=True`, a `metacode.errors.UnknownArgumentTypeError` exception will be raised. When processing an argument, you can also raise this exception for an AST node of a format that your tool does not expect.

> ⚠️ Be careful when writing code that analyzes the AST. Different versions of the Python interpreter can generate different AST based on the same code, so don't forget to test your code (for example, using [matrix](https://docs.github.com/en/actions/how-tos/write-workflows/choose-what-workflows-do/run-job-variations) or [tox](https://tox.wiki/)) well. Otherwise, it is better to use standard `metacode` argument types.

You can allow your users to write keys in any case. To do this, pass `ignore_case=True`:

```python
print(parse('KEY: action', 'key', ignore_case=True))
#> [ParsedComment(key='KEY', command='action', arguments=[])]
```

You can also easily add support for several different keys. To do this, pass a list of keys instead of one key:

```python
print(parse('key: action # other_key: other_action', ['key', 'other_key']))
#> [ParsedComment(key='key', command='action', arguments=[]), ParsedComment(key='other_key', command='other_action', arguments=[])]
```

Well, now we can read the comments. But what if we want to record? There is another function for this: `insert()`:

```python
from metacode import insert, ParsedComment
```

You send the comment you want to insert there, as well as the current comment (empty if there is no comment, or starting with # if there is), and you get a ready-made new comment text:

```python
print(insert(ParsedComment(key='key', command='command', arguments=['lol', 'lol-kek']), ''))
# key: command[lol, 'lol-kek']
print(insert(ParsedComment(key='key', command='command', arguments=['lol', 'lol-kek']), '# some existing text'))
# key: command[lol, 'lol-kek'] # some existing text
```

As you can see, our comment is inserted before the existing comment. However, you can do the opposite:

```python
print(insert(ParsedComment(key='key', command='command', arguments=['lol', 'lol-kek']), '# some existing text', at_end=True))
# some existing text # key: command[lol, 'lol-kek']
```

> ⚠️ Be careful: AST nodes can be read, but cannot be written.


## What about other languages?

If you are writing your Python-related tool not in Python, as is currently fashionable, but in some other language, such as Rust, you may want to adhere to the `metacode` standard for machine-readable comments, however, you cannot directly use the ready-made parser described [above](#usage). What to do?

The proposed `metacode` language is a syntactic subset of Python. The original `metacode` parser allows you to read arbitrary arguments written in Python as AST nodes. The rules for such parsing are determined by the specific version of the interpreter that `metacode` runs under, and they cannot be strictly standardized, since [Python syntax](https://docs.python.org/3/reference/grammar.html) is gradually evolving in an unpredictable direction. However, you can use a "safe" subset of the valid syntax by implementing your parser based on this [`EBNF`](https://en.wikipedia.org/wiki/Extended_Backus%E2%80%93Naur_form) grammar:

```
line ::= element { "#" element }
element ::= statement | ignored_content
statement ::= key ":" action [ "[" arguments "]" ]
ignored_content ::= ? any sequence of characters excluding "#" ?

key ::= identifier
action ::= identifier { "-" identifier }
arguments ::= argument { "," argument }

argument ::= hyphenated_identifier 
           | identifier 
           | string_literal 
           | complex_literal 
           | number_literal 
           | "True" | "False" | "None" | "..."

hyphenated_identifier ::= identifier "-" identifier
identifier ::= ? python-style identifier ?
string_literal ::= ? python-style string ?
number_literal ::= ? python-style number ?
complex_literal ::= ? python-style complex number ?
```

If you suddenly implement your ready-made open-source parser of this grammar in a language other than Python, please [let me know](https://github.com/pomponchik/metacode/issues). This information can be added to this text.

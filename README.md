![logo](https://raw.githubusercontent.com/pomponchik/metacode/develop/docs/assets/logo_3.svg)

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

Many source code analysis tools use comments in a special format to mark it up. This is an important part of the Python ecosystem, but there is still no single standard around it. This library offers such a standard.


## Table of contents

- [**Why?**](#why)
- [**The language**](#the-language)
- [**Installation**](#installation)
- [**Usage**](#usage)


## Why?

In the Python ecosystem, there are many tools dealing with source code: linters, test coverage collection systems, and many others. Many of them use special comments, and as a rule, the style of these comments is very similar. Here are some examples:

- [`Ruff`](https://docs.astral.sh/ruff/linter/#error-suppression), [`Vulture`](https://github.com/jendrikseipp/vulture?tab=readme-ov-file#flake8-noqa-comments) — `# noqa`, `# noqa: E741, F841`.
- [`Black`](https://black.readthedocs.io/en/stable/usage_and_configuration/the_basics.html#ignoring-sections) and [`Ruff`](https://docs.astral.sh/ruff/formatter/#format-suppression) — `# fmt: on`, `# fmt: off`.
- [`Mypy`](https://discuss.python.org/t/ignore-mypy-specific-type-errors/58535) — `# type: ignore`, `type: ignore[error-code]`.
- [`Coverage`](https://coverage.readthedocs.io/en/7.13.0/excluding.html#default-exclusions) — `# pragma: no cover`, `# pragma: no branch`.
- [`Isort`](https://pycqa.github.io/isort/docs/configuration/action_comments.html) — `# isort: skip`, `# isort: off`.
- [`Bandit`](https://bandit.readthedocs.io/en/latest/config.html#suppressing-individual-lines) — `# nosec`.

... and a lot others.

They seem very similar. But you know what? *There is no single standard for such comments*. Seriously.

The internal implementation of reading such comments is also different. Someone uses regular expressions, someone uses even more primitive string processing tools, and someone uses full-fledged parsers, including the Python parser or even written from scratch.

As a result, as a user, you need to remember the rules by which comments are written for each specific tool. And at the same time, you can't be sure that things like double comments (when you want to leave 2 comments for different tools in one line of code) will work in principle. And as the creator of such tools, you are faced with a seemingly simple task — just to read a comment — and find out for yourself that it suddenly turns out to be quite difficult, and there are many possible mistakes.

This is exactly the problem that this library solves. It describes a simple and intuitive standard for action comments, and also offers a ready-made parser that creators of other tools can use. The standard offered by this library is based entirely on a subset of the Python syntax and can be easily reimplemented even if you do not want to use this library directly.


















## The language

## Installation


Install it:

```bash
pip install metacode
```

You can also quickly try out this and other packages without having to install using [instld](https://github.com/pomponchik/instld).


## Usage

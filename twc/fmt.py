"""Format console output."""
# pylint: disable=no-name-in-module
# See https://github.com/PyCQA/pylint/issues/491

import re
import sys
import json

import click
import yaml

from pygments import highlight
from pygments.lexers import JsonLexer, YamlLexer
from pygments.formatters import TerminalFormatter


class Table:
    """Print table. Example::

    >>> t = Table()
    >>> t.header(['KEY', 'VALUE'])  # header is optional
    >>> t.row(['key 1', 'value 1'])
    >>> t.row(['key 2', 'value 2'])
    >>> t.rows(
    ...     [
    ...         ['key 3', 'value 3'],
    ...         ['key 4', 'value 4']
    ...     ]
    >>> )
    >>> t.print()

    """

    def __init__(self, whitespace: str = "\t"):
        self.__rows = []
        self.__whitespace = whitespace

    def header(self, columns: list):
        """Add `columns` list as first element in `rows` list."""
        self.__rows.insert(0, [str(col) for col in columns])

    def row(self, row: list):
        """Add new row to table."""
        self.__rows.append([str(col) for col in row])

    def rows(self, rows: list):
        """Add multiple rows to table."""
        for row in rows:
            self.row(row)

    def print(self):
        """Print table content to terminal."""
        widths = [max(map(len, col)) for col in zip(*self.__rows)]
        for row in self.__rows:
            click.echo(
                self.__whitespace.join(
                    (val.ljust(width) for val, width in zip(row, widths))
                )
            )


class Printer:
    """Display data in different formats."""

    def __init__(self, data: object):
        self._data = data

    def raw(self):
        """Print raw API response text (mostly raw JSON)."""
        click.echo(self._data.text)

    def colorize(self, data: str, lexer: object = JsonLexer()):
        """Print colorized output. Fallback to non-color."""
        click.echo(highlight(data, lexer, TerminalFormatter()).strip())

    def pretty_json(self):
        """Print colorized JSON output. Fallback to non-color output if
        Pygments not installed and fallback to raw output on JSONDecodeError.
        """
        try:
            json_data = json.dumps(
                self._data.json(), indent=4, sort_keys=True, ensure_ascii=False
            )
            self.colorize(json_data, lexer=JsonLexer())
        except json.JSONDecodeError:
            self.raw()

    def pretty_yaml(self):
        """Print colorized YAML output. Fallback to non-color output if
        Pygments not installed and fallback to raw output on YAMLError.
        """
        try:
            yaml_data = yaml.dump(
                self._data.json(), sort_keys=True, allow_unicode=True
            )
            self.colorize(yaml_data, lexer=YamlLexer())
        except yaml.YAMLError:
            self.raw()

    def print(self, output_format: str = "raw", func=None, **kwargs):
        """Print `requests.Response` object.
        - If `output_format` is 'raw' print raw HTTP body text.
        - If `output_format` is 'json' print colorized JSON.
        - If `output_format` is 'yaml' print colorized YAML.
        - If function `func` is passed use it to print response data.
        """
        if output_format == "raw":
            self.raw()
        elif output_format == "json":
            self.pretty_json()
        elif output_format == "yaml":
            self.pretty_yaml()
        else:
            try:
                if func:
                    func(self._data, **kwargs)
            except KeyError:  # fallback to 'json' or 'raw' on error
                click.echo(
                    "Error: Cannot represent output. Fallback to JSON.",
                    err=True,
                )
                self.pretty_json()


def printer(response: object, output_format: str = "raw", func=None, **kwargs):
    """Print `requests.Response` object.
    This is the same as `Printer(*args, **kwargs).print()`.
    """
    to_print = Printer(response)
    if func:
        to_print.print(output_format, func=func, **kwargs)
    else:
        to_print.print(output_format, **kwargs)


def query_dict(data: dict, keys: list):
    """Return value of dict by list of keys. For example::

    >>> mydict = {'server':{'os':{'name':'ubuntu','version':'22.04',}}}
    >>> query = 'server.os.name'
    >>> result = query_dict(mydict, query.split('.'))

    In result: 'ubuntu'
    """
    exp = ""
    for key in keys:
        if re.match(r"^[a-zA-Z0-9_]+$", key):
            exp = exp + f"['{key}']"
    try:
        # pylint: disable=eval-used
        return eval(f"{data}{exp}", {"__builtins__": {}}, {})
    except TypeError:
        return None


def filter_list(objects: list, filters: str) -> list:
    """Filter list of objects. Return filtered list.

    `filters` is a string with following format::

        ``<key>:<value>,<key>:<value>``

    Key-Value pairs count is unlimited. Available filter keys and
    values depends on passed object.
    """
    if not re.match(r"^(([a-zA-Z0-9._-]+:[a-zA-Z0-9._-]+),?)+$", filters):
        sys.exit("Error: Invalid filter format")

    for key_val in filters.split(","):
        try:
            key, val = key_val.split(":")

            # Allow search in megabytes or gigabytes, e.g. 1024m, 1g.
            if key in ["ram", "disk", "size"]:
                if val.lower().endswith("m"):
                    val = val[:-1]
                if val.lower().endswith("g"):
                    val = str(int(val[:-1]) * 1024)

            objects = list(
                filter(
                    # pylint: disable=cell-var-from-loop
                    # This is fine
                    lambda x: str(query_dict(x, key.split("."))) == val,
                    objects,
                )
            )
        except (KeyError, ValueError):
            return []
    return objects

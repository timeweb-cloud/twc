"""Click extensions."""

import click


class MutuallyExclusiveOption(click.Option):
    """Add mutually exclusive options support for Click. Example::

    @click.option(
        "--dry",
        is_flag=True,
        cls=MutuallyExclusiveOption,
        mutually_exclusive=["wet"],
    )
    @click.option("--wet", is_flag=True)
    """

    def __init__(self, *args, **kwargs):
        self.mutually_exclusive = set(kwargs.pop("mutually_exclusive", []))
        help = kwargs.get("help", "")  # pylint: disable=redefined-builtin
        if self.mutually_exclusive:
            kwargs["help"] = help + (
                " NOTE: This argument is mutually exclusive with "
                f"arguments: [{', '.join(self.mutually_exclusive)}]."
            )
        super().__init__(*args, **kwargs)

    def handle_parse_result(self, ctx, opts, args):
        if self.mutually_exclusive.intersection(opts) and self.name in opts:
            raise click.UsageError(
                f"Illegal usage: '{self.name}' is mutually exclusive with "
                f"arguments: [{', '.join(self.mutually_exclusive)}]."
            )
        return super().handle_parse_result(ctx, opts, args)

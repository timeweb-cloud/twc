"""Typer eXtended."""

from typing import Optional, Union, Any, Type, Dict, Callable, Sequence, List

from typer import Typer
from typer.models import CommandFunctionType, CommandInfo, TyperInfo, Default
from typer.core import TyperCommand, TyperGroup


CONTEXT_SETTINGS = {"help_option_names": ["-h", "--help"]}


class TyperAlias(Typer):
    """Commands and groups aliases support for Typer."""

    # pylint: disable=redefined-builtin
    # pylint: disable=invalid-name

    def command(
        self,
        *names: Optional[Sequence[str]],
        cls: Optional[Type[TyperCommand]] = None,
        context_settings: Optional[Dict[Any, Any]] = None,
        help: Optional[str] = None,
        epilog: Optional[str] = None,
        short_help: Optional[str] = None,
        options_metavar: str = "[OPTIONS]",
        add_help_option: bool = True,
        no_args_is_help: bool = False,
        hidden: bool = False,
        deprecated: bool = False,
        rich_help_panel: Union[str, None] = Default(None),
    ) -> Callable[[CommandFunctionType], CommandFunctionType]:
        if cls is None:
            cls = TyperCommand
        if context_settings is None:
            context_settings = CONTEXT_SETTINGS

        name = None
        aliases = []

        # Split names to command name and aliases.
        if names:
            name = names[0]
            aliases = names[1:]

        def decorator(
            f: CommandFunctionType,
            help: Optional[str] = help,
            short_help: Optional[str] = short_help,
        ) -> CommandFunctionType:
            # Add aliases to command short_help
            if aliases:
                help_text = short_help or help or f.__doc__
                short_help = f"{help_text} (aliases: {', '.join(aliases)})"

            self.registered_commands.append(
                CommandInfo(
                    name=name,
                    cls=cls,
                    context_settings=context_settings,
                    callback=f,
                    help=help,
                    epilog=epilog,
                    short_help=short_help,
                    options_metavar=options_metavar,
                    add_help_option=add_help_option,
                    no_args_is_help=no_args_is_help,
                    hidden=hidden,
                    deprecated=deprecated,
                    rich_help_panel=rich_help_panel,
                )
            )
            for alias in aliases:
                # Register aliases as commands.
                # Note that aliases are hidden.
                self.registered_commands.append(
                    CommandInfo(
                        name=alias,
                        cls=cls,
                        context_settings=context_settings,
                        callback=f,
                        help=help,
                        epilog=epilog,
                        short_help=short_help,
                        options_metavar=options_metavar,
                        add_help_option=add_help_option,
                        no_args_is_help=no_args_is_help,
                        hidden=True,
                        deprecated=deprecated,
                        rich_help_panel=rich_help_panel,
                    )
                )
            return f

        return decorator

    def add_typer(
        self,
        typer_instance: "Typer",
        *,
        name: Optional[str] = Default(None),
        aliases: Optional[List[str]] = None,
        cls: Optional[Type[TyperGroup]] = Default(None),
        invoke_without_command: bool = Default(False),
        no_args_is_help: bool = Default(True),
        subcommand_metavar: Optional[str] = Default(None),
        chain: bool = Default(False),
        result_callback: Optional[Callable[..., Any]] = Default(None),
        # Command
        context_settings: Optional[Dict[Any, Any]] = Default(CONTEXT_SETTINGS),
        callback: Optional[Callable[..., Any]] = Default(None),
        help: Optional[str] = Default(None),
        epilog: Optional[str] = Default(None),
        short_help: Optional[str] = Default(None),
        options_metavar: str = Default("[OPTIONS]"),
        add_help_option: bool = Default(True),
        hidden: bool = Default(False),
        deprecated: bool = Default(False),
        # Rich settings
        rich_help_panel: Union[str, None] = Default(None),
    ) -> None:
        self.registered_groups.append(
            TyperInfo(
                typer_instance,
                name=name,
                cls=cls,
                invoke_without_command=invoke_without_command,
                no_args_is_help=no_args_is_help,
                subcommand_metavar=subcommand_metavar,
                chain=chain,
                result_callback=result_callback,
                context_settings=context_settings,
                callback=callback,
                help=help,
                epilog=epilog,
                short_help=short_help,
                options_metavar=options_metavar,
                add_help_option=add_help_option,
                hidden=hidden,
                deprecated=deprecated,
                rich_help_panel=rich_help_panel,
            )
        )

        if aliases is None:
            aliases = []

        # Add aliases into group short_help.
        for group in self.registered_groups:
            if aliases:
                if group.name == name:
                    help_text = (
                        group.typer_instance.info.short_help
                        or group.typer_instance.info.help
                    )
                    group.typer_instance.info.short_help = (
                        f"{help_text} (aliases: {', '.join(aliases)})"
                    )

        # Register aliases for groups.
        for alias in aliases:
            self.registered_groups.append(
                TyperInfo(
                    typer_instance,
                    name=alias,
                    cls=cls,
                    invoke_without_command=invoke_without_command,
                    no_args_is_help=no_args_is_help,
                    subcommand_metavar=subcommand_metavar,
                    chain=chain,
                    result_callback=result_callback,
                    context_settings=context_settings,
                    callback=callback,
                    help=help,
                    epilog=epilog,
                    short_help=short_help,
                    options_metavar=options_metavar,
                    add_help_option=add_help_option,
                    hidden=True,
                    deprecated=deprecated,
                    rich_help_panel=rich_help_panel,
                )
            )

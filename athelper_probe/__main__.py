"""athelper-probe entry point."""

import click

from athelper_probe.cmd_run import cmd_run
from athelper_probe.cmd_report import cmd_report
from athelper_probe.cmd_list_probes import cmd_list_probes
from athelper_probe.cmd_validate_target import cmd_validate_target


@click.group()
@click.version_option()
def main():
    """ATHelper red-team CLI."""


main.add_command(cmd_run, "run")
main.add_command(cmd_report, "report")
main.add_command(cmd_list_probes, "list-probes")
main.add_command(cmd_validate_target, "validate-target")


if __name__ == "__main__":
    main()

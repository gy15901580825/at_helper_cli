"""athelper-probe entry point."""

from uuid import UUID

import click

from athelper_probe import api_client
from athelper_probe.cmd_init import init_command
from athelper_probe.cmd_run import cmd_run
from athelper_probe.cmd_report import cmd_report
from athelper_probe.cmd_list_probes import cmd_list_probes
from athelper_probe.cmd_validate_target import cmd_validate_target


def _parse_org_id(ctx, param, value):
    if value is None:
        return None
    try:
        return str(UUID(value))
    except ValueError:
        raise click.BadParameter(f"{value!r} is not a valid organization UUID")


@click.group()
@click.version_option()
@click.option("--org-id", envvar="ATHELPER_ORG_ID", callback=_parse_org_id, help="Organization to act in, for users in several organizations (or env ATHELPER_ORG_ID). Default: your personal organization.")
def main(org_id):
    """ATHelper red-team CLI."""
    api_client.set_org_id(org_id)


main.add_command(init_command, "init")
main.add_command(cmd_run, "run")
main.add_command(cmd_report, "report")
main.add_command(cmd_list_probes, "list-probes")
main.add_command(cmd_validate_target, "validate-target")


if __name__ == "__main__":
    main()

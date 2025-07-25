"""Main CLI tool for ACTM."""

import click

from actm.common.config_reader import logger


@click.group(
    context_settings={
        "auto_envvar_prefix": "ACTM",
        "help_option_names": ["-h", "--help"],
        "show_default": True,
    }
)
@click.option(
    "--config",
    default="config/config.yml",
    type=click.Path(),
    help="Path to the configuration file.",
)
@click.option("--output-folder", type=click.Path(), help="Path to the output folder.")
@click.pass_context
def actmtoolbox():
    """Export activity listings from Active Mississauga."""
    logger.info("ACTM initialized.")


# DOWNLOAD COMMAND
@actmtoolbox.command("download")
@click.pass_context
def download():
    """Download data from the website."""


def main():
    """Run the ACTM toolbox."""
    actmtoolbox()
    logger.info("Active Mississauga Toolbox completed.")


if __name__ == "__main__":
    main()

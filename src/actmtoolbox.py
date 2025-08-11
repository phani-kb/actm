"""Main CLI tool for ACTM."""

import click
from pyfiglet import figlet_format

from actm.common.config_reader import logger
from actm.common.constants import APP_NAME, APP_VERSION


def print_banner():
    """Prints the ACTM banner using the app name and version from constants."""
    print(figlet_format(f"{APP_NAME} v{APP_VERSION}", font="slant"))


# Custom Click Group to show a banner for help
class BannerGroup(click.Group):
    """Custom Click Group to show a banner for help."""

    def get_help(self, ctx):
        print_banner()
        return super().get_help(ctx)


@click.group(
    context_settings={
        "auto_envvar_prefix": "ACTM",
        "help_option_names": ["-h", "--help"],
        "show_default": True,
    },
    cls=BannerGroup,
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
    print_banner()
    logger.info("ACTM initialized.")


# DOWNLOAD COMMAND


@actmtoolbox.command("download")
@click.pass_context
def download():
    """Download data from the website."""
    print_banner()


def main():
    """Run the ACTM toolbox."""
    actmtoolbox()
    logger.info("Active Mississauga Toolbox completed.")


if __name__ == "__main__":
    main()

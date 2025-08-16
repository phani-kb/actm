"""Main CLI tool for ACTM."""

import click
from pyfiglet import figlet_format
from webdriver_manager.chrome import ChromeDriverManager

from actm.common import utils
from actm.common.config_reader import ACTMConfig, ConfigReader, logger
from actm.common.constants import APP_NAME, APP_VERSION
from actm.common.enums import ACTMEnum, DataSaveFormat, DownloadType
from actm.downloaders.base_downloader import DownloaderFactory


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
    "config_path",
    default="config/config.yml",
    type=click.Path(),
    help="Path to the configuration file.",
)
@click.option("--output-folder", type=click.Path(), help="Path to the output folder.")
@click.pass_context
def actmtoolbox(ctx, config_path, output_folder):
    """CLI tool for Active Mississauga."""
    print_banner()
    config_reader = ConfigReader(config_path)
    if config_reader.config is None:
        logger.error("Failed to load configuration from %s", config_path)
        raise ValueError(f"Configuration could not be loaded from {config_path}")
    actm_config: ACTMConfig = config_reader.config
    if output_folder:
        actm_config.output_folder = output_folder
    ctx.obj = {"config": actm_config}
    logger.info("ACTM initialized with config: %s", config_reader.file_path)


def _get_all_subclasses(cls):
    """Recursively get all subclasses of a given class."""
    subclasses = set(cls.__subclasses__())
    for subclass in subclasses.copy():
        subclasses.update(_get_all_subclasses(subclass))
    return sorted(subclasses, key=lambda x: x.__name__)


def _get_chrome_driver_path(config: ACTMConfig) -> str:
    """Get the chrome driver path from config or install it."""
    chrome_driver_path = config.get("web_driver")
    if not chrome_driver_path or not isinstance(chrome_driver_path, str):
        chrome_driver_path = ChromeDriverManager().install()
        logger.info("Chrome driver path not found. Installing driver at: %s", chrome_driver_path)
    return chrome_driver_path


def _get_data_save_format(save_format: str, config: ACTMConfig) -> DataSaveFormat:
    """Get the data save format, CLI arg over config."""
    if save_format:
        format_obj = DataSaveFormat.from_id(save_format)
        if format_obj and isinstance(format_obj, DataSaveFormat):
            return format_obj

    activities_config = config.get_filters().get("activities", {})
    config_save_format = activities_config.get("save_format")
    if config_save_format:
        format_obj = DataSaveFormat.from_id(config_save_format)
        if format_obj and isinstance(format_obj, DataSaveFormat):
            return format_obj

    logger.info("Save format not found in config. Using default CSV.")
    return DataSaveFormat.CSV


def _handle_enum_display(enum_name: str):
    """Display details for the specified enum."""
    logger.info("Showing details for enum: %s", enum_name)
    all_subclasses = _get_all_subclasses(ACTMEnum)
    enum_class = next((cls for cls in all_subclasses if cls.__name__ == enum_name), None)

    if not enum_class:
        logger.error("Enum %s not found.", enum_name)
        return

    logger.info(enum_class.__doc__)
    options = enum_class.list()
    descriptions = [str(enum_class.from_id(opt.id)) for opt in options]
    utils.write_output(descriptions)


# DOWNLOAD COMMAND
@actmtoolbox.command("download")
@click.option("--dtype", type=click.Choice(DownloadType.supported_ids()), help="Type of download.")
@click.option(
    "--extract-data",
    is_flag=True,
    help="Extract the downloaded data based on the download type.",
)
@click.option(
    "--save-format",
    type=click.Choice(DataSaveFormat.ids()),
    default=DataSaveFormat.CSV.id,
    help="Save format.",
)
@click.option(
    "--enum",
    type=click.Choice([cls.__name__ for cls in _get_all_subclasses(ACTMEnum)]),
    help="Show details of the specified enum.",
)
@click.pass_context
def download(ctx, dtype, extract_data, save_format, enum):
    """Download data from the website."""
    config: ACTMConfig = ctx.obj["config"]

    if enum:
        _handle_enum_display(enum)
        return

    if not dtype:
        logger.error("Download type is required. Use --dtype option.")
        return

    download_type = DownloadType.from_id(dtype)
    if not download_type or not isinstance(download_type, DownloadType):
        logger.error("Invalid download_type: %s", dtype)
        return

    logger.info("Downloading data with type: %s", dtype)

    chrome_driver_path = _get_chrome_driver_path(config)
    data_save_format = _get_data_save_format(save_format, config)
    output_folder = config.output_folder

    logger.info("Save format: %s", data_save_format)

    downloader = DownloaderFactory.get_downloader(chrome_driver_path, download_type, output_folder)
    if not downloader:
        logger.error("Failed to create downloader for download type: %s", dtype)
        return

    if extract_data:
        if downloader.downloaded_file_exists(data_save_format):
            logger.info("Extracting data from existing downloaded file...")
            dtype_filters = config.get_filters().get(dtype, {})
            downloader.extract_data(data_save_format, dtype_filters)
        else:
            logger.error("Downloaded file does not exist. Cannot extract data.")
    else:
        downloader.download(download_type, config.home_url, data_save_format, config.filters)


def main():
    """Run the ACTM toolbox."""
    actmtoolbox.main()
    logger.info("Active Mississauga Toolbox completed.")


if __name__ == "__main__":
    main()

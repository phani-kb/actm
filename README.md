# ACTM

A tool to download and export activity listings from the Active Mississauga website, supporting filters and multiple output formats.

## Features

- Download and extract activities data
- Configurable filters for age, date, and other criteria
- Command-line interface for easy automation

## Installation

1. Clone the repository:

   ```bash
   git clone https://github.com/phani-kb/actm.git
   cd actm
   ```

2. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

3. (Optional) For development/editable install:

   ```bash
   pip install -e .
   pip install -r requirements-dev.txt
   ```

## Running

Examples:

```bash
actm --help
python src/actmtoolbox.py download --dtype activities
```

Example output:

```bash
              __                     ____   ___  ____ 
  ____ ______/ /_____ ___     _   __/ __ \ <  / / __ \
 / __ `/ ___/ __/ __ `__ \   | | / / / / / / / / / / /
/ /_/ / /__/ /_/ / / / / /   | |/ / /_/ / / /_/ /_/ / 
\__,_/\___/\__/_/ /_/ /_/    |___/\____(_)_/(_)____/  
                                                                                                            
                                                      
Usage: actm [OPTIONS] COMMAND [ARGS]...

   CLI tool for Active Mississauga.

Options:
   --config PATH         Path to the configuration file.  [default:
                                    config/config.yml]
   --output-folder PATH  Path to the output folder.
   -h, --help            Show this message and exit.  [default: False]

Commands:
   download  Download data from the website.
```

## License & Disclaimer for ACTM

## 1. License

This code is **copyrighted** and is provided for **personal, educational, and research use only**. You **may not**:

- Use this code for commercial purposes.
- Modify, distribute, or reproduce the code without explicit permission.
- Use the code to download data in violation of a website’s Terms of Service.

## 2. Data Usage Disclaimer

This project downloads publicly available data, but **does not guarantee legality** of downloading from specific websites. You are solely responsible for ensuring compliance with:

- The **Terms of Service** of any website you download from.
- **Applicable laws** regarding data collection and usage in your jurisdiction.

## 3. Liability

This software is provided **“as is”** without any warranties. The author **is not responsible** for any legal consequences, damages, or misuse resulting from using this code.

## 4. Contact

For questions or permissions, please open an issue.

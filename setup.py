#!/usr/bin/env python3
"""
Setup.py for ACTM.
"""

import os

from setuptools import find_packages, setup


# Read requirements from requirements.txt
def read_requirements():
    """Read requirements from requirements.txt."""
    req_file = os.path.join(os.path.dirname(__file__), "requirements.txt")
    with open(req_file, "r", encoding="utf-8") as f:
        return [line.strip() for line in f if line.strip() and not line.startswith("#")]


def read_dev_requirements():
    """Read development requirements from requirements-dev.txt."""
    dev_req_file = os.path.join(os.path.dirname(__file__), "requirements-dev.txt")
    if os.path.exists(dev_req_file):
        with open(dev_req_file, "r", encoding="utf-8") as f:
            return [line.strip() for line in f if line.strip() and not line.startswith("#")]
    return []


setup(
    name="actm",
    version="0.1.0",
    description="A tool to export activity listings from the Active Mississauga website.",
    author="Phani K",
    author_email="192951055+phani-kb@users.noreply.github.com",
    url="https://github.com/phani-kb/actm",
    package_dir={"": "src"},
    packages=find_packages(where="src", include=["actm*"]),
    py_modules=["actmtoolbox"],
    python_requires=">=3.10",
    install_requires=read_requirements(),
    extras_require={
        "dev": read_dev_requirements(),
    },
    entry_points={
        "console_scripts": [
            "actmtoolbox=actmtoolbox:actmtoolbox",
            "actm=actmtoolbox:actmtoolbox",
        ],
    },
    include_package_data=True,
    package_data={
        "": ["*.yml", "*.yaml", "*.txt"],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Topic :: Utilities",
        "Environment :: Console",
    ],
    keywords=[
        "cli",
        "csv",
        "toolbox",
        "toolkit",
        "tool",
        "mississauga",
        "activities",
    ],
    project_urls={
        "Homepage": "https://github.com/phani-kb/actm",
        "Repository": "https://github.com/phani-kb/actm",
        "Issues": "https://github.com/phani-kb/actm/issues",
    },
)

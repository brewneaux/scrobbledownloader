from setuptools import setup, find_packages
from os import path

with open("README.md") as fh:
    long_desc = fh.read()

with open('requirements.txt') as fh:
    requires = fh.readlines()

setup(
    name="scrobbledownloader",
    version="0.0.1",
    description="last.fm year in review download script",
    long_description=long_desc,
    packages=find_packages(),
    install_requires=requires,
    entry_points={"console_scripts": ["download-scrobbles=scrobbledownload.cli:cli"]},
)

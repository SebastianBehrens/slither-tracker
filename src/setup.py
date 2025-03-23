from setuptools import setup, find_packages

setup(
    name='slither',

    version='0.0.1',
    description="An application analyzing player performance in the game Slither.io.",

    long_description=open("../README.md").read(),
    long_description_content_type="text/markdown",

    author="Sebastian Behrens",
    maintainer="Sebastian Behrens",

    url="https://github.com/sebastianbehrens/slither-tracker",

    packages=find_packages()

)


from setuptools import setup, find_packages


with open("README.md") as f:
    readme = f.read()

with open("LICENSE") as f:
    license = f.read()

requires = ["bleak", "cobs", "pyserial", "pyserial-asyncio"]

setup(
    name="genki-wave",
    version="0.0.1",
    description="Repository to interface with the wave ring",
    long_description=readme,
    author="Robert Torfason",
    author_email="robert@genkiinstruments.com",
    url="https://github.com/genkiinstruments/genki-wave",
    license=license,
    packages=find_packages(exclude=("tests", "docs")),
    install_requires=requires,
)

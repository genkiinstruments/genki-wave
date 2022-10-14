from setuptools import setup, find_packages


with open("README.md") as f:
    readme = f.read()

requires = ["bleak", "cobs", "pyserial", "pyserial-asyncio"]

setup(
    name="genki-wave",
    version="0.4.1",
    description="Python API for Wave by Genki",
    long_description=readme,
    long_description_content_type="text/markdown",
    author="Robert Torfason",
    author_email="robert@genkiinstruments.com",
    url="https://github.com/genkiinstruments/genki-wave",
    license="MIT",
    classifiers=[
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: POSIX :: Linux",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
    ],
    python_requires=">=3.8",
    packages=find_packages(exclude=("tests", "docs")),
    install_requires=requires,
)

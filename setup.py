"""
Setup file for ff2zim
"""
from setuptools import setup


setup(
    name="ff2zim",
    version="0.1.0",
    description="Build ZIM files for fanfictions",
    long_description=open('README.md', "r").read(),
    long_description_content_type="text/markdown",
    keywords="ZIM fanfiction fanfic fanficfare",
    author="IMayBeABitShy",
    url="https://github.com/IMayBeABitShy/ff2zim",
    packages=[
        "ff2zim",
        ],
    include_package_data=True,
    install_requires=[
        "requests",
    ],
    entry_points={
        "console_scripts": [
            "ff2zim = ff2zim.cli:main",
        ],
    },
    classifiers=[
        "Development Status :: 3 - Alpha",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3 :: Only",
        "Topic :: Utilities",
        "Topic :: System :: Archiving",
    ],
)

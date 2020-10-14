# ff2zim

*ff2zim* is a tool for creating [*Zim*-Files](https://en.wikipedia.org/wiki/ZIM_(file_format)) containing fanfictions. At its core *ff2zim* uses [FanFicFare](https://github.com/JimmXinu/FanFicFare), but takes care of managing the files and provide additional functionality.

## Features

- Manage fanfiction downloads and updates
- Export as a ZIM file
- Export stories to EPUBs
- Interactive shell
- Gather statistics (total words, size)
- Special ffnet support (download entire categories, ...)



## Requirements

ff2zim requires:

- python3
- zimwriterfs
- [fanficfare](https://github.com/JimmXinu/FanFicFare)
- [BeautifulSoup4/bs4](https://pypi.org/project/beautifulsoup4/)
- [six](https://pypi.org/project/six/)

**Note:** Both *fanficfare* and *zimwriterfs* are called using the `subprocess` module. Please ensure that your `$PATH` is correctly configured. *fanficfare* also needs to be present as a python module.

## Install

Run `python3 setup.py install`.



## Basic Usage

### Start ff2zim

Run `ff2zim`.

### Create a new project

Skip this step if you already have a project.

A *Project* contains all settings, static resources, targets and downloaded fanfics.

Type `init <path-to-your-project-here>`  and press enter.

### Select a project

Type `select <path-to-your-project-here>`  and press enter.

### Add targets

A target is the URL for the fanfic to download.

Type `add <URL-to-your-fanfic-here>`  and press enter.

Alternatively, add `target_urls.txt` within the project directory directly. Each line should contain exactly one URL. Empty lines and lines starting with `#` will be ignored.

This step does not result in any downloads being started.

### Check missing targets

To see all not yet downloaded targets, use `list missing`.

### Download targets

Use either `download_all` or `download_n <N>` to download the fanfics.

### Check downloaded fanfics

To see all already downloaded targets, use `list_titles`.

### Build ZIM

To build the ZIM, use `build <outpath-here>`.

You should now have a ZIM file containing all downloaded fanfics.



## Terms

### Project

A *ff2zim project* refers to a specific directory and its contents. A project stores its configuration, state-related informations like targets and the actual downloaded fanfics.

### Target

A *target* represents a story to download. This is usually a URL to the fanfic.



## Advanced Usage


# ff2zim

*ff2zim* is a tool for creating [*Zim*-Files](https://en.wikipedia.org/wiki/ZIM_(file_format)) containing fanfictions.



## Status

ff2zim is currently being refactored and its scope heavily expanded. The unpublished version was a single file which only supported a single site.



## Requirements

ff2zim requires:

- python3
- zimwriterfs
- [fanficfare](https://github.com/JimmXinu/FanFicFare)

**Note:** Both *fanficfare* and *zimwriterfs* are called using the `subprocess` module. Please ensure that your `$PATH` is correctly configured.

## Install

Run `python3 setup.py install`



## Usage

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
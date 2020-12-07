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
- zimwriterfs (part of [zim-tools](https://github.com/openzim/zim-tools))
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

Type `init <path-to-your-project-here>` and press enter.

### Select a project

Type `select <path-to-your-project-here>` and press enter.

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

### Updating content

If some of the fanfics you have downloaded have been updated since then, you will probably want to update the fanfics. Fear not, *ff2zim* provides you with some nice tools for this task.

Just like the download, the update system is also state based. This means that the action to check for updates and the action to actually update are two separate actions. Also, a story is always updated completely, it will be completely downloaded again even if only a single new chapter has been added.

- If you have set up your IMAP accessible mail account to store update notifications in a specific mail directory, you can use the `check_imap_for_updates` command to search this mail directory for all **unread** emails, mark these read and then mark these for updates. Before the first time you do this, you'll have to execute the `imap_setup` command first.
- If you already know which story has been updated, you can use the `mark_for_update <story>` command to mark a single fanfic for update.
- If you want to update an entire ffnet category and download all new stories from there, use the `check_ffnet_category_for_update <category_url>` command.
- To see which fics require an update, use the `list_update_required` command.
- The `update_n` and `update_all` commands behave just like their download equivalents.

### Specifying options

You likely want to configure some build and download options. These options are grouped in so called `sections`. To change these options, you have two options:

- if you want to set the value of an option to a text/string value, you can use the `set_option <section> <option> <value>` command of the CLI.
- otherwise, you can edit the `project.json` file in the project directory directly.

**ZIM build options**

The options for changing how a ZIM file is build are in the `build` section.

- `title`: title of the ZIM. Default: `fanfiction archive`.
- `language`: language of the ZIM. Default: EN.
- `description`: description of the ZIM file. DEFAULT: `Archived fanfictions`.
- `creator`: The creator of the content. Default: `various`.
- `publisher`: The publisher of the ZIM, meaning you. Default: `UNKNOWN`.
- `minify`: Minify content. See below. Default: `false`
- `include_images`: include images in the build. Default: `true`.
- `include_epubs`: include epub files in the build. Default: `true`.

**Download options**

The options for downloading fanfics are in the `download` section.

Additionally, fanficfare has some default paths it will search for config files.


### Including and excluding content

**Images**

Images are included by default.

If you want images to be excluded from your download, set the `include_images` option of the `download` section to `false`.

If you only want these images excluded from your ZIM file but still want to download them, set the `include_images` option of the `build` section to `false`.

**EPUBs**

EPUBs are build together with the ZIM file by default.

To disable the EPUB build, set the `include_epubs` option of the `build` section to `false`.

You can also build EPUBs seperately by using the `generate_epubs [--by-category] [outdir]` command. If you specify `--by-category`, the generated EPUBs will be stored in subdirectories with the name of their category.


### Using subprojects

You can split a project into multiple subprojects. If you do this, building the toplevel project will also include the subprojects. The ZIM will then be build with the build options of the toplevel project.

**Advanatages of using subprojects:**

- thematic organization

- Use different combinations of subprojects and their stored fanfictions to produce various ZIM files while only having to store one copy of the fanfic.
- Specify various build configurations


To setup subprojects, edit the `subprojects.txt` file in the project root directory.

### Content minification

ff2zim allows automated minification of most of the generated content. Experience shows that the results were neglible, so it's disabled by default. To change this, set the `build`:`minify` option to `True`.

This requires additional dependencies. To specify that you want these installed during install, use the `minify` extra.

Practically, the content minification only allows for minimal size reduction. If you want to reduce the size of your ZIM file, consider to **not** include images and EPUBs.


## Attribution

The icon image was taken from [here](https://www.brandeps.com/icon/B/Book-03). According to the website, the it is licensed under the CC0 license.

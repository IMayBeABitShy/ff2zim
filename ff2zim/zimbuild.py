"""
This module contains the function to build a ZIM file from a project.
"""
import os
import subprocess
import tempfile
import json
import shutil

from .project import Project
from .exceptions import AlreadyExists
from .reporter import BaseReporter, VoidReporter
from .htmlpages import (
    create_index_page, create_stats_page,
    create_author_page, create_category_page,
    create_sort_script, create_style_file,
    )
from .utils import bleach_name


# BUILD DIRECTORY STRUCTURE
# ----------------------------
# BUILDIR/
# | Used for building the ZIM file
# |
# +-html/
#   | Contains the webpages to add
#   |
#   +-resources/
#   | | Contains static resource
#   | |
#   | +-favicon
#   | | The icon for the ZIM file
#   | |
#   | +-brython.js
#   | | The brython interpreter
#   | |
#   | +-sort.py
#   |   The sort and filter script
#   |
#   +-story/
#   | | Contains the stories.
#   | |
#   | +-ID/
#   | | | Story by id
#   | | | 
#   | | +-story.html
#   | |   The actual story, as an HTML file
#   | |
#   | ...
#   |
#   +-category/
#   | | The category/universe list
#   | |
#   | +-NAME/
#   | | | The universe by name
#   | | |
#   | | +-list.html
#   | | | The list of stories in this universe
#   | | |
#   | | +-stories.json
#   | |   Combined metadata of all stories in this universe
#   | |
#   | ...
#   |
#   +-author/
#     | The pages of the authors. Not the full pages, but information what stories are in our database.
#     |
#     +-ID/
#       | The author by id
#       |
#       +-author.html
#       | author information page
#       |
#       +-stories.json
#         Combined metadata of all stories by this author


def build_zim(project, outpath, reporter=None):
    """
    Build a project into a ZIM file.
    
    @param project: project to build
    @type path: L{ff2zim.project.Project}
    @param outpath: path to write ZIM to
    @type outpath: L{str}
    @param reporter: reporter used for status reports
    @type reporter: L{BaseReporter}
    """
    assert isinstance(project, Project)
    assert isinstance(outpath, str)
    assert isinstance(reporter, BaseReporter) or reporter is None
    
    if reporter is None:
        reporter = VoidReporter()
    
    if os.path.isdir(outpath):
        raise AlreadyExists("{} points to a directory.".format(outpath))
    
    with tempfile.TemporaryDirectory() as tempdir:
        reporter.msg("Using '{}' as build directory.".format(tempdir))
        
        # --------- prepare build ---------
        reporter.msg("Preparing build...")
        if not os.path.exists(tempdir):
            os.makedirs(tempdir)
        
        htmldir = os.path.join(tempdir, "html")
        if not os.path.exists(htmldir):
            os.mkdir(htmldir)
        
        # collect metadata
        reporter.msg("-> Collecting metadata... ", end="")
        metadata = project.collect_metadata()
        id2meta = {}
        category2ids = {"ALL": []}
        authordata = {}
        for e in metadata:
            storyid = e["storyId"]
            id2meta[storyid] = e
            category = e["category"]
            if category not in category2ids:
                category2ids[category] = [storyid]
            else:
                category2ids[category].append(storyid)
            category2ids["ALL"].append(storyid)
            authorid = e["authorId"]
            if authorid not in authordata:
                authordata[authorid] = {
                    "name": e["author"],
                    "id": authorid,
                    "url": e["authorUrl"],
                    "html": e["authorHTML"],
                    "stories": [storyid],
                }
            else:
                authordata[authorid]["stories"].append(storyid)
        reporter.msg("Done.")
        reporter.msg("   -> Found {} stories.".format(len(id2meta.keys())))
        reporter.msg("   -> Found {} categories.".format(len(category2ids.keys())))
        reporter.msg("   -> Found {} authors.".format(len(authordata.keys())))
        
        # copy resources
        reporter.msg("-> Preparing static resources... ", end="")
        resourcedir = os.path.join(htmldir, "resources")
        if not os.path.exists(resourcedir):
            os.mkdir(resourcedir)
        shutil.copyfile(
            os.path.join(project.path, "resources", "favicon.icon"),
            os.path.join(resourcedir, "favicon.icon"),
            )
        shutil.copyfile(
            os.path.join(project.path, "resources", "brython.js"),
            os.path.join(resourcedir, "brython.js"),
        )
        # shutil.copyfile(
        #     os.path.join(path, "resources", "brython_stdlib.js"),
        #     os.path.join(resourcedir, "brython_stdlib.js"),
        # )
        sortpath = os.path.join(resourcedir, "sort.py")
        create_sort_script(sortpath)
        csspath = os.path.join(resourcedir, "styles.css")
        create_style_file(csspath)
        reporter.msg("Done.")
        
        # copy stories
        reporter.msg("-> Copying stories... ", end="")
        ncopied = 0
        storydir = os.path.join(htmldir, "stories")
        if not os.path.exists(storydir):
            os.mkdir(storydir)
        for sid in id2meta.keys():
            srcdir = os.path.join(project.path, "fanfics", str(sid))
            src = os.path.join(srcdir, "story.html")
            dstdir = os.path.join(storydir, str(sid))
            dst = os.path.join(dstdir, "story.html")
            if not os.path.exists(dstdir):
                os.mkdir(dstdir)
            shutil.copyfile(src, dst)
            ncopied += 1
        reporter.msg("Done.")
        reporter.msg("   -> Copied {} files.".format(ncopied))
        
        # create category pages
        reporter.msg("-> Creating category pages... ", end="")
        category_dir = os.path.join(htmldir, "category")
        if not os.path.exists(category_dir):
            os.mkdir(category_dir)
        ncreated = 0
        for category in category2ids:
            catdir = os.path.join(category_dir, bleach_name(category))
            if not os.path.exists(catdir):
                os.mkdir(catdir)
            listfile = os.path.join(catdir, "list.html")
            create_category_page(listfile, category)
            metafile = os.path.join(catdir, "stories.json")
            combined_meta = [e for e in metadata if e["storyId"] in category2ids[category]]
            with open(metafile, "w") as fout:
                json.dump(combined_meta, fout)
            ncreated += 1
        reporter.msg("Done.")
        reporter.msg("   -> Created {} pages.".format(ncreated))
        
        # create author pages
        reporter.msg("Creating author pages... ", end="")
        author_dir = os.path.join(htmldir, "author")
        if not os.path.exists(author_dir):
            os.mkdir(author_dir)
        ncreated = 0
        for authorid in authordata:
            authorinfo = authordata[authorid]
            authorpath = os.path.join(author_dir, str(authorid))
            create_author_page(authorpath, authorinfo, id2meta)
            ncreated += 1
        reporter.msg("Done.")
        reporter.msg("   -> Created {} pages".format(ncreated))
        
        # create index page
        reporter.msg("Creating index page... ", end="")
        indexpath = os.path.join(htmldir, "index.html")
        create_index_page(indexpath, id2meta, category2ids, authordata)
        reporter.msg("Done.")
        
        # create statpage
        reporter.msg("Creating statistics page... ", end="")
        statpath = os.path.join(htmldir, "stats.html")
        create_stats_page(statpath, id2meta, category2ids, authordata)
        reporter.msg("Done.")
        
        # ---------- actual build -----------
        
        # gather buildoptions
        reporter.msg("Collecting build options... ", end="")
        title       = project.get_option("build", "title", "fanfiction archive")
        language    = project.get_option("build", "language", "EN")
        description = project.get_option("build", "description", "Archived fanfictions")
        creator     = project.get_option("build", "creator", "various")
        publisher   = project.get_option("build", "publisher", "UNKNOWN")
        reporter.msg("Done.")
        
        # build zim
        reporter.msg("Building...")
        subprocess.check_call(
            [
                "zimwriterfs",
                "-w", "index.html",
                "-f", "resources/favicon.icon",
                "-l", language,
                "-t", title,
                "-d", description,
                "-c", creator,
                "-p", publisher,
                "-i",
                htmldir,
                outpath,
            ],
        )
        reporter.msg("Done.")

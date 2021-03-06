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
    create_cover_page, create_simplelist,
    )
from .utils import bleach_name
from .epubconverter import Html2EpubConverter
from .minify import minify_file, minify_metadata


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
#   | +-ABBREV-ID/
#   | | | Story by abbev+id combination
#   | | |
#   | | +-cover.html
#   | | | The cover page for the story, providing informations and links.
#   | | | 
#   | | +-story.html
#   | | | The actual story, as an HTML file
#   | | |
#   | | +-story.epub
#   | |   The story in epub format (if include_epubs==True)
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
#   | | | Combined metadata of all stories in this universe
#   | | |
#   | | +-simplelist.html
#   | |   A simple, non-javascript list of stories.
#   | |
#   | ...
#   |
#   +-author/
#   | | The pages of the authors. Not the full pages, but information what stories are in our database.
#   | |
#   | +-ABBREV-ID/
#   |   | The author by abbrev+id combo
#   |   |
#   |   +-author.html
#   |   | author information page
#   |   |
#   |   +-stories.json
#   |     Combined metadata of all stories by this author
#   |
#   +-index.html
#   | The index page
#   |
#   +-stats.html
#     Statistics about the zimfile.




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
    
    projects = [project] + project.get_subprojects()
    
    with tempfile.TemporaryDirectory() as tempdir:
        reporter.msg("Using '{}' as build directory.".format(tempdir))
        
        # --------- prepare build ---------
        reporter.msg("Preparing build...")
        if not os.path.exists(tempdir):
            os.makedirs(tempdir)
        
        reporter.msg("-> Creating build directory... ", end="")
        htmldir = os.path.join(tempdir, "html")
        if not os.path.exists(htmldir):
            os.mkdir(htmldir)
        reporter.msg("Done.")
        
        # gather buildoptions
        reporter.msg("-> Collecting build options... ", end="")
        minify          = project.get_option("build", "minify", False)
        include_images  = project.get_option("build", "include_images", True)
        build_epubs     = project.get_option("build", "include_epubs", True)
        zim_title       = project.get_option("build", "title", "fanfiction archive")
        zim_language    = project.get_option("build", "language", "EN")
        zim_description = project.get_option("build", "description", "Archived fanfictions")
        zim_creator     = project.get_option("build", "creator", "various")
        zim_publisher   = project.get_option("build", "publisher", "UNKNOWN")
        reporter.msg("Done.")
        
        # collect metadata
        reporter.msg("-> Collecting metadata... ", end="")
        # metadata = project.collect_metadata()
        
        id2meta = {}
        metadata = []
        category2ids = {"ALL": []}
        authordata = {}
        projects_and_fsids = []
        for proj in projects:
            fsids = []
            for e in proj.collect_metadata(include_subprojects=False):
                abbrev = e["siteabbrev"]
                storyid = "{}-{}".format(abbrev, e["storyId"])
                if storyid in id2meta:
                    # prevent duplicates
                    # TODO: better take last updated here
                    continue
                fsids.append(storyid)
                metadata.append(e)
                id2meta[storyid] = e
                category = e["category"]
                if category not in category2ids:
                    category2ids[category] = [storyid]
                else:
                    category2ids[category].append(storyid)
                category2ids["ALL"].append(storyid)
                authororgid = e["authorId"]
                authorid = "{}-{}".format(abbrev, authororgid)
                if authorid not in authordata:
                    authordata[authorid] = {
                        "name": e["author"],
                        "id": authororgid,
                        "url": e["authorUrl"],
                        "html": e["authorHTML"],
                        "stories": [storyid],
                    }
                else:
                    authordata[authorid]["stories"].append(storyid)
            projects_and_fsids.append((proj, fsids))
        reporter.msg("Done.")
        n_stories = len(id2meta.keys())
        n_categories = len(category2ids.keys())
        n_authors = len(authordata.keys())
        reporter.msg("   -> Found {} stories.".format(n_stories))
        reporter.msg("   -> Found {} categories.".format(n_categories))
        reporter.msg("   -> Found {} authors.".format(n_authors))
        
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
        create_sort_script(sortpath, minify=minify)
        csspath = os.path.join(resourcedir, "styles.css")
        create_style_file(csspath, minify=minify)
        reporter.msg("Done.")
        
        # copy stories
        reporter.msg("Copying stories...")
        for proj, fsids in projects_and_fsids:
            reporter.msg("-> {}".format(proj.path))
            nscopied = 0
            nicopied = 0
            desc = "   -> Copying {}stories".format("minified " if minify else "")
            if include_images:
                desc += " and images"
            if build_epubs:
                desc += ", building EPUBs"
            desc += "..."
            with reporter.with_progress(desc, len(fsids)) as pb:
                storydir = os.path.join(htmldir, "stories")
                if not os.path.exists(storydir):
                    os.mkdir(storydir)
                for fsid in fsids:
                    # story
                    storydata = id2meta[fsid]
                    abbrev, sid = storydata["siteabbrev"], storydata["storyId"]
                    srcdir = os.path.join(proj.path, "fanfics", abbrev, sid)
                    src = os.path.join(srcdir, "story.html")
                    dstdir = os.path.join(storydir, fsid)
                    dst = os.path.join(dstdir, "story.html")
                    if not os.path.exists(dstdir):
                        os.mkdir(dstdir)
                    shutil.copyfile(src, dst)
                    if minify:
                        minify_file(dst)
                    nscopied += 1
                    # images
                    if include_images:
                        simgd = os.path.join(srcdir, "images")
                        if os.path.exists(simgd):
                            dimgd = os.path.join(dstdir, "images")
                            shutil.copytree(simgd, dimgd)
                            nicopied += len(os.listdir(dimgd))
                    # epub
                    if build_epubs:
                        epubdest = os.path.join(dstdir, "story.epub")
                        converter = Html2EpubConverter(srcdir)
                        converter.parse()
                        converter.write(epubdest)
                    # cover page
                    coverpagepath = os.path.join(dstdir, "cover.html")
                    create_cover_page(
                        coverpagepath,
                        fsid, 
                        id2meta[fsid],
                        include_images=include_images,
                        include_epubs=build_epubs,
                        minify=minify,
                        )
                    # advance progress bar
                    pb.advance(1)
            # reporter.msg("Done.")
            reporter.msg("   -> Copied {} stories".format(nscopied), end="")
            if include_images:
                reporter.msg(" and {} images".format(nicopied), end="")
            reporter.msg(".")
        
        # create category pages
        with reporter.with_progress("-> Creating category pages... ", n_categories) as pb:
            category_dir = os.path.join(htmldir, "category")
            if not os.path.exists(category_dir):
                os.mkdir(category_dir)
            ncreated = 0
            for category in category2ids:
                catdir = os.path.join(category_dir, bleach_name(category))
                if not os.path.exists(catdir):
                    os.mkdir(catdir)
                # create category page
                listfile = os.path.join(catdir, "list.html")
                create_category_page(listfile, category, minify=minify)
                # dump metadata
                metafile = os.path.join(catdir, "stories.json")
                combined_meta = [e for e in metadata if "{}-{}".format(e["siteabbrev"], e["storyId"]) in category2ids[category]]
                if minify:
                    minify_metadata(metadata)
                with open(metafile, "w") as fout:
                    json.dump(combined_meta, fout)
                # create simplified list
                simplelistfile = os.path.join(catdir, "simplelist.html")
                create_simplelist(simplelistfile, category, id2meta, category2ids[category], minify=minify)
                
                ncreated += 1
                pb.advance(1)
        # reporter.msg("Done.")
        reporter.msg("   -> Created {} pages.".format(ncreated))
        
        # create author pages
        with reporter.with_progress("Creating author pages... ", n_authors) as pb:
            author_dir = os.path.join(htmldir, "author")
            if not os.path.exists(author_dir):
                os.mkdir(author_dir)
            ncreated = 0
            for authorid in authordata:
                authorinfo = authordata[authorid]
                authorpath = os.path.join(author_dir, str(authorid))
                create_author_page(authorpath, authorinfo, id2meta, minify=minify)
                
                ncreated += 1
                pb.advance(1)
        # reporter.msg("Done.")
        reporter.msg("   -> Created {} pages".format(ncreated))
        
        # create index page
        reporter.msg("Creating index page... ", end="")
        indexpath = os.path.join(htmldir, "index.html")
        create_index_page(indexpath, id2meta, category2ids, authordata, minify=minify)
        reporter.msg("Done.")
        
        # create statpage
        reporter.msg("Creating statistics page... ", end="")
        statpath = os.path.join(htmldir, "stats.html")
        create_stats_page(statpath, id2meta, category2ids, authordata, minify=minify)
        reporter.msg("Done.")
        
        # ---------- actual build -----------
        
        # build zim
        reporter.msg("Building...")
        subprocess.check_call(
            [
                "zimwriterfs",
                "-w", "index.html",
                "-f", "resources/favicon.icon",
                "-l", zim_language,
                "-t", zim_title,
                "-d", zim_description,
                "-c", zim_creator,
                "-p", zim_publisher,
                "-i",
                "-u",  # because namespaces will be removed
                htmldir,
                outpath,
            ],
        )
        reporter.msg("Done.")

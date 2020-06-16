"""
This module contains the project class, which is responsible for
managing the data and paths.
"""
import os
import json

from .exceptions import NotAValidProject, AlreadyExists, DirectoryNotEmpty
from .reporter import BaseReporter, VoidReporter
from .fileutils import create_file_with_content, append_to_file, download_file, copy_resource_file
from .target import Target
from .converter import get_metadata_converter


# DIRECTORY STRUCTURE
# --------------------------------
# PROJECTDIR/
# | Contains instructions and caches
# |
# +-fanfics/
# | | Contains fanfics and their metadata
# | |
# | +-ABBREV/
# | | | Contains fanfic directories by their site abbreviation
# | | |
# | | +-ID/
# | | | |Contains data for the fanfic with the specified ID
# | | | |
# | | | +-story.html
# | | | | Contains the HTML content of chapter 1
# | | | |
# | | | +-metadata.json
# | | |  Contains the metadata of this fanfic
# | | |
# | | +- ...
# | |
# | +- ...
# |
# +-resources/
# | | Contains other resources, e.g. favicon.png
# | |
# | +-favicon.ico
# |
# +-target_urls.txt
# |  A list of URLs, one per line, which to download and include.
# |
# +-project.json
#    Contains other project data.


TARGETLIST_DEFAULT_CONTENT = """
# Welcome to ff2zim.
# Please add the fanfics you want to download to this file.
# Each line should contain exactly one fanficfare compatible URL.
# lines starting with '#' will be ignored.
"""

PROJECT_JSON_DEFAULT_CONTENT = """
{
    "version": "0.2",
}
"""



class Project(object):
    """
    A ff2zim project.
    
    A Project manages configuration, targets and raw data.
    
    @ivar path: path of the project
    @type path: L{str}
    """
    
    def __init__(self, path):
        if not self.is_valid_project(path):
            raise NotAValidProject(
                "Path '{}' does not point to a valid project.".format(path),
                )
        self.path = path

    @classmethod
    def init_new(cls, path, reporter=None):
        """
        Prepare a project directory and populate it.
        
        This directory will be created if neccessary, but not it's parent directories.
        If it already exists and is not empty, an error is raised.
        
        @param path: path to init
        @type path: L{str}
        @param reporter: reporter used for status reports
        @type reporter: L{ff2zim.reporter.BaseReporter}
        
        @raises: L{ff2zim.exceptions.DirectoryNotEmpty}
        @raises: L{ff2zim.exceptions.AlreadyExists}
        
        @return: the new project
        @rtype: L{Project}
        """
        assert isinstance(path, str)
        assert isinstance(reporter, BaseReporter) or reporter is None
        
        if reporter is None:
            reporter = VoidReporter()
        
        if cls.is_valid_project(path):
            raise AlreadyExists("Already a valid project!")
        
        reporter.msg("Initiating a new project in '{}'...".format(path))
        
        if not os.path.exists(path):
            reporter.msg("Creating: {}".format(path))
            os.mkdir(path)
        else:
            reporter.msg("Path '{}' already exists, reusing it if not empty.".format(path))
        if not len(os.listdir(path)) == 0:
            raise DirectoryNotEmpty("Path '{}' is not empty!".format(path))
        
        create_file_with_content(os.path.join(path, "project.json"), PROJECT_JSON_DEFAULT_CONTENT)
        create_file_with_content(os.path.join(path, "target_urls.txt"), TARGETLIST_DEFAULT_CONTENT)
        cls.populate_resources(path, reporter=reporter)
        
        reporter.msg("Project initialized.")
        
        return cls(path)
    
    @staticmethod
    def is_valid_project(path):
        """
        Check whether path refers to a valid project.
        
        @param path: path to check
        @type path: L{str}
        
        @return: whether path refers to a valid project
        @rtype: L{bool}
        """
        assert isinstance(path, str)
        
        if not os.path.exists(path):
            return False
        if not os.path.isdir(path):
            return False
        pp = os.path.join(path, "project.json")
        if not os.path.exists(pp):
            return False
        if not os.path.isfile(pp):
            return False
        return True
    
    def get_option(self, category, name=None, default=None):
        """
        Get a config option.
        
        @param category: name of option category
        @type category: L{str}
        @param name: name of option. If omitted, return value for category.
        @type name: L{str}
        @param default: default to return if category/name not found
        @type default: anything
        """
        pf = os.path.join(self.path, "project.json")
        with open(pf, "r") as fin:
            content = json.load(fin)
        if category not in content:
            return default
        if name is None:
            return content[category]
        elif name not in content[category]:
            return default
        else:
            return content[category][name]
    
    
    def set_option(self, category, name, value):
        """
        Set a config option.
        
        @param category: name of option category
        @type category: L{str}
        @param name: name of option. If omitted, set value for category.
        @type name: L{str}
        @param value: value to set
        @type value: any json-serialzeable type
        """
        pf = os.path.join(self.path, "project.json")
        with open(pf, "r") as fin:
            content = json.load(fin)
        if name is None:
            content[category] = value
        else:
            if category not in content:
                content[category] = {}
            content[category][name] = value
        with open(pf, "w") as fout:
            json.dump(content, fout)
        
    
    @classmethod
    def populate_resources(cls, path, reporter=None):
        """
        Populate the project with static resources.
        
        Existing resources will be overwriten.
        
        @param path: path to populate
        @type path: L{str}
        @param reporter: reporter used for status reports
        @type reporter: L{ff2zim.reporter.BaseReporter} or L{None}
        """
        if not cls.is_valid_project(path):
            raise NotAValidProject(path)
        reporter.msg("Populating static resources...")
        resource_path = os.path.join(path, "resources")
        if not os.path.exists(resource_path):
            os.mkdir(resource_path)
        faviconpath = os.path.join(resource_path, "favicon.icon")
        reporter.msg("Creating favicon.icon... ", end="")
        copy_resource_file("favicon.icon", faviconpath)
        reporter.msg("Done.")
        
        brythonpath = os.path.join(resource_path, "brython.js")
        brythonlibpath = os.path.join(resource_path, "brython_stdlib.js")
        reporter.msg("Downloading brython.js... ", end="")
        download_file("https://brython.info/src/brython.js", brythonpath)
        reporter.msg("Done.")
        reporter.msg("Downloading brython_stdlib.js...", end="")
        download_file("https://brython.info/src/brython_stdlib.js", brythonlibpath)
        reporter.msg("Done.")
    
    
    def add_target(self, target):
        """
        Add a target to the target list.
        
        @param target: target to add
        @type target: L{str} or L{int}
        """
        # check that target is valid
        t = Target(target)
        
        tp = os.path.join(self.path, "target_urls.txt")
        append_to_file(tp, t.url + "\n")
        
    
    
    def list_targets(self, exclude_existing=False):
        """
        List all URLs to download.
        
        @param exclude_existing: If nonzero, do not include URLs which are already downloaded.
        @type exclude_existing: L{bool}
        
        @return: list of Targets to download
        @rtype: L{list} of L{ff2zim.target.Target}
        """
        assert isinstance(exclude_existing, bool)
        tp = os.path.join(self.path, "target_urls.txt")
        if not os.path.exists(tp):
            return []
        targets = []
        # read target list
        with open(tp, "r") as fin:
            for line in fin:
                line = line.strip()
                if line.startswith("#"):
                    # ignore comments
                    continue
                elif line == "":
                    # ignore empty lines
                    continue
                else:
                    target = Target(line)
                    if target not in targets:
                        # only add if not a duplicate
                        targets.append(target)
        
        if exclude_existing:
            # remove existing URLs.
            targets = list(filter(lambda x: not self.has_target_locally(x), targets))
        
        return targets
    
    
    def has_target(self, target):
        """
        Check if a target is defined for this project
        
        @param target: target to check
        @type target: L{ff2zim.target.Target} or L{str}
        
        @return: True if target already exists
        @rtype: L{bool}
        """
        if not isinstance(target, Target):
            target = Target(target)
        targets = self.list_targets(exclude_existing=False)
        return (target in targets)
    
    
    def has_target_locally(self, target):
        """
        Check if the given fanfic is already stored locally.
        
        @param target: target to check
        @type target: L{ff2zim.target.Target} or L{str}
        
        @return: True if it is already stored locally
        @rtype: L{bool}
        """
        if not isinstance(target, Target):
            target = Target(target)
        fp = os.path.join(self.path, "fanfics", target.subpath)
        if os.path.exists(fp):
            return True
        else:
            return False
    
    
    def collect_metadata(self, reporter=None):
        """
        Return the combined metadata of all fanfics.
        
        This will be a list of the individual metadata.
        
        @param reporter: reporter used for status reports
        @type reporter: L{ff2zim.reporter.BaseReporter}
        
        @return: the combined metadata
        @rtype: L{list} of L{dict}
        """
        if reporter is None:
            reporter = VoidReporter()
        
        fp = os.path.join(self.path, "fanfics")
        if not os.path.exists(fp):
            # empty
            return []
        aliases = self.get_category_aliases()
        am = []
        for abbrev in os.listdir(fp):
            sp = os.path.join(fp, abbrev)
            story_ids = sorted(os.listdir(sp))
            for sid in story_ids:
                smp = os.path.join(sp, sid, "metadata.json")
                if not os.path.exists(smp):
                    reporter.msg("WARNING: Story {} has no metadata!".format(sid))
                    continue
                with open(smp, "r") as fin:
                    content = json.load(fin)
                
                # convert site dependent values
                converter = get_metadata_converter(abbrev)
                content = converter.convert(content)
                
                # resolve aliases
                if "category" in content:
                    content["category"] = aliases.get(content["category"], content["category"])
                am.append(content)
        return am
    
    def add_category_alias(self,from_, to):
        """
        Define a alias for a category.
        Afterwards, categories from the 'from_' category will be handled
        as if they were from the 'to' category.
        
        @param from_: category which should be considered an alias
        @type from_: L{str}
        @param to: category which 'from_' should be considered an alias of
        @type to: L{str}
        """
        p = os.path.join(self.path, "aliases.json")
        if os.path.exists(p):
            with open(p, "r") as fin:
                aliases = json.load(fin)
        else:
            aliases = {}
        aliases[from_] = to
        with open(p, "w") as fout:
            json.dump(aliases, fout)
    
    def get_category_aliases(self):
        """
        Return all category aliases.
        
        @return: a dict mapping src->dst aliases
        @rtype: L{dict} of L{str} -> L{str}
        """
        p = os.path.join(self.path, "aliases.json")
        if os.path.exists(p):
            with open(p, "r") as fin:
                aliases = json.load(fin)
        else:
            aliases = {}
        return aliases

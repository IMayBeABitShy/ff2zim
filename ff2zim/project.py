"""
This module contains the project class, which is responsible for
managing the data and paths.
"""
import os
import json

from .exceptions import NotAValidProject, NotAValidTarget, AlreadyExists, DirectoryNotEmpty
from .reporter import BaseReporter, VoidReporter
from .fileutils import create_file_with_content, append_to_file, download_file, copy_resource_file
from .utils import str_to_int
from .targetutils import get_id_from_url, is_valid_url_or_id


TARGETLIST_DEFAULT_CONTENT = """
# Welcome to ff2zim.
# Please add the fanfics you want to download to this file.
# Each line should contain exactly one URL pointing to a fanfic.
# lines starting with '#' will be ignored.
"""

PROJECT_JSON_DEFAULT_CONTENT = """
{
    "version": "0.1",
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
            raise NotAValidProject("Path '{}' does not point to a valid project.")
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
        if not is_valid_url_or_id(target):
            raise NotAValidTarget(target)
        tp = os.path.join(self.path, "target_urls.txt")
        append_to_file(tp, str(target) + "\n")
        
    
    
    def list_targets(self, exclude_existing=False):
        """
        List all URLs to download.
        
        @param exclude_existing: If nonzero, do not include URLs which are already downloaded.
        @type exclude_existing: L{bool}
        
        @return: list of URLs to download
        @rtype: L{list} of L{str}
        """
        assert isinstance(exclude_existing, bool)
        tp = os.path.join(self.path, "target_urls.txt")
        if not os.path.exists(tp):
            return []
        lines = []
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
                elif line in lines:
                    # ignore duplicates
                    continue
                else:
                    lines.append(line)
        
        if exclude_existing:
            # remove existing URLs.
            lines = list(filter(lambda x: not self.has_fanfic(x), lines))
        
        return lines
    
    
    def has_target(self, target):
        """
        Check if a target is defined for this project
        
        @param target: target to check
        @type target: L{str} or L{int}
        
        @return: True if target already exists
        @rtype: L{bool}
        """
        if isinstance(target, int):
            sid = target
        elif isinstance(target, str):
            sid = get_id_from_url(target)
            if sid is None:
                raise NotAValidTarget(target)
        else:
            raise NotAValidTarget(target)
        targets = self.list_targets(exclude_existing=False)
        targets = [get_id_from_url(u) for u in targets]
        return (sid in targets)
    
    
    def has_fanfic(self, id_or_url):
        """
        Check if the given fanfic is already stored locally.
        
        @param id_or_url: ID or URL of fanfic to check
        @type id_or_url: L{int} or L{str}
        
        @return: True if it is already stored locally
        @rtype: L{bool}
        """
        if isinstance(id_or_url, int):
            fid = id_or_url
        elif isinstance(id_or_url, str):
            fid = get_id_from_url(id_or_url)
        else:
            raise TypeError("Got Value with unknown type: {}!".format(repr(id_or_url)))
        fp = os.path.join(self.path, "fanfics", str(fid))
        if os.path.exists(fp):
            return True
        else:
            return False
    
    
    def collect_metadata(self):
        """
        Return the combined metadata of all fanfics.
        
        This will be a list of the individual metadata.
        
        @return: the combined metadata
        @rtype: L{list} of L{dict}
        """
        fp = os.path.join(self.path, "fanfics")
        if not os.path.exists(fp):
            # empty
            return []
        story_ids = sorted(os.listdir(fp))
        am = []
        for sid in story_ids:
            smp = os.path.join(fp, sid, "metadata.json")
            if not os.path.exists(smp):
                reporter.msg("WARNING: Story {} has no metadata!".format(sid))
                continue
            with open(smp, "r") as fin:
                content = json.load(fin)
            # rewrite content
            content["authorId"] = int(content.get("authorId", "0"))
            content["favs"] = str_to_int(content.get("favs", "0"))
            content["follows"] = str_to_int(content.get("follows", "0"))
            content["numChapters"] = str_to_int(content.get("numChapters", "0"))
            content["numWords"] = str_to_int(content.get("numWords", "0"))
            content["reviews"] = str_to_int(content.get("reviews", "0"))
            content["storyId"] = int(content.get("storyId", "0"))
            am.append(content)
        return am
    
    def download_target(id_or_url, reporter=None):
        """
        Download the target
        
        @param id_or_url: ID or URL to download.
        @type id_or_url: L{int} or L{str}
        @param reporter: reporter for status reports
        @type reporter: L{ff2zim.reporter.BaseReporter}
        """
        assert isinstance(reporter, BaseReporter) or reporter is None
        
        if reporter is None:
            reporter = VoidReporter()
        
        if not is_valid_url_or_id(id_or_url):
            raise NotAValidTarget(id_or_url)
        
        if isinstance(id_or_url, str):
            if id_or_url.isdigit():
                fid = int(id_or_url)
                url = get_url_for_id(fid)
            else:
                url = id_or_url
                fid = get_id_from_url(url)
        else:
            fid = id_or_url
            url = get_url_for_id(fid)
        
        fanfic_path = os.path.join(path, "fanfics")
        target_path = os.path.join(fanfic_path, str(fid))
        story_path = os.path.join(target_path, "story.html")
        metadata_path = os.path.join(target_path, "metadata.json")
        
        if os.path.exists(story_path):
            raise AlreadyExists("Story already exists!")
        
        reporter.msg("Downloading: {}... ".format(url), end="")
        
        try:
            output = subprocess.check_output(
                [
                    "fanficfare",
                    "-f", "html",
                    "-j",
                    "-o", "is_adult=true",
                    "-o", "output_filename={t}{s}${{storyId}}{s}story${{formatext}}".format(t=fanfic_path, s=os.sep),
                    url,
                    ],
                universal_newlines=True,
                )
        except subprocess.CalledProcessError:
            reporter.msg("Error.\nCleaning up...")
            if os.path.exists(target_path):
                shutil.rmtree(target_path)
            reporter.msg("Done.")
        else:
            reporter.msg("Done.\nSaving Metadata... ", end="")
            # dump output into metadata
            with open(metadata_path, "w") as fout:
                fout.write(output)
            reporter.msg("Done.")
    

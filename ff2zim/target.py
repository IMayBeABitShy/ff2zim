"""
This module defines the Target class, which is used to specify a
specific fanfiction to download.
"""
import os
import subprocess
import shutil

from fanficfare import adapters
from fanficfare.configurable import Configuration
from fanficfare.exceptions import UnknownSite

from .exceptions import NotAValidTarget, AlreadyExists
from .utils import bleach_name
from .reporter import BaseReporter, VoidReporter


class Target(object):
    """
    This class represents a target to download.
    
    @ivar url: url to story
    @type url: L{str}
    @ivar abbrev: site abbreviation
    @type abbrev: L{str}
    @ivar id: the ID of this target. Should be unique for this abbrev.
    @type id: L{str}
    @ivar subpath: local subpath to this target
    @type subpath: L{str}
    """
    
    def __init__(self, url):
        self.url = url
        configuration = Configuration(["test1.com"], "HTML", lightweight=True)
        try:
            adapter = adapters.getAdapter(configuration, url)
        except UnknownSite:
            raise NotAValidTarget(url)
        self.abbrev = adapter.story.getMetadata("siteabbrev")
        if self.abbrev is None:
            self.abbrev = "unknown"
        self.id = adapter.story.getMetadata("storyId")
        if self.id is None:
            self.id = self._id_from_url(url)
    
    @staticmethod
    def _id_from_url(url):
        """
        Generate a ID from a URL.
        
        @param url: url to generate ID from
        @type url: L{str}
        @return: the new ID
        @rtype: L{str}
        """
        return bleach_name(url)
    
    @property
    def subpath(self):
        return os.path.join(self.abbrev, self.id)
    
    
    def __str__(self):
        return self.url
    
    def __eq__(self, other):
        if not isinstance(other, Target):
            return False
        return (self.abbrev == other.abbrev) and (self.id == other.id)
    
    def __cmp__(self, other):
        if not isinstance(other, Target):
            return -1
        e1 = (self.abbrev, self.id)
        e2 = (other.abbrev, other.id)
        return (e1 > e2) - (e1 < e2)
    
    def download(self, project, reporter=None):
        """
        Download the target into the specified project.
        
        @param project: project to download into
        @type project: L{ff2zim.project.Project}
        @param reporter: reporter for status reports
        @type reporter: L{ff2zim.reporter.BaseReporter}
        """
        assert isinstance(reporter, BaseReporter) or reporter is None
        
        if reporter is None:
            reporter = VoidReporter()
        
        fanfic_path = os.path.join(project.path, "fanfics")
        target_path = os.path.join(fanfic_path, self.subpath)
        story_path = os.path.join(target_path, "story.html")
        metadata_path = os.path.join(target_path, "metadata.json")
        
        if os.path.exists(story_path):
            raise AlreadyExists("Story already exists!")
        
        reporter.msg("Downloading: {}... ".format(self.url), end="")
        
        try:
            args = [
                "fanficfare",
                "-f", "html",
                "-j",
                "--non-interactive",
                "-o", "is_adult=true",
                "-o", "output_filename={t}{s}${{siteabbrev}}{s}${{storyId}}{s}story${{formatext}}".format(t=fanfic_path, s=os.sep),
                ]
            if project.get_option("download", "include_images", True):
                args += ["-o", "include_images=true"]
                args += ["-o", "skip_author_cover=false"]
            args.append(self.url)
            
            output = subprocess.check_output(
                args,
                universal_newlines=True,
                )
        except subprocess.CalledProcessError:
            reporter.msg("Error.\nCleaning up...")
            if os.path.exists(target_path):
                shutil.rmtree(target_path)
            reporter.msg("Done.")
        else:
            # check if download was successfull
            if not os.path.exists(target_path):
                # not successfull
                reporter.msg("Error.")
            else:
                reporter.msg("Done.\nSaving Metadata... ", end="")
                # dump output into metadata
                with open(metadata_path, "w") as fout:
                    fout.write(output)
                reporter.msg("Done.")
    

        

if __name__ == "__main__":
    # testcode
    while True:
        url = input("URL: ")
        target = Target(url)
        print("Subpath: ", target.subpath)

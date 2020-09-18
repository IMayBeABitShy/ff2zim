"""
Create epub files from html stories.
"""
import argparse
import os
import json
import re
import datetime
import logging
from pprint import pprint

from six.moves import configparser

import bs4
from fanficfare.story import Story
from fanficfare.configurable import Configuration
from fanficfare import writers


FFDL_PLACEHOLDER = "___FF2ZIM_IMGURL_FFDL_PLACEHOLDER___"


class Html2EpubConverter(object):
    """
    The HTML to EPUB converter.
    
    @param path: path to dir containing story and metadata
    @type path: L{str}
    @param include_images: if nonzero, include images in epub
    @type include_images: L{bool}
    
    @cvar IGNORE_METADATA_KEYS: tuple of metadata keys to ignore
    @type IGNORE_METADATA_KEYS: L{tuple} of L{str}
    @cvar CHAPTER_NAME_LINK_REGEX: regex to use to identify hrefs of chapter links
    @type CHAPTER_NAME_LINK_REGEX: compiled regex
    """
    
    IGNORE_METADATA_KEYS = ("output_filename", "zchapters")
    CHAPTER_NAME_REGEX = re.compile("^section[0-9]+$")
    CHAPTER_NAME_LINK_REGEX = re.compile("#section[0-9]+")
    
    def __init__(self, path, include_images=True):
        self.path = path
        self.include_images = include_images
        self.soup = None
        self.story = None
        self.config = None
    
    def get_soup(self):
        """
        Return the content soup, generating it if neccessary.
        
        @return: the soup, possibly cached
        @rtype: L{bs4.BeautifulSoup}
        """
        if self.soup is None:
            sp = os.path.join(self.path, "story.html")
            with open(sp, "r") as fin:
                content = fin.read()
            self.soup = bs4.BeautifulSoup(content, "html.parser")
        return self.soup
    
    def get_story(self):
        """
        Return the fanficfare story, instancing it if neccessary.
        
        @return: the story, possibly cached
        @rtype: L{fanficfare.story.Story}
        """
        if self.story is None:
            conf = self.get_config()
            self.story = Story(conf)
        return self.story
    
    def get_config(self):
        """
        Return the fanficfare configuration, creating it if neccessary.
        
        @return: the configuration, possibly cached
        @rtype: L{fanficfare.configurable.Configuration}
        """
        if self.config is None:
            self.config = Configuration(["zimhtml"], "epub")
            try:
                self.config.add_section('overrides')
            except configparser.DuplicateSectionError:
                # generally already exists in defaults.ini
                pass
            if self.include_images:
                self.config.set("overrides", "include_images", "true")
        return self.config
    
    def parse_metadata(self):
        """
        Read and set the metadata of the story.
        """
        story = self.get_story()
        mp = os.path.join(self.path, "metadata.json")
        with open(mp, "r") as fin:
            content = json.load(fin)
        for key in content.keys():
            # check if key is blacklisted
            if key in self.IGNORE_METADATA_KEYS:
                continue
            
            value = content[key]
            
            # parse values if neccessary
            if key == "dateCreated":
                value = datetime.datetime.strptime(value, "%Y-%m-%d %H:%M:%S")
            elif key in ("datePublished", "dateUpdated"):
                for fmt in ("%Y-%m-%d", "%Y-%m-%d %H:%M:%S", "%Y-%m-%d %H:%M"):
                    try:
                        value = datetime.datetime.strptime(value, fmt)
                        break
                    except ValueError:
                        continue
                else:
                    # invalid format
                    value = datetime.datetime(1, 1, 1)
            
            story.setMetadata(key, value)
    
    def add_images(self):
        """
        Add the images to the URL.
        """
        soup = self.get_soup()
        story = self.get_story()
        
        all_images = soup.find_all("img")
        for imgtag in all_images:
            if imgtag.get("alt") == "cover":
                is_cover = True
            else:
                is_cover = False
            img_url = imgtag["src"]
            # fanficfare does not like 'ffdl-' present in the URL, replace it with a placeholder
            sub_img_url = img_url.replace("ffdl-", FFDL_PLACEHOLDER)
            newsrc, imgurl = story.addImgUrl("file://{}/story.html".format(self.path), sub_img_url, self.fetch_image, cover=is_cover)
            # rewrite image tag
            imgtag["src"] = newsrc
            if not imgtag.has_attr("longdesc"):
                imgtag["longdesc"] = imgurl
    
    def fetch_image(self, url, **kwargs):
        """
        This method is cally by the story to fetch the images.
        
        @param url: url to fetch
        @type url: L{str}
        """
        assert url.startswith("file://")
        url = url.replace("file://", "")
        # fanficfare does not like 'ffdl-' present in the URL, we replaced it with a placeholder earlier
        url = url.replace(FFDL_PLACEHOLDER, "ffdl-")
        with open(url, "rb") as fin:
            data = fin.read()
        return data
    
    def parse_chapter_contents(self):
        """
        Parse the chapter contents.
        """
        soup = self.get_soup()
        story = self.get_story()
        # chapter_title_matches = soup.find_all("a", href=self.CHAPTER_NAME_LINK_REGEX)
        # all_chapter_names = [e.text for e in chapter_title_matches]
        # all_storytexts = soup.find_all(id="storytextp")
        first_title_tag = soup.find("a", {"name": self.CHAPTER_NAME_REGEX})
        all_chapter_names = [first_title_tag.text]
        all_storytexts = []
        for tag in first_title_tag.next_siblings:
            if tag.name == "a":
                all_chapter_names.append(tag.text)
            elif tag.name == "div":
                all_storytexts.append(str(tag))
            #else:
            #    raise Exception("Unknown HTML tag on content-root-level of story: '{}'!".format(tag))
        
        for title, html in zip(all_chapter_names, all_storytexts):
            story.addChapter(
                {
                    "title": title,
                    "html": html,
                },
            )
    
    def parse(self):
        """
        Parse the whole input story.
        """
        self.parse_metadata()
        self.add_images()  # <-- must be before parse_chapter_contents()
        self.parse_chapter_contents()
    
    def write(self, path=None):
        """
        Write the fanfic to an epub.
        
        @param path: path to write to
        @type path: L{str}
        """
        if path is None:
            path = os.path.join(self.path, "story.epub")
        config = self.get_config()
        logging.getLogger("fanficfare").setLevel(logging.WARNING)
        writer = writers.getWriter("epub", config, self)
        writer.writeStory(
            outfilename=path,
            metaonly=False,
            forceOverwrite=True,
            )
        
    
    def getStory(self):
        """
        Return the story. Part of the fake adapter api.
        
        @return: the story
        @rtype: L{fanficfare.story.Story}
        """
        return self.get_story()
    
    def getStoryMetadataOnly(self):
        """
        Return the story. Part of the fake adapter api.
        
        @return: the story
        @rtype: L{fanficfare.story.Story}
        """
        # We implement no difference from getStory()
        return self.getStory()


def main():
    """
    The main function.
    """
    parser = argparse.ArgumentParser(description="Convert story to EPUB")
    parser.add_argument("path", help="path to story directory")
    parser.add_argument("outpath", nargs="?", default="story.epub", help="path to write epub to")
    parser.add_argument("--print-images", action="store_true", dest="printimages", help="print image information")
    parser.add_argument("--print-content", action="store_true", dest="printcontent", help="print content")
    ns = parser.parse_args()
    
    conv = Html2EpubConverter(ns.path)
    conv.parse()
    story = conv.get_story()
    if ns.printimages:
        pprint(story.getImgUrls())
    if ns.printcontent:
        pprint(story.getChapters())
    conv.write(ns.outpath)

if __name__ == "__main__":
    main()
    

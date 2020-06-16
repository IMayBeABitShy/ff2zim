"""
This module contains metadata converter to ensure metadata key names
are roughly the same.
"""
from .utils import str_to_int


class BaseMetadataConverter(object):
    """
    Base class for all metadata converters.
    """
    @staticmethod
    def convert(data):
        """
        Convert the metadata dict.
        
        @param data: metadata to convert. This will both be modifed and returned.
        @type data: L{str}
        """
        pass


class NoConverter(BaseMetadataConverter):
    """
    A converter which does not modify anything.
    """
    @staticmethod
    def convert(data):
        return data


class DefaultConverter(BaseMetadataConverter):
    """
    The default converter.
    """
    @staticmethod
    def convert(data):
        data["numWords"] = str_to_int(data["numWords"])
        data["numChapters"] = str_to_int(data["numChapters"])
        return data
        
    
class FFNetConverter(BaseMetadataConverter):
    """
    A converter for ffnet.
    """
    @staticmethod
    def convert(data):
        data["authorId"] = data.get("authorId", "???")
        data["favs"] = str_to_int(data.get("favs", "0"))
        data["follows"] = str_to_int(data.get("follows", "0"))
        data["numChapters"] = str_to_int(data.get("numChapters", "0"))
        data["numWords"] = str_to_int(data.get("numWords", "0"))
        data["reviews"] = str_to_int(data.get("reviews", "0"))
        data["storyId"] = data.get("storyId", "???")
        return data


class AO3Converter(BaseMetadataConverter):
    """
    A converter for ao3.
    """
    @staticmethod
    def convert(data):
        data["authorId"] = data.get("authorId", "???")
        data["favs"] = str_to_int(data.get("kudos", "0"))
        # technically, bookmarks are not follows, but we cant access subscriptions
        if not data.get("bookmarks", ""):
            data["bookmarks"] = "0"
        data["follows"] = str_to_int(data.get("bookmarks", "0"))
        data["numChapters"] = str_to_int(data.get("numChapters", "0"))
        data["numWords"] = str_to_int(data.get("numWords", "0"))
        data["reviews"] = str_to_int(data.get("comments", "0"))
        data["storyId"] = data.get("storyId", "???")
        return data


class FSBConverter(BaseMetadataConverter):
    """
    A converter for FSB.
    """
    @staticmethod
    def convert(data):
        data["authorId"] = data.get("authorId", "???")
        # data["favs"] = str_to_int(data.get("kudos", "0"))
        # data["follows"] = str_to_int(data.get("bookmarks", "0"))
        data["numChapters"] = str_to_int(data.get("numChapters", "0"))
        numWords = 0
        for chapterdata in data["zchapters"]:
            chaptermeta = chapterdata[1]
            numWords += str_to_int(chaptermeta.get("kwords", "0"))
        data["numWords"] = numWords
        data["status"] = "Unknown"
        # data["reviews"] = str_to_int(data.get("comments", "0"))
        data["storyId"] = data.get("storyId", "???")
        return data


# map site abbrev -> converter
CONVERTERS = {
    "ffnet": FFNetConverter(),
    "ao3": AO3Converter(),
    "fsb": FSBConverter(),
}


def get_metadata_converter(abbrev):
    """
    Get the converter for the specified site or the default conerter.
    
    @param abbrev: site abbrev to get the converter for
    @type abbrev: L{str}
    
    @return: the converter or the default converter.
    @rtype: L{BaseMetadataConverter}
    """
    return CONVERTERS.get(abbrev, DefaultConverter())

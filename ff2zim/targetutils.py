"""
Utilities for targets.
"""
import re
from urllib.parse import urlparse


STORY_URL_REGEX = r"((http(s)?://)?(www\.)?fanfiction\.net)?/s/[0-9]+"


def get_id_from_url(url):
    """
    Return the ID in a fanfiction.net URL.
    
    @param url: URL to extract from
    @type url: L{str}
    @return: the id of the fanfic
    @rtype: L{int}
    """
    assert isinstance(url, str)
    if url.isdigit():
        return int(url)
    parsed = urlparse(url)
    path = parsed.path
    if not path.startswith("/s/"):
        return None
    wos = path[3:]
    lspos = wos.find("/")
    ids = wos[:lspos]
    fid = int(ids)
    return fid


def get_url_for_id(fid):
    """
    Return the url for the fanfic with the specified id.
    
    @param fid: id to get URL for.
    @type fid: L{int}
    
    @return: the URL
    @rtype: L{str}
    """
    return "https://fanfiction.net/s/{}".format(fid)


def is_valid_url_or_id(s):
    """
    Check if s is a valid URL or ID.
    
    @param s: value to check
    @type s: L{str} or L{int}
    @return: whether s is a valid target
    @rtype: L{bool}
    """
    assert isinstance(s, (int, str))
    if isinstance(s, int) or s.isdigit():
        if int(s) > 0:
            return True
        else:
            return False
    else:
        parsed = urlparse(s)
        if parsed.scheme not in ("http", "https"):
            return False
        elif parsed.netloc not in ("www.fanfiction.net", "fanfiction.net"):
            return False
        else:
            return True


def find_all_ids_in_string(s):
    """
    Find all story ids in a string.
    
    @param s: string to parse
    @type s: L{str}
    
    @return: list of ids in URL
    @rtype: L{list} of L{int}
    """
    ids = []
    matches = re.finditer(STORY_URL_REGEX, s)
    for m in matches:
        si = m.start()
        ei = m.end() + 1
        ms = s[si:ei]
        sid = get_id_from_url(ms)
        ids.append(sid)
    return ids

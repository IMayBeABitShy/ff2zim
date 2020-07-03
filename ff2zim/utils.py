"""
Various utility functions.
"""

def str_to_int(s):
    """
    Convert a fanfiction number string to an integer.
    
    @param s: string to parse/convert
    @type s: L{str}
    
    @return: the number
    @rtype: L{int}
    """
    s = s.strip().lower()
    s = s.replace("(", "")
    s = s.replace(")", "")
    if s.count(".") > 1:
        # period can not indicate start of decimal
        s = s.replace(".", ",")
    s = s.replace(",", "")
    if s.endswith("k"):
        multiplier = 1000
        s = s[:-1]
    elif s.endswith("m"):
        multiplier = 1000000
        s = s[:-1]
    else:
        multiplier = 1
    if not s:
        return 0
    return int(float(s) * multiplier)



def bleach_name(name):
    """
    Make a name safe for the file system.
    
    @param name: name to make safe
    @type name: L{str}
    
    @return: A safer version of name
    @rtype: L{str}
    """
    assert isinstance(name, str)
    
    name = name.replace("\x00", "_")
    name = name.replace("/",    "_")
    name = name.replace("\\",   "_")
    name = name.replace("#",    "_")
    name = name.replace("?",    "_")
    name = name.replace("&",    "_")
    name = name.replace("=",    "_")
    name = name.replace(":",    "_")
    
    return name

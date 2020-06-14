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
    s = s.replace(",", "")
    s = s.replace("k", "000")
    s = s.replace("m", "000000")
    return int(s)



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
    name = name.replace("/", "_")
    name = name.replace("\\", "_")
    return name

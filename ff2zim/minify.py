"""
File minification utilities.
"""
import os

try:
    import htmlmin
except ImportError:
    htmlmin = None
try:
    import csscompressor
except ImportError:
    csscompressor = None
try:
    import python_minifier
except ImportError:
    python_minifier = None

from .fileutils import create_file_with_content


# list of metadata keys to keep.
METADATA_IMPORTANT_KEYS = [
    "author",
    "authorId",
    "characters",
    "dateCreated",
    "datePublished",
    "dateUpdated",
    "description",
    "favs",
    "follows",
    "language",
    "langcode",
    "numChapters",
    "numWords",
    "rating",
    "siteabbrev",
    "status",
    "storyId",
    "title",
]


def minify_file(path):
    """
    Minify the specified file in-place.
    
    @param path: path to file to minify
    @type path: L{str}
    """
    extension = os.path.splitext(path)[-1].replace(".", "")
    with open(path, "r") as fin:
        content = fin.read()
    
    if extension in ("html", "htm"):
        new_content = minify_html(content)
    elif extension == "css":
        new_content = minify_css(content)
    else:
        raise NotImplementedError("Unsure how to minify file of type '{}'!".format(extension))
    
    create_file_with_content(path, new_content, replace=True)


def minify_metadata(metadata):
    """
    Minify metadata in-place. Metadata may either be a dict or list of dicts.
    
    @param metadata: metadata (dict/list) to minify
    @type metadata: l{dict} or L{list} of L{dict}
    """
    if isinstance(metadata, (list, tuple)):
        # minify each entry seperately
        for e in metadata:
            minify_metadata(e)
    elif isinstance(metadata, dict):
        # minify entry
        for key in list(metadata.keys()):
            if key not in METADATA_IMPORTANT_KEYS:
                del metadata[key]
    else:
        # unknown type
        raise TypeError("Expected list of dict or dict, not '{}'!".format(type(metadata)))


def minify_html(s):
    """
    Minify html code.
    
    @param s: html code to minify
    @type s: L{str}
    @return: the minified html
    @rtype: L{str}
    """
    if htmlmin is None:
        raise NotImplementedError("Dependency 'htmlmin' required, but not found!")
    return htmlmin.minify(
        s,
        remove_comments=True,
        reduce_boolean_attributes=True,
        remove_optional_attribute_quotes=True,
    )


def minify_css(s):
    """
    Minify CSS code.
    
    @param s: css to minify
    @type s: L{str}
    @return: the minfied css
    @rtype: L{str}
    """
    if csscompressor is None:
        raise NotImplementedError("Dependency 'csscompressor' required, but not found!")
    return csscompressor.compress(
        s,
        preserve_exclamation_comments=False,
    )
    

def minify_python(s):
    """
    Minify python code.
    
    @param s: python code to minify
    @type s: L{str}
    @return: the minified python code
    @rtype: L{str}
    """
    # not working with brython :(
    return s
    if python_minifier is None:
        raise NotImplementedError("Dependency 'python-minifier' required, but not found!")
    return python_minifier.minify(
        s,
        remove_annotations=True,
        remove_pass=True,
        # remove_literal_statements=
        combine_imports=True,
        hoist_literals=True,
        rename_locals=True,
        rename_globals=True,
    )
    

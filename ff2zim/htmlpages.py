"""
Functions and constants for creating the HTML pages and other web content.
"""
import os
import json

from .utils import bleach_name
from .fileutils import create_file_with_content
from .minify import minify_css, minify_html, minify_python, minify_metadata


INDEX_TEMPLATE = """<!DOCTYPE html>
<HTML>
    <HEAD>
        <META charset="UTF-8">
        <title>{title}</title>
        <link rel="stylesheet" href="resources/styles.css">
    </HEAD>
    <BODY>
        <H1>{title}</H1>
        <hr>
        <TABLE border="1" class="content_count">
            <tr>
                <th>Type</th>
                <th>Count</th>
            </tr>
            <tr>
                <td>Categories</td>
                <td><P align="right">{ncategories:,}</P></td>
            </tr>
            <tr>
                <td>Authors</td>
                <td><P align="right">{nauthors:,}</P></td>
            </tr>
            <tr>
                <td>Stories</td>
                <td><P align="right">{nstories:,}</P></td>
            </tr>
            <tr>
                <td>Chapters</td>
                <td><P align="right">{nchapters:,}</P></td>
            </tr>
            <tr>
                <td>Words</td>
                <td><P align="right">{nwords:,}</P></td>
            </tr>
        </TABLE>
        <A style="float: right;" href="stats.html">More statistics</A>
        <BR>
        <hr>
        {categories}
        <hr>
    </BODY>
</HTML>
"""

STATPAGE_TEMPLATE = """<!DOCTYPE html>
<HTML>
    <HEAD>
        <META charset="UTF-8">
        <title>Statistics</title>
        <link rel="stylesheet" href="resources/styles.css">
    </HEAD>
    <BODY>
        <H1>Statistics</H1>
        <hr>
        <TABLE border="1" class="content_stats">
            <tr>
                <th>Type</th>
                <th>Count</th>
            </tr>
            <tr>
                <td>Sources</td>
                <td><P align="right">{nsources:,.4f}</P></td>
            </tr>
            <tr>
                <td>Categories</td>
                <td><P align="right">{ncategories:,.4f}</P></td>
            </tr>
            <tr>
                <td>Authors</td>
                <td><P align="right">{nauthors:,.4f}</P></td>
            </tr>
            <tr>
                <td>Stories</td>
                <td><P align="right">{nstories:,.4f}</P></td>
            </tr>
            <tr>
                <td>Stories per Author</td>
                <td><P align="right">{spa:,.4f}</P></td>
            </tr>
            <tr>
                <td>Chapters</td>
                <td><P align="right">{nchapters:,.4f}</P></td>
            </tr>
            <tr>
                <td>Chapters per Story</td>
                <td><P align="right">{cps:,.4f}</P></td>
            </tr>
            <tr>
                <td>Words</td>
                <td><P align="right">{nwords:,.4f}</P></td>
            </tr>
            <tr>
                <td>Words per Chapter</td>
                <td><P align="right">{wpc:,.4f}</P></td>
            </tr>
            <tr>
                <td>Wordcount in novels (lower bound)</td>
                <td><P align="right">{wcin_lower:,.4f}</P></td>
            </tr>
            <tr>
                <td>Wordcount in novels (upper bound)</td>
                <td><P align="right">{wcin_upper:,.4f}</P></td>
            </tr>
            <tr>
                <td>Wordcount in Bibles</td>
                <td><P align="right">{wcib:,.4f}</P></td>
            </tr>
        </TABLE>
    </BODY>
</HTML>
"""

CATEGORY_TEMPLATE = """<!DOCTYPE html>
<HTML>
    <HEAD>
        <META charset="UTF-8">
        <title>{name} (Category)</title>
        <script type="text/javascript" src="../../resources/brython.js"></script>
        <!-- <script type="text/javascript" src="../../resources/brython_stdlib.js"></script> -->
        <link rel="stylesheet" href="../../resources/styles.css">
        <noscript><style> .jsonly {{display: none;}} </style></noscript>
    </HEAD>
    <BODY onload="brython()">
        <H1>{name}</H1>
        <hr>
        <DIV class="jsonly">
            <script type="text/python" src="../../resources/sort.py" id="category_sort"></script>
            <DIV id="sort_settings">
            </DIV>
            <hr>
            <DIV id="table_container">
                <P id="load_message">Loading...</P>
            </DIV>
        </DIV>
        <noscript>
            <P>Javascript is disabled. Please use the <A href="simplelist.html">Content List</A> instead.</P>
        </noscript>
    </BODY>
</HTML>
"""

AUTHOR_TEMPLATE = """<!DOCTYPE html>
<HTML>
    <HEAD>
        <META charset="UTF-8">
        <title>{name} (Author)</title>
        <script type="text/javascript" src="../../resources/brython.js"></script>
        <!-- <script type="text/javascript" src="../../resources/brython_stdlib.js"></script> -->
        <link rel="stylesheet" href="../../resources/styles.css">
        <noscript><style> .jsonly {{display: none;}} </style></noscript>
    </HEAD>
    <BODY onload="brython()">
        <H1>{name}</H1>
        <hr>
        <P><B>Name:           </B> {name}</P>
        <P><B>ID:             </B> {id}</P>
        <P><B>Fanfiction Link:</B> <A href={authorlink}>{authorlink}</A></P>
        <hr>
        <DIV class="jsonly">
            <script type="text/python" src="../../resources/sort.py" id="author_sort"></script>
            <DIV id="sort_settings">
            </DIV>
            <hr>
            <DIV id="table_container">
                <P id="load_message">Loading...</P>
            </DIV>
        </DIV>
        <noscript>
            <P>Javascript is disabled. Please use the <A href="simplelist.html">Content List</A> instead.</P>
        </noscript>
    </BODY>
</HTML>
"""

COVER_TEMPLATE = """<!DOCTYPE html>
<HTML>
    <HEAD>
        <META charset="UTF-8">
        <title>{title} (Cover)</title>
        <link rel="stylesheet" href="../../resources/styles.css">
    </HEAD>
    <BODY>
        <H1>{title} (Cover)</H1>
        {cover}
        <hr>
        <P><B>Title:          </B> {title}</P>
        <P><B>Author:         </B> {author}</P>
        <P><B>Chapters:       </B> {chapters}</P>
        <P><B>Words:          </B> {words}</P>
        <P><B>Published:      </B> {published}</P>
        <P><B>Updated:        </B> {updated}</P>
        <P><B>Packaged:       </B> {packaged}</P>
        <P><B>Description:    </B> {description}</P>
        <hr>
        <DIV class="cover_storylinks">
            <P><A class="cover_read_link" href="story.html">Read</A><P>
            {epublink}
        </DIV>
    </BODY>
</HTML>
"""

SIMPLELIST_TEMPLATE = """<!DOCTYPE html>
<HTML>
    <HEAD>
        <META charset="UTF-8">
        <title>List of {title} stories</title>
        <link rel="stylesheet" href="resources/styles.css">
        <noscript><style> .jsonly {{display: none;}} </style></noscript>
    </HEAD>
    <BODY>
        <H1>List of {title} stories</H1>
        <hr>
        <DIV class="jsonly">
            <P><B>Note: <A href="list.html">Advance Filter&amp;Sort</A> is available</B></P>
            <hr>
        </DIV>
        <DIV class="contentlist_nav">
            {contentlist_nav}
        </DIV>
        {content}
    </BODY>
</HTML>
"""

SORT_SCRIPT = """
from javascript import JSON

from browser import document, html, bind

TABLE_CONTAINER = "table_container"
SORT_SETTINGS = "sort_settings"
RATINGS = ["K", "K+", "T", "M", "ANY"]
STATI = ["In-Progress", "Completed", "ANY"]
LANGUAGES = [("ANY", "ANY")]
CHARACTERS = ["ANY"]

METADATA = None


def load_metadata():
    # load story metadata
    global METADATA
    metadatapath = document.location.pathname
    metadatapath = metadatapath[:metadatapath.rfind("/") + 1] + "stories.json"
    with open(metadatapath, "r") as fin:
        content = fin.read()
    METADATA = JSON.parse(content)
    


def update_globals():
    # update the global variables such as languages
    global LANGUAGES, CHARACTERS
    tlangs = set()
    tlangs.add(("ANY", "ANY"))
    tcharacters = set()
    for e in METADATA:
        langtuple = (e["language"], e["langcode"])
        tlangs.add(langtuple)
        storycharacters = e.get("characters", [])
        for c in storycharacters:
            tcharacters.add(c)
    LANGUAGES = list(sorted(tlangs))
    CHARACTERS = ["ANY"] + sorted(tcharacters)


def get_sortinfo():
    # return the sort&filter settings
    sortinfo = {}
    # sortinfo["language"] = document.query.getfirst("language", "ANY")
    # sortinfo["rating"] = document.query.getfirst("rating", "ANY")
    # sortinfo["status"] = document.query.getfirst("status", "ANY")
    # sortinfo["sort_by"] = document.query.getfirst("sortBy", "updated")
    # sortinfo["reverse"] = (document.query.getfirst("reverse", "0") == "1")
    # sortinfo["characters"] = [c.replace("+", " ") for c in document.query.getlist("characters")]
    
    if "language" not in document:
        # settings not yet populated, return default
        return {
            "language": "ANY",
            "rating": "ANY",
            "status": "ANY",
            "sort_by": "updated",
            "reverse": False,
            "characters": ["ANY"],
            "ship": [],
        }
        
    sortinfo["language"] = document["language"].value
    sortinfo["rating"] = document["rating"].value
    sortinfo["status"] = document["status"].value
    sortinfo["sort_by"] = document["sortBy"].value
    sortinfo["reverse"] = document["reverse"].checked
    sortinfo["characters"] = [option.value for option in document["characters"] if option.selected]
    sortinfo["ship"] = [option.value for option in document["ship"] if option.selected]
    return sortinfo


def sort_entries(sortinfo):
    # sort and filter the entries
    
    filtered = []
    for e in METADATA:
        
        # filter language
        if sortinfo["language"] != "ANY":
            if e.get("langcode") != sortinfo["language"]:
                continue
        
        # filter rating
        if sortinfo["rating"] != "ANY":
            if e.get("rating", "M") != sortinfo["rating"]:
                continue
                
        # filter status
        if sortinfo["status"] != "ANY":
            if e.get("status", "???") != sortinfo["status"]:
                continue
        
        # filter characters
        characters = e.get("characters", [])
        chars_valid = True
        for cn in sortinfo["characters"]:
            if cn == "ANY":
                break
            elif cn not in characters:
                chars_valid = False
                break
        if not chars_valid:
            # characters do not match
            continue
        
        # filter ship
        ship_valid = False
        ship = sortinfo["ship"]
        storyships = [cn for ss in e.get("ships", []) for cn in ss]
        if not all([(cn in storyships or (cn == "ANY" and storyships)) for cn in ship]):
            # not all characters are shipped
            continue
        
        filtered.append(e)
    
    # set sort
    sortname = sortinfo.get("sort_by", "title")
    invert_reverse = False  # if True, invert reverse
    if sortname == "title":
        sortkey = lambda x: x.get("title", "???")
    elif sortname == "published":
        sortkey = lambda x: x.get("datePublished", "???")
        invert_reverse = True
    elif sortname == "updated":
        sortkey = lambda x: x.get("dateUpdated", "???")
        invert_reverse = True
    elif sortname == "added":
        sortkey = lambda x: x.get("dateCreated", "???")
        invert_reverse = True
    elif sortname == "favorites":
        sortkey = lambda x: x.get("favs", 0)
        invert_reverse = True
    elif sortname == "follows":
        sortkey = lambda x: x.get("follows", 0)
        invert_reverse = True
    elif sortname == "chapters":
        sortkey = lambda x: x.get("numChapters", 0)
        invert_reverse = True
    elif sortname == "words":
        sortkey = lambda x: x.get("numWords", 0)
        invert_reverse = True
    elif sortname == "author":
        sortkey = lambda x: x.get("author", "???")
    elif sortname == "words_per_chapter":
        sortkey = lambda x: x.get("numWords", 0) / x.get("numChapters", 1)
        invert_reverse = True
    else:
        raise ValueError("Unknown sort: " + sortname)
    
    if invert_reverse:
        reverse = not sortinfo.get("reverse", False)
    else:
        reverse = sortinfo.get("reverse", False)
    
    return sorted(filtered, key=sortkey, reverse=reverse)


def create_table(sorted_entries):
    # create the table containing the sorted entries.
    tbl = html.TABLE(border=1, id="table_results", **{"class": "stories"})
    tbl <= html.TR(html.TH("Story") + html.TH("Author") + html.TH("Description") + html.TH("Stats"))
    for e in sorted_entries:
        title = e["title"]
        sid = e["storyId"]
        abbrev = e["siteabbrev"]
        author = e.get("author", "")
        author_id = e.get("authorId", 0)
        fsid = "{}-{}".format(abbrev, sid)
        faid = "{}-{}".format(abbrev, author_id)
        description = e.get("description", "???")
        favs = e.get("favs", 0)
        follows = e.get("follows", 0)
        words = e.get("numWords", 0)
        chapters = e.get("numChapters", 0)
        stats = "<P><B>Chapters:</B> {:,}</P><P><B>Words:</B> {:,}</P>".format(chapters, words)
        stats += "<P><B>Followers:</B> {:,}</P><P><B>Favorites:</B> {:,}</P>".format(follows, favs)
        tbl <= html.TR(
            html.TD(
                    html.A(title, href="../../stories/{}/cover.html".format(fsid))
                ) + html.TD(
                    html.A(author, href="../../author/{}/author.html".format(faid))
                ) + html.TD(
                    html.P(description, **{"class": "description"})
                ) + html.TD(
                    html.P(stats, **{"class": "stats"})
                )
            )
    return tbl


def update_table():
    # update the table based on the sort.
    sortinfo = get_sortinfo()
    entries = sort_entries(sortinfo)
    container = document[TABLE_CONTAINER]
    for child in container.children:
        del document[child.id]
    if len(entries) == 0:
        document[TABLE_CONTAINER] <= html.P("No stories matching your query could be found.", id="text_noresult")
    else:
        document[TABLE_CONTAINER] <= create_table(entries)


def create_settings():
    # create the sort and filter form
    current = get_sortinfo()
    cur_lang = current["language"]
    cur_sel = current["sort_by"]
    cur_rating = current["rating"]
    cur_status = current["status"]
    cur_chars = current["characters"]
    cur_ship = current["ship"]
    div = html.DIV()
    form = html.FORM(**{"class": "sort_form"})
    
    # language
    form <= html.LABEL("Language:", **{"for": "language", })
    form <= html.SELECT(
        [html.OPTION(langname, value=langcode, selected=(cur_lang == langcode)) for (langname, langcode) in LANGUAGES],
        id="language",
        name="language",
    )
    form <= html.BR()
    
    # age rating
    form <= html.LABEL("Rating:", **{"for": "rating", })
    form <= html.SELECT(
        [html.OPTION(r, value=r, selected=(cur_rating == r)) for r in RATINGS],
        id="rating",
        name="rating",
    )
    form <= html.BR()
    
    # completion status
    form <= html.LABEL("Status:", **{"for": "status", })
    form <= html.SELECT(
        [html.OPTION(s, value=s, selected=(cur_status == s)) for s in STATI],
        id="status",
        name="status",
    )
    form <= html.BR()
    
    # characters
    form <= html.LABEL("Characters:", **{"for": "characters", })
    form <= html.SELECT(
        [html.OPTION(character, value=character, selected=(character in cur_chars)) for character in CHARACTERS],
        id="characters",
        name="characters",
        multiple=True,
    )
    
    # pairing
    form <= html.LABEL("Ship:", **{"for": "ship", })
    form <= html.SELECT(
        [html.OPTION(character, value=character, selected=(character in cur_ship)) for character in CHARACTERS],
        id="ship",
        name="ship",
        multiple=True,
    )
    
    # sort and order reversal
    form <= html.LABEL("Sort By:", **{"for": "sortBy", })
    form <= html.SELECT(
        [
            html.OPTION("Added", value="added", selected=(cur_sel == "added")),
            html.OPTION("Author", value="author", selected=(cur_sel == "author")),
            html.OPTION("Chapters", value="chapters", selected=(cur_sel == "chapters")),
            html.OPTION("Favorites", value="favorites", selected=(cur_sel == "favorites")),
            html.OPTION("Follows", value="follows", selected=(cur_sel == "follows")),
            html.OPTION("Published", value="published", selected=(cur_sel == "published")),
            html.OPTION("Title", value="title", selected=(cur_sel == "title")),
            html.OPTION("Updated", value="updated", selected=(cur_sel == "updated")),
            html.OPTION("Words", value="words", selected=(cur_sel == "words")),
            html.OPTION("Words/Chapter", value="words_per_chapter", selected=(cur_sel == "words_per_chapter")),
        ],
        id="sortBy",
        name="sortBy",
    )
    form <= html.BR()
    form <= html.LABEL("Reverse Order:", **{"for": "reverse", })
    form <= html.INPUT(type="checkbox", name="reverse", id="reverse", value="1", checked=(current["reverse"]))
    form <= html.BR()
    
    # submit button
    submit_button = html.INPUT(id="update_button", type="submit", value="Sort & Filter")
    submit_button.bind("click", on_submit)
    form <= submit_button
    div <= form
    document[SORT_SETTINGS] <= div


def on_submit(evt):
    # on submit
    evt.preventDefault()
    update_table()

def main():
    # the main function
    load_metadata()
    update_globals()
    create_settings()
    update_table()

main()
"""

STYLE_CONTENT = """
/* CSS style sheet for ffn2zim */
.description {
    font-size: small;
}

.stats {
    font-size: small;
}

table, th, tr {
    border: 1px solid black;
    border-collapse: collapse;
}

.stats P {
    white-space: nowrap;
    margin-bottom: 5px;
    margin: 5px;
}

.content_count P {
    margin-left: 5px;
    margin-right: 5px;
    margin-bottom: 5px;
    margin-top: 5px;
}

.content_count {
    width: 100%;
}

.content_count TH {
    background: darkgrey;
}

.content_overview {
    width: 100%;
}

.content_overview P {
    margin-left: 5px;
    margin-right: 5px;
    margin-bottom: 5px;
    margin-top: 5px;
}

.content_overview TH {
    background: darkgrey;
}

.stories {
    width: 100%;
}

.stories TH {
    background: darkgrey;
}

.content_stats {
    width: 100%;
}

.content_stats P {
    margin-left: 5px;
    margin-right: 5px;
    margin-bottom: 5px;
    margin-top: 5px;
}

.content_stats TH {
    background: darkgrey;
}

.sort_form * {
    margin-bottom: 8px;
}

.sort_form LABEL {
    display: inline-block;
    width:10%;
    font-weight: bold;
}

.sort_form SELECT {
    display: inline-block;
    width: 90%
}

.sort_form #update_button {
    width: 100%;
    font-weight: bold;
}
"""


def create_author_page(path, authorinfo, id2meta, minify=False):
    """
    Create an author page.
    
    @param path: path to author directory
    @type path: L{str}
    @param authorinfo: a dict containing details about the author
    @type authorinfo: L{dict}
    @param id2meta: a dict mapping story IDs to their metadata
    @type id2meta: L{dict}
    @param minify: if nonzero, minify content
    @type minify: L{str}
    """
    assert isinstance(path, str)
    assert isinstance(authorinfo, dict)
    assert isinstance(id2meta, dict)
    if not os.path.exists(path):
        os.mkdir(path)
    pagepath = os.path.join(path, "author.html")
    datapath = os.path.join(path, "stories.json")
    simplelistfile = os.path.join(path, "simplelist.html")
    authorcontent = AUTHOR_TEMPLATE.format(
        name=authorinfo["name"],
        authorlink=authorinfo["url"],
        html=authorinfo["html"],
        id=authorinfo["id"],
        )
    metadata = [id2meta[sid] for sid in authorinfo["stories"]]
    if minify:
        authorcontent = minify_html(authorcontent)
        minify_metadata(metadata)
    create_file_with_content(pagepath, authorcontent)
    create_file_with_content(datapath, json.dumps(metadata))
    create_simplelist(
        simplelistfile,
        authorinfo["name"]+"'s",
        id2meta,
        authorinfo["stories"],
        minify=minify,
    )


def create_category_page(path, name, minify=False):
    """
    Create a category page.
    
    @param path: path to write to
    @type path: L{str}
    @param name: name of categiry
    @type name: L{str}
    @param minify: if nonzero, minify content
    @type minify: L{str}
    """
    assert isinstance(path, str)
    assert isinstance(name, str)
    content = CATEGORY_TEMPLATE.format(name=name)
    if minify:
        content = minify_html(content)
    create_file_with_content(path, content)


def create_index_page(path, id2meta, category2ids, authordata, minify=False):
    """
    Create the index/welcome page.
    
    @param path: path to write to
    @type path: L{str}
    @param id2meta: a dict mapping story IDs to their metadata
    @type id2meta: L{dict}
    @param category2ids: a dict mapping story IDs to their metadata
    @type category2ids: L{dict}
    @param authordata: a dict mapping authorIDs to information about them
    @type authordata: L{str}
    @param minify: if nonzero, minify content
    @type minify: L{str}
    """
    assert isinstance(path, str)
    assert isinstance(id2meta, dict)
    assert isinstance(category2ids, dict)
    assert isinstance(authordata, dict)
    
    nauthors = len(list(authordata.keys()))
    nstories = len(list(id2meta.keys()))
    ncategories = len(list(category2ids.keys()))
    
    nwords = 0
    nchapters = 0
    
    for sid in id2meta:
        md = id2meta[sid]
        nwords += md["numWords"]
        nchapters += md["numChapters"]
    
    categories_and_n = [(c, len(category2ids[c])) for c in category2ids]
    # first sort by alphabet, then by chapter count
    categories_and_n = sorted(categories_and_n, key=lambda x: x[0], reverse=False)
    categories_and_n = sorted(categories_and_n, key=lambda x: x[1], reverse=True)
    category_table_start = "<table border='1' class='content_overview'>"
    category_table_start += "<TR><TH>Category</TH><TH>Stories</TH></TR>"
    category_table = category_table_start + "\n".join(
            [
            "<tr><td><a href='{url}'>{ct}</a></td><td><P align='right'>{n}<P></td></tr>".format(
                url="category/{}/list.html".format(bleach_name(c[0])),
                ct=c[0],
                n=c[1])
                for c in categories_and_n
            ]
        ) + "</table>"
    
    html = INDEX_TEMPLATE.format(
        title="ff2zim",
        nauthors=nauthors,
        nstories=nstories,
        ncategories=ncategories,
        nchapters=nchapters,
        nwords=nwords,
        categories=category_table,
    )
    if minify:
        html = minify_html(html)
    create_file_with_content(path, html)


def create_stats_page(path, id2meta, category2ids, authordata, minify=False):
    """
    Create the statistics page.
    
    @param path: path to write to
    @type path: L{str}
    @param id2meta: a dict mapping story IDs to their metadata
    @type id2meta: L{dict}
    @param category2ids: a dict mapping story IDs to their metadata
    @type category2ids: L{dict}
    @param authordata: a dict mapping authorIDs to information about them
    @type authordata: L{str}
    @param minify: if nonzero, minify content
    @type minify: L{str}
    """
    assert isinstance(path, str)
    assert isinstance(id2meta, dict)
    assert isinstance(category2ids, dict)
    assert isinstance(authordata, dict)
    
    nauthors = len(list(authordata.keys()))
    nstories = len(list(id2meta.keys()))
    ncategories = len(list(category2ids.keys()))
    
    nwords = 0
    nchapters = 0
    sources = []
    
    for sid in id2meta:
        md = id2meta[sid]
        nwords += md["numWords"]
        nchapters += md["numChapters"]
        source = md["siteabbrev"]
        if source not in sources:
            sources.append(source)
    
    html = STATPAGE_TEMPLATE.format(
        nsources=len(sources),
        ncategories=ncategories,
        nstories=nstories,
        spc=(nstories / float(ncategories)),
        nauthors=nauthors,
        spa=(nstories / float(nauthors)),
        nchapters=nchapters,
        cps=(nchapters / float(nstories)),
        nwords=nwords,
        wpc=(nwords / float(nchapters)),
        wcin_lower=(nwords / 90000.0),
        wcin_upper=(nwords / 60000.0),
        wcib=(nwords / 789650.0),
    )
    if minify:
        html = minify_html(html)
    create_file_with_content(path, html)


def create_cover_page(path, fsid, metadata, include_images=False, include_epubs=False, minify=False):
    """
    Write a cover page for a story.
    
    @param path: path to write to
    @type path: l{str}
    @param fsid: full story ID
    @type fsid: L{str}
    @param metadata: metadata of the story
    @type metadata: L{dict}
    @param include_images: if nonzero, include the cover in the output.
    @type include_images: L{bool}
    @param include_epubs: if nonzero, include a link for the epub
    @type include_epubs: L{bool}
    @param minify: if nonzero, minify content
    @type minify: L{str}
    """
    page = COVER_TEMPLATE.format(
        fsid=fsid,
        title=metadata.get("title", "???"),
        author=metadata.get("author", "???"),
        words=metadata.get("numWords", "???"),
        chapters=metadata.get("numChapters", "???"),
        description=metadata.get("description", "???"),
        published=metadata.get("datePublished", "???"),
        updated=metadata.get("dateUpdated", "???"),
        packaged=metadata.get("dateCreated", "???"),
        cover=('<CENTER><img src="../stories/{}/images/cover.jpg" alt="cover"></CENTER>'.format(fsid) if include_images else ""),
        epublink=('<P><A class="cover_epub_link" href="story.epub" download="{}.epub">Download EPUB</A></>'.format(metadata.get("title", "story"))),
        )
    if minify:
        page = minify_html(page)
    create_file_with_content(path, page)


def create_sort_script(path, minify=False):
    """
    Write the sort script to the given path.
    
    @param path: path to write to
    @type path: L{str}
    @param minify: if nonzero, minify content
    @type minify: L{str}
    """
    script = SORT_SCRIPT
    if minify:
        script = minify_python(script)
    create_file_with_content(path, script)


def create_style_file(path, minify=False):
    """
    Write the CSS style sheet to the given path.
    
    @param path: path to write to
    @type path: L{str}
    @param minify: if nonzero, minify content
    @type minify: L{str}
    """
    css = STYLE_CONTENT
    if minify:
        css = minify_css(css)
    create_file_with_content(path, css)


def create_simplelist(path, title, id2meta, fsids, minify=False):
    """
    Write the simple content list to the given path.
    
    @param path: path to write to
    @type path: L{str}
    @param title: category title
    @type title: L{str}
    @param id2meta: a dict mapping story IDs to their metadata
    @type id2meta: L{dict}
    @param fsids: list of fsids to include
    @type fsids: L{list} of L{str}
    @param minify: if nonzero, minify content
    @type minify: L{str}
    """
    letter2titles_and_fsids = {}  # map letter -> [(title, fsids), ...]
    for fsid in fsids:
        meta = id2meta[fsid]
        storytitle = meta.get("title", "???")
        first_letter = "_"
        for letter in storytitle.strip().upper():
            if letter.isalnum():
                first_letter = letter
                break
        if first_letter in letter2titles_and_fsids:
            letter2titles_and_fsids[first_letter].append((storytitle, fsid))
        else:
            letter2titles_and_fsids[first_letter] = [(storytitle, fsid)]
    nav = []
    content = []
    for letter in sorted(letter2titles_and_fsids.keys()):
        nav.append('<A href="#{l}">{l}</A>'.format(l=letter))
        content.append('<H2 id="{l}">{l}</H2>'.format(l=letter))
        content.append('<UL class="linklist">')
        for storytitle, fsid in letter2titles_and_fsids[letter]:
            content.append('<LI><A href="../../stories/{fsid}/cover.html">{title}</A></LI>'.format(fsid=fsid, title=storytitle))
        content.append("</UL>")
    page = SIMPLELIST_TEMPLATE.format(
        title=title,
        contentlist_nav=" ".join(nav),
        content="\n".join(content),
    )
    if minify:
        page = minify_html(page)
    create_file_with_content(path, page)

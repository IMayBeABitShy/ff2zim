"""
Functions and constants for creating the HTML pages and other web content.
"""
import os
import json

from .utils import bleach_name
from .fileutils import create_file_with_content


INDEX_TEMPLATE = """<!DOCTYPE html>
<HTML>
    <HEAD>
        <META charset="UTF-8">
        <title>{title}</title>
        <link rel="stylesheet" href="../../resources/styles.css">
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
    </BODY>
</HTML>
"""

STATPAGE_TEMPLATE = """<!DOCTYPE html>
<HTML>
    <HEAD>
        <META charset="UTF-8">
        <title>Statistics</title>
        <link rel="stylesheet" href="../../resources/styles.css">
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
    </HEAD>
    <BODY onload="brython()">
        <script type="text/python" src="../../resources/sort.py" id="category_sort"></script>
        <H1>{name}</H1>
        <hr>
        <DIV id="sort_settings">
        </DIV>
        <hr>
        <DIV id="table_container">
            <P id="load_message">Loading...</P>
        </DIV>
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
    </HEAD>
    <BODY onload="brython()">
        <script type="text/python" src="../../resources/sort.py" id="author_sort"></script>
        <H1>{name}</H1>
        <hr>
        <P><B>Name:           </B> {name}</P>
        <P><B>ID:             </B> {id}</P>
        <P><B>Fanfiction Link:</B> <A href={authorlink}>{authorlink}</A></P>
        <hr>
        <DIV id="sort_settings">
        </DIV>
        <hr>
        <DIV id="table_container">
            <P id="load_message">Loading...</P>
        </DIV>
    </BODY>
</HTML>
"""

SORT_SCRIPT = """
from javascript import JSON

from browser import document, html

TABLE_CONTAINER = "table_container"
SORT_SETTINGS = "sort_settings"
RATINGS = ["K", "K+", "T", "M", "ALL"]
STATI = ["In-Progress", "Completed", "ALL"]


def load_metadata():
    # load story metadata
    metadatapath = document.location.pathname.replace("/A/", "/-/", 1)
    metadatapath = metadatapath[:metadatapath.rfind("/") + 1] + "stories.json"
    with open(metadatapath, "r") as fin:
        content = fin.read()
    metadata = JSON.parse(content)
    return metadata


def get_sortinfo():
    # return the sort&filter settings
    sortinfo = {}
    sortinfo["sort_by"] = document.query.getfirst("sortBy", "updated")
    sortinfo["reverse"] = (document.query.getfirst("reverse", "0") == "1")
    sortinfo["rating"] = document.query.getfirst("rating", "ALL")
    sortinfo["status"] = document.query.getfirst("status", "ALL")
    return sortinfo


def sort_entries(metadata, sortinfo):
    # sort and filter the entries
    
    filtered = []
    for e in metadata:
        # filter rating
        if sortinfo["rating"] != "ALL":
            if e.get("rating", "M") != sortinfo["rating"]:
                continue
                
        # filter status
        if sortinfo["status"] != "ALL":
            if e.get("status", "???") != sortinfo["status"]:
                continue
        
        filtered.append(e)
        # TODO: filter
    
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
    else:
        raise ValueError("Unknown sort: " + sortname)
    
    if invert_reverse:
        reverse = not sortinfo.get("reverse", False)
    else:
        reverse = sortinfo.get("reverse")
    
    return sorted(filtered, key=sortkey, reverse=reverse)


def create_table(sorted_entries):
    # create the table containing the sorted entries.
    tbl = html.TABLE(border=1, **{"class": "stories"})
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
                    html.A(title, href="../../stories/{}/story.html".format(fsid))
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
    metadata = load_metadata()
    sortinfo = get_sortinfo()
    entries = sort_entries(metadata, sortinfo)
    container = document[TABLE_CONTAINER]
    for child in container.children:
        del document[child.id]
    document[TABLE_CONTAINER] <= create_table(entries)


def create_settings():
    current = get_sortinfo()
    cur_sel = current["sort_by"]
    cur_rating = current["rating"]
    cur_status = current["status"]
    div = html.DIV()
    form = html.FORM(**{"class": "sort_form"})
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
        ],
        id="sortBy",
        name="sortBy",
    )
    form <= html.BR()
    form <= html.LABEL("Reverse Order:", **{"for": "reverse", })
    form <= html.INPUT(type="checkbox", name="reverse", id="reverse", value="1", checked=(current["reverse"]))
    form <= html.BR()
    form <= html.LABEL("Rating:", **{"for": "rating", })
    form <= html.SELECT(
        [html.OPTION(r, value=r, selected=(cur_rating == r)) for r in RATINGS],
        id="rating",
        name="rating",
    )
    form <= html.BR()
    form <= html.LABEL("Status:", **{"for": "status", })
    form <= html.SELECT(
        [html.OPTION(s, value=s, selected=(cur_status == s)) for s in STATI],
        id="status",
        name="status",
    )
    form <= html.BR()
    form <= html.INPUT(type="submit")
    div <= form
    document[SORT_SETTINGS] <= div

create_settings()
update_table()
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
"""


def create_author_page(path, authorinfo, id2meta):
    """
    Create an author page.
    
    @param path: path to author directory
    @type path: L{str}
    @param authorinfo: a dict containing details about the author
    @type authorinfo: L{dict}
    @param id2meta: a dict mapping story IDs to their metadata
    @type id2meta: L{dict}
    """
    assert isinstance(path, str)
    assert isinstance(authorinfo, dict)
    assert isinstance(id2meta, dict)
    if not os.path.exists(path):
        os.mkdir(path)
    pagepath = os.path.join(path, "author.html")
    datapath = os.path.join(path, "stories.json")
    authorcontent = AUTHOR_TEMPLATE.format(
        name=authorinfo["name"],
        authorlink=authorinfo["url"],
        html=authorinfo["html"],
        id=authorinfo["id"],
        )
    create_file_with_content(pagepath, authorcontent)
    metadata = [id2meta[sid] for sid in authorinfo["stories"]]
    create_file_with_content(datapath, json.dumps(metadata))


def create_category_page(path, name):
    """
    Create a category page.
    
    @param path: path to write to
    @type path: L{str}
    @param name: name of categiry
    @type name: L{str}
    """
    assert isinstance(path, str)
    assert isinstance(name, str)
    content = CATEGORY_TEMPLATE.format(name=name)
    create_file_with_content(path, content)


def create_index_page(path, id2meta, category2ids, authordata):
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
    create_file_with_content(path, html)


def create_stats_page(path, id2meta, category2ids, authordata):
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
    create_file_with_content(path, html)


def create_sort_script(path):
    """
    Write the sort script to the given path.
    
    @param path: path to write to
    @type path: L{str}
    """
    create_file_with_content(path, SORT_SCRIPT)


def create_style_file(path):
    """
    Write the CSS style sheet to the given path.
    
    @param path: path to write to
    @type path: L{str}
    """
    create_file_with_content(path, STYLE_CONTENT)

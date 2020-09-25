"""
The command line interface.
"""
import cmd
import shlex
import os
import time
import re
import getpass
from urllib.parse import urljoin, urlparse, parse_qs

from fanficfare.geturls import get_urls_from_text

import requests
import bs4

from .project import Project
from .zimbuild import build_zim
from .exceptions import DirectoryNotEmpty, NotAValidTarget
from .reporter import StdoutReporter
from .target import Target
from .epubconverter import Html2EpubConverter
from .utils import bleach_name
from .fileutils import format_size


class FF2ZIMConsole(cmd.Cmd):
    """
    CLI for ff2zim.
    
    @ivar project: the currently active project
    @type project: L{ff2zim.project.Project} or L{None}
    @ivar reporter: reporter for operation output
    @type reporter: L{ff2zim.reporter.BaseReporter}
    """
    
    intro = "Welcome to ff2zim!\nSee 'help usage' for details."
    prompt = "ff2zim> "
    
    def __init__(self):
        cmd.Cmd.__init__(self)
        
        self.project = None
        self.reporter = StdoutReporter()
    
    def help_usage(self, s=""):
        """
        Print help for the usage.
        """
        print("Usage")
        print("-------------")
        print("1. Create a new project using 'init <path>' or select an existing one using 'select <path>'.")
        print("2. Use 'add <url> to add an URL. Alternatively, edit 'target_urls.txt' in the project directory directly.")
        print("3. Check which fanfics still need to be downloaded using 'list_missing'.")
        print("4. Download all of them using 'download_all'.")
        print("5. Check all downloaded fanfics using 'list_titles'.")
        print("6. Build your ZIM file using 'build <outpath>'.")
        
    
    def do_quit(self, s=""):
        """
        quit: quit.
        """
        print("Goodbye.")
        return True
    
    do_EOF = do_quit
    
    def do_project(self, s):
        """
        project: Print the current project path.
        """
        if self.project is None:
            print("No project path selected. Use 'select' To select one.")
        else:
            print(self.project.path)
    
    def do_select(self, s):
        """
        select <path>: Select the new project path. It must already exist.
        """
        if not Project.is_valid_project(s):
            print("Error: Path '{}' does not refer to a valid project.".format(s))
            print("If it does not yet exist, try 'init <path>' instead.")
            return
        else:
            print("Selecting '{}' as project.".format(s))
            self.project = Project(s)
    
    def do_unselect(self, s):
        """
        unselect: unselect current project
        """
        if self.project is None:
            print("No project selected.")
            return
        else:
            print("Unselecting '{}'...".format(self.project.path))
            self.project = None
    
    def do_init(self, s):
        """
        init <path>: init a new project at path.
        """
        if self.project is not None:
            print("Error: Please 'unselect' current project first.")
            return
        if Project.is_valid_project(s):
            print("Error: It seems like the path refers to a valid project.")
            print("In order to ensure that it will not be overwritten, init has been cancelled.")
            print("If you want to select the given path, use 'select' instead.")
            print("If you want to init the specified path, remove it first.")
            return
        try:
            Project.init_new(s, reporter=self.reporter)
        except DirectoryNotEmpty:
            print("Error: The specified path already contains files.")
            return
        except Exception as e:
            print("Error: {}".format(e))
            if hasattr(e, "message"):
                print(e.message)
            return
        else:
            print("Selecting as current project...")
            self.do_select(s)
            print("Done.")
    
    def do_regenerate_static_resources(self, s):
        """
        regenerate_static_resources: regenerate the static resources.
        """
        if self.project is None:
            print("Error: No project selected.")
            return
        else:
            self.project.populate_resources(reporter=self.reporter)
    
    def do_list_targets(self, s):
        """
        list_targets: list all stories which should be targeted.
        """
        if self.project is None:
            print("Error: No project selected.")
            return
        else:
            targets = self.project.list_targets(exclude_existing=False)
            for target in targets:
                print(str(target))
    
    def do_list_missing(self, s):
        """
        list_missing: list all stories which should be targeted and are not yet stored locally.
        """
        if self.project is None:
            print("Error: No project selected.")
            return
        else:
            targets = self.project.list_targets(exclude_existing=True)
            for target in targets:
                print(str(target))
    
    def do_list_titles(self, s):
        """
        list_titles: list all story titles currently stored locally.
        """
        if self.project is None:
            print("Error: No project selected.")
            return
        else:
            entries = []
            for md in self.project.collect_metadata():
                sab = md.get("siteabbrev", "???")
                sid = md.get("storyId", "???")
                title = md.get("title", "???")
                entries.append((sab, sid, title))
            for sab, sid, title in sorted(entries):
                print("[{}] {} - {}".format(sab, sid, title))
    
    def do_add(self, s):
        """
        add <url>: Add a URL to the target list.
        """
        if self.project is None:
            print("Error: No project selected.")
            return
        try:
            target = Target(s)
        except NotAValidTarget:
            print("Error: Not a valid URL/ID!")
            return
        else:
            if self.project.has_target(target):
                print("Info: Target '{}' already defined, skipping...".format(s))
                return
            else:
                self.project.add_target(s)
    
    def do_add_from_file(self, s):
        """
        add_from_file <path>: Add all URLs/IDS in a file to the target list.
        """
        if self.project is None:
            print("Error: No project selected.")
            return
        elif not os.path.isfile(s):
            print("Error: file '{}' not found!".format(s))
            return
        else:
            with open(s, "r") as fin:
                content = fin.read()
            urls = get_urls_from_text(content)
            for url in urls:
                self.do_add(url)
    
    def do_add_ffn_from_file(self, s):
        """
        add_ffn_from_file <path>: Add all URLs/IDS from ffn in a file to the target list.
        """
        if self.project is None:
            print("Error: No project selected.")
            return
        elif not os.path.isfile(s):
            print("Error: file '{}' not found!".format(s))
            return
        else:
            with open(s, "r") as fin:
                content = fin.read()
            matches = re.findall(r"/s/[0-9]+/", content)
            urls = [urljoin("https://fanfiction.net/", e) for e in matches]
            for url in urls:
                self.do_add(url)
    
    def do_add_ffn_category(self, s):
        """
        add_ffn_category <category_url>: Add all stories from a ffn category URL.
        """
        if self.project is None:
            print("Error: No project selected.")
            return
        page = requests.get(s, params={"srt": "1", "r": "10"}).text
        soup = bs4.BeautifulSoup(page, "html.parser")
        last_a = soup.find("a", text="Last")
        if last_a is not None:
            n_pages = int(parse_qs(urlparse(last_a["href"]).query)["p"][0])
        else:
            next_a = soup.find("a", text="Next")
            if next_a is None:
                n_pages = 1
            else:
                n_pages = int(parse_qs(urlparse(last_a["href"]).query)["p"][0])
        pages = [page]
        for i in range(1, n_pages + 1):
            url = "{}?srt=1&r=10&p={}".format(s, i)
            page = requests.get(url).text
            pages.append(page)
            time.sleep(1)
        all_urls = []
        for page in pages:
            matches = re.findall(r"/s/[0-9]+/", page)
            urls = [urljoin("https://fanfiction.net/", e) for e in matches]
            for url in urls:
                if url not in all_urls:
                    all_urls.append(url)
        
        # efficient insert
        new_urls = sorted(all_urls)
        old_urls = sorted([t.url for t in self.project.list_targets()])
        nnu, nou = len(new_urls), len(old_urls)
        ni, oi = 0, 0
        while ni < nnu:
            if oi >= nou:
                # url is new
                self.project.add_target(new_urls[ni])
                ni += 1
            else:
                nu, ou = new_urls[ni], old_urls[oi]
                if nu != ou:
                    # url is new
                    self.project.add_target(nu)
                    ni += 1
                else:
                    # url is old
                    print("Info: Target '{}' already defined, skipping...".format(nu))
                    ni += 1
                    oi += 1
    
    def do_download_all(self, s):
        """
        download_all: download all targets, except those already downloaded.
        """
        if self.project is None:
            print("Error: No project selected.")
            return
        targets = self.project.list_targets(exclude_existing=True)
        for target in targets:
            target.download(self.project, reporter=self.reporter)
    
    def do_download_n(self, s):
        """
        download_n <n>: download n targets
        """
        try:
            n = int(s)
        except ValueError:
            print("Error: Invalid value: {}".format(repr(s)))
            return
        if n <= 0:
            print("Error: n is smaller than 0.")
            return
        if self.project is None:
            print("Error: No project selected.")
            return
        targets = self.project.list_targets(exclude_existing=True)
        m = min(n, len(targets))
        for i in range(m):
            t = targets[i]
            t.download(self.project, reporter=self.reporter)
    
    def do_build(self, s):
        """
        build <path>: build the project into a ZIM. The ZIM will be written to the specified path.
        """
        if self.project is None:
            print("Error: No project selected.")
            return
        if len(s.strip()) == 0:
            print("Error: No outfile specified.")
            return
        build_zim(self.project, s.strip(), reporter=self.reporter)
    
    def do_set_option(self, s):
        """
        set_option <category> <name> <value>: set an option to value
        """
        if self.project is None:
            print("Error: No project selected.")
            return
        splitted = tuple(shlex.split(s))
        if len(splitted) != 3:
            print("Error: expected 3 arguments!")
            return
        c, n, v = splitted
        self.project.set_option(c, n, v)
    
    def do_get_option(self, s):
        """
        get_option <category> <name>: Show the value of an option
        """
        if self.project is None:
            print("Error: No project selected.")
            return
        splitted = tuple(shlex.split(s))
        if len(splitted) != 2:
            print("Error: expected 2 arguments!")
            return
        c, n = splitted
        o = self.project.get_option(c, n)
        print(o)
    
    def do_list_category_aliases(self, s):
        """
        list_category_aliases: list all category aliases
        """
        if self.project is None:
            print("Error: No project selected.")
            return
        aliases = self.project.get_category_aliases()
        for src in sorted(aliases.keys()):
            dst = aliases[src]
            print("{} -> {}".format(src, dst))
    
    def do_add_category_alias(self, s):
        """
        add_category_alias <src> <dst>: make src an alias of dst
        """
        if self.project is None:
            print("Error: No project selected.")
            return
        splitted = shlex.split(s)
        if len(splitted) != 2:
            print("Error: expected exactly 2 arguments!")
            return
        src = splitted[0]
        dst = splitted[1]
        self.project.add_category_alias(src, dst)
        print("'{}' is now an alias of '{}'.".format(src, dst))
    
    def do_generate_epubs(self, s):
        """
        generate_epubs [--by-category] <outdir>: generate epubs for all stories and save them to outdir.
        """
        if self.project is None:
            print("Error: No project selected.")
            return
        splitted = shlex.split(s)
        seperate_by_categories = False
        if len(splitted) == 0:
            print("Error: no out directory specified!")
            return
        elif len(splitted) == 1:
            outdir = splitted[0]
        elif len(splitted) == 2 and "--by-category" in splitted:
            seperate_by_categories = True
            splitted.remove("--by-category")
            outdir = splitted[0]
        else:
            print("Error: invalid argument count")
            return
        if not os.path.exists(outdir) or not os.path.isdir(outdir):
            print("Error: '{}' does not refer to a valid directory.".format(outdir))
            return
        epubs_meta = self.project.collect_metadata()
        n_epubs = len(epubs_meta)
        with self.reporter.with_progress("Generating EPUBs", n_epubs) as pb:
            storydir = os.path.join(self.project.path, "fanfics")
            n_generated = 0
            start = time.time()
            for meta in epubs_meta:
                siteabbr = meta.get("siteabbrev", "??")
                sitepath = os.path.join(storydir, siteabbr)
                sid = meta["storyId"]
                fdir = os.path.join(sitepath, sid)
                title = meta.get("title", siteabbr + "_" + sid)
                if seperate_by_categories:
                    category = bleach_name(meta.get("category", "???"))
                    cdir = os.path.join(outdir, category)
                    if not os.path.exists(cdir):
                        os.mkdir(cdir)
                    outpath = os.path.join(cdir, title + ".epub")
                else:
                    outpath = os.path.join(outdir, title + ".epub")
                converter = Html2EpubConverter(fdir)
                converter.parse()
                converter.write(outpath)
                n_generated += 1
                pb.advance(1)
        print("Done. Generated {n} EPUBs in {t:.2f}s.".format(
            n=n_generated,
            t=time.time() - start,
            )
        )
    
    def do_list_update_required(self, s):
        """
        list_update_required: List all stories requiring an update.
        """
        if self.project is None:
            print("Error: No project selected.")
            return
        for url in self.project.list_marked_for_update():
            target = Target(url)
            print(str(target))
    
    def do_mark_for_update(self, url):
        """
        mark_for_update <url>: mark an story for update.
        """
        if self.project is None:
            print("Error: No project selected.")
            return
        if len(url) == 0:
            print("Error: missing 'url' parameter.")
            return
        else:
            self.project.set_update_mark(url, True)
    
    def do_check_imap_for_updates(self, s):
        """
        check_imap_for_updates: check the IMAP server for updates.
        """
        if self.project is None:
            print("Error: No project selected.")
            return
        srv = self.project.get_option("imap", "server")
        usr = self.project.get_option("imap", "user")
        pswd = self.project.get_option("imap", "password")
        folder = self.project.get_option("imap", "folder")
        if (srv is None) or (usr is None) or (folder is None):
            print("Error: IMAP not configured.")
            print("Use 'imap_set' to configure IMAP.")
            return
        if pswd is None:
            pswd = getpass.getpass("Password for '{}': ".format(usr))
        self.project.check_imap_for_updates(srv, usr, pswd, folder, reporter=self.reporter)
    
    def do_imap_setup(self, s):
        """
        imap_setup: setup IMAP server update checks.
        """
        if self.project is None:
            print("Error: No project selected.")
            return
        
        print("=========== IMAP SETUP =============")
        print("ff2zim can use fanficfare to check your emails for story updates.")
        print("To do this, please create a new folder on your IMAP server and auto-sort story update mails into that folder.")
        print("Please ensure that IMAP access is allowed and that your server supports SSL.")
        print("WARNING: ff2zim will mark emails containing story IDs as 'read'.")
        print("")
        if input("Continue? (Y/n) ").lower() not in ("y", "yes"):
            print("Aborting.")
            return
        
        server = input("IMAP server host: ")
        user = input("User: ")
        password = getpass.getpass("Password (WARNING: will be stored in plaintext, leave empty to be asked each time): ")
        folder = input("Folder name: ")
        print("Saving...")
        self.project.set_option("imap", "server", server)
        self.project.set_option("imap", "user", user)
        if password:
            self.project.set_option("imap", "password", password)
        self.project.set_option("imap", "folder", folder)
    
    def do_update_all(self, s):
        """
        update_all: update all targets marked for update
        """
        if self.project is None:
            print("Error: No project selected.")
            return
        targets = self.project.list_marked_for_update()
        for target in targets:
            self.project.update(target, reporter=self.reporter)
    
    def do_update_n(self, s):
        """
        update_n <n>: update n targets marked for update
        """
        try:
            n = int(s)
        except ValueError:
            print("Error: Invalid value: {}".format(repr(s)))
            return
        if n <= 0:
            print("Error: n is smaller than 0.")
            return
        if self.project is None:
            print("Error: No project selected.")
            return
        targets = self.project.list_marked_for_update()
        m = min(n, len(targets))
        for i in range(m):
            t = targets[i]
            self.project.update(t, reporter=self.reporter)
    
    def do_stats(self, s):
        """
        stats: print statistics of this project.
        """
        if self.project is None:
            print("Error: No project selected.")
            return
        allstats = self.project.get_stats()
        
        for stats in allstats:
            name = stats.get("name", "???")
            print("==================== {} ===================".format(name))
        
            print("-------------- FILE SIZES --------------")
            to_print = [
                ("All", "size_all"),
                ("Project state", "size_states"),
                ("Project resources", "size_resources"),
                ("Stories", "size_stories"),
                (" -> Texts", "size_story_texts"),
                (" -> Metadata", "size_story_metadata"),
                (" -> Assets", "size_story_assets"),
            ]
            for name, key in to_print:
                size = format_size(stats[key])
                print("{:24s}{:>12}".format(name, size))
            print("-------------- Content Stats --------------")
            to_print = [
                ("Stories", "n_stories"),
                ("Authors", "n_authors"),
                ("Categories", "n_categories"),
                (" -> Aliases", "n_aliases"),
                ("Sources", "n_sources"),
                ("Chapters", "n_chapters"),
                ("Words", "n_words"),
            ]
            for name, key in to_print:
                num = stats[key]
                print("{:24s}{:>12}".format(name, num))



def main():
    """
    The main function.
    
    This will run the CLI.
    """
    cmdo = FF2ZIMConsole()
    cmdo.cmdloop()


if __name__ == "__main__":
    main()

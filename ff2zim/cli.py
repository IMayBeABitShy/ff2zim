"""
The command line interface.
"""
import cmd
import shlex
import os

from .project import Project
from .zimbuild import build_zim
from .exceptions import DirectoryNotEmpty
from .targetutils import is_valid_url_or_id, find_all_ids_in_string
from .reporter import StdoutReporter


class FFN2ZIMConsole(cmd.Cmd):
    """
    CLI for ffn2zim.
    
    @ivar project: the currently active project
    @type project: L{ff2zim.project.Project} or L{None}
    @ivar reporter: reporter for operation output
    @type reporter: L{ff2zim.reporter.BaseReporter}
    """
    
    intro = "Welcome to ffn2zim!\nSee 'help usage' for details."
    prompt = "ffn2zim> "
    
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
            print("Unselecting '{}'...".format(self.project_path))
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
                print(target)
    
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
                print(target)
    
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
                sid = int(md.get("storyId", "0"))
                title = md.get("title", "???")
                entries.append((sid, title))
            for sid, title in sorted(entries):
                print("{} - {}".format(sid, title))
    
    def do_add(self, s):
        """
        add <url or id>: Add a URL or an ID to the target list.
        """
        if self.project is None:
            print("Error: No project selected.")
            return
        elif not is_valid_url_or_id(s):
            print("Error: Not a valid URL/ID!")
            return
        elif self.project.has_target(s):
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
            ids = find_all_ids_in_string(content)
            for sid in ids:
                self.do_add(str(sid))
    
    def do_download_all(self, s):
        """
        download_all: download all targets, except those already downloaded.
        """
        if self.project is None:
            print("Error: No project selected.")
            return
        targets = self.project.list_targets(exclude_existing=True)
        for target in targets:
            self.project.download_target(target, reporter=self.reporter)
    
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
        targets = self.project.list_targets(self.project, exclude_existing=True)
        m = min(n, len(targets))
        for i in range(m):
            t = targets[i]
            self.project.download_target(t, reporter=self.reporter)
    
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



def main():
    """
    The main function.
    
    This will run the CLI.
    """
    cmdo = FFN2ZIMConsole()
    cmdo.cmdloop()


if __name__ == "__main__":
    main()

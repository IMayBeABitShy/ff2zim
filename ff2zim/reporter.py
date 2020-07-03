"""
Reporter definitions.

A Reporter informs a UI of the state.
"""
from contextlib import contextmanager


class BaseReporter(object):
    """
    Base class for all reporters.
    """
    def msg(self, s, end="\n"):
        """
        Print a message.
        
        @param s: message to print
        @type s: L{str}
        @param end: what to print after the message. Default: linebreak
        @typ end: l{str}
        """
        pass
    
    @contextmanager
    def with_progress(self, description, max):
        """
        This is a context manager which returns a BaseProgressReporter usable
        to indicate progress.
        
        @param description: description for progress
        @type description: L{str}
        @param max: max progress value
        @type max: L{int}
        @return: a context manager whose value can be used for progress indication.
        @rtype: contextmanager with L{BaseProgressReporter}
        """
        bpr = BaseProgressReporter(description, max)
        try:
            yield bpr
        finally:
            bpr.finish()


class BaseProgressReporter(object):
    """
    Base class for ProgressReporters.
    This is used as a context value from L{BaseReporter.with_progress}.
    
    @param description: description for progress
    @type description: L{str}
    @param max: max progress value
    @type max: L{int}
    """
    def __init__(self, description, max):
        self.description = description
        self.max = max
        self.steps = 0
    
    def advance(self, n):
        """
        Advance the progress by n steps.
        
        @param n: number of steps to advance
        @type n: L{int}
        """
        self.steps += n
    


class VoidReporter(BaseReporter):
    """
    A Reporter discarding all messages.
    """
    def msg(self, s, end="\n"):
        pass
    
    @contextmanager
    def with_progress(self, description, max):
        yield VoidProgressReporter(description, max)


class VoidProgressReporter(BaseProgressReporter):
    """
    ProgressReporter used by L{VoidReporter}.
    """
    pass


class StdoutReporter(BaseReporter):
    """
    A Reporter printing all messages.
    """
    def msg(self, s, end="\n"):
        print(s, end=end, flush=True)
    
    @contextmanager
    def with_progress(self, description, max):
        spr = StdoutProgressReporter(description, max)
        try:
            yield spr
        finally:
            spr.finish()


class StdoutProgressReporter(BaseProgressReporter):
    """
    Progress reporter used by L{StdoutReporter}.
    
    @cvar BAR_LENGTH: length of progress bar to print
    @type BAR_LENGTH: L{int}
    """
    
    BAR_LENGTH = 20
    
    def advance(self, steps):
        self.steps += steps
        self.print_progress()
    
    def print_progress(self):
        """
        Print the current progress.
        """
        progress = int((self.steps / self.max) * self.BAR_LENGTH)
        if progress == self.BAR_LENGTH:
            # reduce by one so the arrow is correct
            progress -= 1
        bar = "[" + "=" * (progress - 1) + ">" + " " * (self.BAR_LENGTH - progress -1) + "]"
        print("{} {} ".format(self.description, bar), end="\r")
    
    def finish(self):
        bar = "[" + "=" * self.BAR_LENGTH + "] "
        print("{} {}".format(self.description, bar))


if __name__ == "__main__":
    # test code
    import time
    rep = StdoutReporter()
    rep.msg("Beginning test...")
    with rep.with_progress("test", 300) as pb:
        for i in range(300):
            pb.advance(1)
            time.sleep(0.02)
    rep.msg("Done.")

"""
Reporter definitions.

A Reporter informs a UI of the state.
"""


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


class VoidReporter(BaseReporter):
    """
    A Reporter discarding all messages.
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


class StdoutReporter(BaseReporter):
    """
    A Reporter printing all messages.
    """
    def msg(self, s, end="\n"):
        """
        Print a message.
        
        @param s: message to print
        @type s: L{str}
        @param end: what to print after the message. Default: linebreak
        @typ end: l{str}
        """
        print(s, end=end, flush=True)

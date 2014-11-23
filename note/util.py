import subprocess as SP
import os

itemTypes = ["notes", "todos", "contacts", "places"]

colors = dict()
colors['reset'] = "\033[0m"         # reset
colors['hicolor'] = "\033[1m"       # hicolor
colors['underline'] = "\033[4m"     # underline
colors['invert'] = "\033[7m"        # invert foreground and background
colors['foreground black'] = "\033[30m"
colors['foreground red'] = "\033[31m"
colors['foreground green'] = "\033[32m"
colors['foreground yellow'] = "\033[33m"
colors['foreground blue'] = "\033[34m"
colors['foreground magenta'] = "\033[35m"
colors['foreground cyan'] = "\033[36m"
colors['foreground white'] = "\033[37m"
colors['background black'] = "\033[40m"
colors['background red'] = "\033[41m"
colors['background green'] = "\033[42m"
colors['background yellow'] = "\033[43m"
colors['background blue'] = "\033[44m"
colors['background magenta'] = "\033[45m"
colors['background cyan'] = "\033[46m"
colors['background white'] = "\033[47m"


def scrubID(ID):
    """
        :param ID: An ID that can be of various types, this is very kludgy
        :returns: An integer ID
    """

    if type(ID) == list:
        return int(ID[0])
    elif type(ID) == str:
        return int(ID)
    elif type(ID) == int:
        return ID
    else:
        return None


def which(bin_name):
    """
        :param bin_name: the name of the binary to test for (e.g. vim)
        :returns: True or False depending on wether the binary exists
    """

    with open(os.devnull) as devnull:
        #rc = SP.call(['which', bin_name], stdout=devnull, stderr=devnull)
        rc = SP.call(['which', bin_name])

    return rc  # == 0

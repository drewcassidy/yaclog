import os
from yaclog.changelog import Changelog


def read(path: os.PathLike):
    """
    Create a new Changelog object from the given path
    :param path: a path to a markdown changelog file
    :return: a parsed Changelog object
    """
    return Changelog(path)

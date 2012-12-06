from models import CommentPlus
from forms import CommentPlusForm


def get_model():
    return CommentPlus


def get_form():
    return CommentPlusForm

VERSION = (1, 0, 0, 'a', 1)


def get_version():
    version = '%s.%s' % (VERSION[0], VERSION[1])
    if VERSION[2]:
        version = '%s.%s' % (version, VERSION[2])
    if VERSION[3] != 'f':
        version = '%s%s%s' % (version, VERSION[3], VERSION[4])
    return version

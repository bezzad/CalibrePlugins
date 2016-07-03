# vim:fileencoding=UTF-8:ts=4:sw=4:sta:et:sts=4:ai

from __future__ import (unicode_literals, division, absolute_import,
                        print_function)

__license__   = 'GPL v3'
__docformat__ = 'restructuredtext en'


from calibre.customize import EditBookToolPlugin

PLUGIN_NAME = "Remove garbage tags no ui"
PLUGIN_SAFE_NAME = PLUGIN_NAME.strip().lower().replace(' ', '_')
PLUGIN_DESCRIPTION = 'A tool for ebook editing.'
PLUGIN_VERSION_TUPLE = (1, 1, 0)
PLUGIN_VERSION = '.'.join([str(x) for x in PLUGIN_VERSION_TUPLE])
PLUGIN_AUTHORS = 'Rooholah Abolhasani'

class EditingToolbagPlugin(EditBookToolPlugin):

    name = PLUGIN_NAME
    version = PLUGIN_VERSION_TUPLE
    author = PLUGIN_AUTHORS
    supported_platforms = ['windows', 'osx', 'linux']
    description = PLUGIN_DESCRIPTION
    minimum_calibre_version = (1, 46, 0)

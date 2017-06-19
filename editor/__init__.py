from __future__ import (unicode_literals, division, absolute_import,
                        print_function)

__license__ = 'GPL v3'
__copyright__ = '2017, taaghche.ir'

from calibre.customize import EditBookToolPlugin


class DemoPlugin(EditBookToolPlugin):

    name = 'Edit Book plugin'
    version = (1, 0, 1)
    author = 'Iman Dolatkia'
    supported_platforms = ['windows', 'osx', 'linux']
    description = 'customization for taaghche epubs'
    minimum_calibre_version = (1, 46, 0)

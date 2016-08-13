from __future__ import (unicode_literals, division, absolute_import,
                        print_function)

__license__ = 'GPL v3'
__copyright__ = '2016, taaghche.ir'

from calibre.customize import EditBookToolPlugin


class DemoPlugin(EditBookToolPlugin):

    name = 'indd to epub initial settings'
    version = (1, 0, 0)
    author = 'Rooholah Abolhasani'
    supported_platforms = ['windows', 'osx', 'linux']
    description = 'Some modifications in epub file'
    minimum_calibre_version = (1, 46, 0)

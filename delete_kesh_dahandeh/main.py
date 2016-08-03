#!/usr/bin/env python2
# vim:fileencoding=utf-8
from __future__ import (unicode_literals, division, absolute_import,
                        print_function)

import re
from PyQt5.Qt import QAction, QMenu, QApplication, QMessageBox
from calibre.gui2.tweak_book.plugin import Tool
from calibre.ebooks.oeb.base import XPath, OEB_DOCS, OPF_MIME
from calibre.utils.config import JSONConfig



class delete_kesh_dahandeh(Tool):
    #: Set this to a unique name it will be used as a key
    name = 'DeleteKeshDahandeh'

    #: If True the user can choose to place this tool in the plugins toolbar
    allowed_in_toolbar = True

    #: If True the user can choose to place this tool in the plugins menu
    allowed_in_menu = True

    def create_action(self, for_toolbar=True):
        # Create an action, this will be added to the plugins toolbar and
        # the plugins menu
        ac = QAction(get_icons('images/kesh.png'), 'حذف کاراکترهای کش دهنده', self.gui)
        if not for_toolbar:
            # Register a keyboard shortcut for this toolbar action. We only
            # register it for the action created for the menu, not the toolbar,
            # to avoid a double trigger
            self.register_shortcut(ac, 'Delete_kesh_dahandeh', default_keys=('Ctrl+Shift+Alt+E',))
        ac.triggered.connect(self.add_persian_and_page_direction)
        return ac

    def add_persian_and_page_direction(self):
        self.boss.commit_all_editors_to_container()
        self.boss.add_savepoint('Before: DeleteKeshDahandeh')
        container = self.current_container  # The book being edited as a container object
        for name, media_type in container.mime_map.iteritems():
            if media_type in OEB_DOCS:
                for item in container.parsed(name).getroottree().iter():
                    if item.text is not None:
                        item.text = re.sub(ur"([^ \w><:+=\.1234567890۱۲۳۴۵۶۷۸۹۰])([\u0640]{1,})([^ \w><:+=\.1234567890۱۲۳۴۵۶۷۸۹۰])", ur"\1\3", item.text)
                        item.text = re.sub(ur"([^ \w><:+=\.1234567890۱۲۳۴۵۶۷۸۹۰])([\u0640]{1,})([^ \w><:+=\.1234567890۱۲۳۴۵۶۷۸۹۰])", ur"\1\3", item.text)
                        container.dirty(name)

        # Show the user what changes we have made, allowing her to
        # revert them if necessary
        # self.boss.show_current_diff()
        QMessageBox.information(self.gui, ":)","Process successfuly completed.")
        # Update the editor UI to take into account all the changes we
        # have made
        self.boss.apply_container_update_to_gui()

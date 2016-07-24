# vim:fileencoding=UTF-8:ts=4:sw=4:sta:et:sts=4:ai

from __future__ import (unicode_literals, division, absolute_import,
                        print_function)

__license__   = 'GPL v3'
__docformat__ = 'restructuredtext en'

try:
    from PyQt5.Qt import QAction, QMenu, QDialog
except:
    from PyQt4.Qt import QAction, QMenu, QDialog

from PyQt5.Qt import QAction, QMenu, QApplication, QMessageBox
from calibre.gui2.tweak_book.plugin import Tool
from calibre.gui2.tweak_book import editor_name
from calibre.gui2 import error_dialog, info_dialog
from calibre.ebooks.oeb.polish.container import OEB_DOCS, OEB_STYLES

from calibre.utils.config import JSONConfig
from calibre_plugins.diaps_toolbag.resources.html_parser import MarkupParser
from calibre_plugins.diaps_toolbag.resources.smartypants import smartyPants
from calibre_plugins.diaps_toolbag.utilities import unescape
from calibre_plugins.diaps_toolbag.dialogs import ResultsDialog

from calibre_plugins.diaps_toolbag.__init__ import PLUGIN_SAFE_NAME

from lxml import etree

class SpanDivEdit(Tool):
    name = 'SpanDivEdit'

    #: If True the user can choose to place this tool in the plugins toolbar
    allowed_in_toolbar = True

    #: If True the user can choose to place this tool in the plugins menu
    allowed_in_menu = True

    def create_action(self, for_toolbar=True):
        self.plugin_prefs = JSONConfig('plugins/{0}_SpanDivEdit'.format(PLUGIN_SAFE_NAME))
        self.plugin_prefs.defaults['parse_current'] = True

        # Create an action, this will be added to the plugins toolbar and
        # the plugins menu
        ac = QAction(get_icons('images/spandivedit_icon.png'), _('حذف تگ های اضافه'), self.gui)
        self.restore_prefs()
        if not for_toolbar:
            # Register a keyboard shortcut for this toolbar action. We only
            # register it for the action created for the menu, not the toolbar,
            # to avoid a double trigger
            self.register_shortcut(ac, 'edit-spans-divs', default_keys=('Ctrl+Shift+Alt+E',))
        else:
            menu = QMenu()
            ac.setMenu(menu)
            checked_menu_item = menu.addAction(_('Edit current file only'), self.toggle_parse_current)
            checked_menu_item.setCheckable(True)
            checked_menu_item.setChecked(self.parse_current)
            menu.addSeparator()
            config_menu_item = menu.addAction(_('Customize'), self.show_configuration)
        ac.triggered.connect(self.dispatcher)
        return ac

    def toggle_parse_current(self):
        self.parse_current = not self.parse_current
        self.save_prefs()

    def dispatcher(self):
        container = self.current_container  # The book being edited as a container object
        if not container:
            return info_dialog(self.gui, _('هیچ کتابی باز نیست'),
                        _('لطفا اول یک کتاب را باز کنید'), show=True)
        if self.parse_current:
            name = editor_name(self.gui.central.current_editor)
            if not name or container.mime_map[name] not in OEB_DOCS:
                return info_dialog(self.gui, _('Cannot Process'),
                        _('No file open for editing or the current file is not an (x)html file.'), show=True)

        self.cleanasawhistle = True
        self.changed_files = []

        # criteria1 = ('rtl', 'normal', 'span', 'dir', 'delete', None, '', False)
        # criteria2 = ('ltr', 'normal', 'span', 'dir', 'delete', None, '', False)
        # criteria3 = ('', 'normal', 'span', None, 'delete', None, '', False)

        self.boss.commit_all_editors_to_container()
        self.boss.add_savepoint(_('Before: Span Div Edit'))

        attrs = []
        for name, media_type in container.mime_map.iteritems() :
            if media_type in OEB_DOCS :
                for node in container.parsed(name).getroottree().iter() :
                    for x in node.keys():
                        if x != 'class' and x != 'style' :
                            attrs.append(x)
        
        attrs = sorted(set(attrs))
        # QMessageBox.information(self.gui, "salam", "Here!")
        criterias = []
        for x in attrs:
            criterias.append(('.*', 'regex', 'span', str(x), 'delete', None, '', False))
        criterias.append((None, 'normal', 'span', None, 'delete', None, '', False))
        criterias.append(('.*', 'regex', 'table', 'class', 'delete', None, '', False))
        criterias.append((None, 'normal', 'tr', None, 'delete', None, '', False))
        criterias.append((None, 'normal', 'tbody', None, 'delete', None, '', False))
        criterias.append(('.*', 'regex', 'td', 'class', 'delete', None, '', False))
        QMessageBox.information(self.gui, "salam", "chos!")
        try:
            # self.process_files(criteria1)
            # self.process_files(criteria2)
            # self.process_files(criteria3)
            for cri in criterias :
                self.process_files(cri)
            QMessageBox.information(self.gui, "Success", "ویرایش تگ ها با موفقیت انجام شد")
        except Exception:
            # Something bad happened report the error to the user
            import traceback
            error_dialog(self.gui, _('خطا'),
                _('ویرایش تگ ها انچام نشد.'),
                det_msg=traceback.format_exc(), show=True)
            # Revert to the saved restore point
            self.boss.revert_requested(self.boss.global_undo.previous_container)
        else:
            if not self.cleanasawhistle:
                # Show the user what changes we have made,
                # allowing then to revert them if necessary
                accepted = ResultsDialog(self.gui, self.changed_files).exec_()
                if accepted == QDialog.Accepted:
                    self.boss.show_current_diff()
                # Update the editor UI to take into account all the changes we
                # have made
                self.boss.apply_container_update_to_gui()
            else:
                info_dialog(self.gui, _('هیچی تغییر نکرد'),
                '<p>{0}'.format(_('هیچ تگی با این شرایط پیدا نشد.')), show=True)

    def process_files(self, criteria):
        container = self.current_container  # The book being edited as a container object
        
        for name, media_type in container.mime_map.iteritems() :
            if media_type in OEB_DOCS :
                if self.parse_current:
                    # name = editor_name(self.gui.central.current_editor)
                    data = etree.tostring(container.parsed(name).getroottree(), encoding = 'unicode')
                    # data = etree.ElementTree.parse(name)
                    htmlstr = self.delete_modify(data, criteria)
                    if htmlstr != data:
                        self.cleanasawhistle = False
                        container.open(name, 'wb').write(htmlstr.encode('utf-8'))
                else:
                    from calibre_plugins.diaps_toolbag.dialogs import ShowProgressDialog
                    d = ShowProgressDialog(self.gui, container, OEB_DOCS, criteria, self.delete_modify, _('Parsing'))
                    self.cleanasawhistle = d.clean
                    self.changed_files.extend(d.changed_files)

    def delete_modify(self, data, criteria):
        _parser = MarkupParser(data, srch_str=criteria[0], srch_method=criteria[1], tag=criteria[2], attrib=criteria[3],
                               action=criteria[4], new_tag=criteria[5], new_str=criteria[6], copy=criteria[7])

        htmlstr = _parser.processml()
        return htmlstr

    def show_configuration(self):
        from calibre_plugins.diaps_toolbag.span_div_config import ConfigWidget
        dlg = ConfigWidget(self.gui)
        if dlg.exec_():
            pass

    def restore_prefs(self):
        self.parse_current = self.plugin_prefs.get('parse_current')

    def save_prefs(self):
        self.plugin_prefs['parse_current'] = self.parse_current

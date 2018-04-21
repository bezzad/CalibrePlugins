# vim:fileencoding=UTF-8:ts=4:sw=4:sta:et:sts=4:ai

from __future__ import (unicode_literals, division, absolute_import,
                        print_function)

__license__ = 'GPL v3'
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
from calibre.ebooks.oeb.base import XPath
from calibre.utils.config import JSONConfig
from calibre_plugins.diaps_toolbag.resources.html_parser import MarkupParser
from calibre_plugins.diaps_toolbag.resources.smartypants import smartyPants
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
            return QMessageBox.information(self.gui, "Success", "لطفا اول یک کتاب را باز کنید")

        if self.parse_current:
            name = editor_name(self.gui.central.current_editor)
            if not name or container.mime_map[name] not in OEB_DOCS:
                return QMessageBox.information(self.gui, "Success", "لطفا اول یک فایل html را باز کنید")

        self.cleanasawhistle = True
        self.changed_files = []

        # criteria1 = ('rtl', 'normal', 'span', 'dir', 'delete', None, '', False)
        # criteria2 = ('ltr', 'normal', 'span', 'dir', 'delete', None, '', False)
        # criteria3 = ('', 'normal', 'span', None, 'delete', None, '', False)

        self.boss.commit_all_editors_to_container()
        self.boss.add_savepoint(_('Before: Span Div Edit'))

        attrs = []
        for name, media_type in container.mime_map.iteritems():
            if media_type in OEB_DOCS:
                for node in container.parsed(name).getroottree().iter():
                    for x in node.keys():
                        if x != 'class' and x != 'style' and x != 'id':
                            attrs.append(x)

        attrs = sorted(set(attrs))

        criterias = []
        for x in attrs:
            criterias.append(('.*', 'regex', 'span', str(x), 'delete', None, '', False))
        criterias.append((None, 'normal', 'span', None, 'delete', None, '', False))
        criterias.append(('.*', 'regex', 'table', 'class', 'delete', None, '', False))
        criterias.append((None, 'normal', 'tr', None, 'delete', None, '', False))
        criterias.append((None, 'normal', 'tbody', None, 'delete', None, '', False))
        criterias.append(('.*', 'regex', 'td', 'class', 'delete', None, '', False))

        try:
            for cri in criterias:
                self.process_files(cri)

            # Craw same tags to combining
            marge_done = self.combine_same_tags("span") | self.combine_same_tags("b") | self.remove_extra_tags("br")
            if marge_done:
                QMessageBox.information(self.gui, "Combine Same Tags",
                                        "Combination of 'b' and 'span' and 'br' tags completed")
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
                self.boss.show_current_diff()

                # Update the editor UI to take into account all the changes we
                # have made
                self.boss.apply_container_update_to_gui()
            else:
                QMessageBox.information(self.gui, "Success", "موردی پیدا نشد")

    def process_files(self, criteria):
        container = self.current_container  # The book being edited as a container object

        for name, media_type in container.mime_map.iteritems():
            if media_type in OEB_DOCS:
                if self.parse_current:
                    # name = editor_name(self.gui.central.current_editor)
                    data = etree.tostring(container.parsed(name).getroottree(), encoding='unicode')
                    # data = etree.ElementTree.parse(name)
                    htmlstr = self.delete_modify(data, criteria)
                    if htmlstr != data:
                        self.cleanasawhistle = False
                        container.open(name, 'wb').write(htmlstr.encode('utf-8'))
                        container.parsed(name)
                        container.dirty(name)
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

    def combine_same_tags(self, tag):
        if tag is None or tag == "":
            return False

        done = False
        try:
            # self.boss.commit_all_editors_to_container()
            # self.boss.add_savepoint('Before: ChangeSplittingTag_' + tag)

            tag = tag.lower()

            # The book being edited as a container object
            container = self.current_container

            for name, media_type in container.mime_map.iteritems():
                if media_type in OEB_DOCS:  # A HTML file. Parsed HTML files are lxml elements
                    # for node in container.parsed(name).getroottree().iter(): # read line by line
                    for body in XPath('//h:body')(container.parsed(name)):  # read xml nodes
                        done |= self.combine_same_tags_crawler(body, tag)
                        container.dirty(name)

            # Tell the container that we have changed
            if done:
                self.cleanasawhistle = False
        except Exception as e:
            QMessageBox.information(self.gui, "main Err", "error({0}): {1}".format(type(e), e.args))
            return False
        else:
            # Show the user what changes we have made, allowing her to
            # revert them if necessary
            # self.boss.show_current_diff()
            #
            # Update the editor UI to take into account all the changes we
            # have made
            # self.boss.apply_container_update_to_gui()
            return done

    def combine_same_tags_crawler(self, node, tag):
        if node is None or tag is None:
            return False

        found = False
        try:
            children = node.getchildren()

            if children is not None:
                count = len(children)

                if count > 0:  # Crow just for first child
                    found |= self.combine_same_tags_crawler(children[0], tag)

                if count > 1:  # CROW Pair Nodes
                    # 1 <-- last
                    for index in range(count - 1, 0, -1):
                        pre_node = children[index - 1]
                        this_node = children[index]

                        # check children of this node
                        found |= self.combine_same_tags_crawler(this_node, tag)

                        # combine any this and preview node
                        # marge tags if two tag is same and after first tag is empty or whitespace!
                        if this_node.tag.lower().endswith(tag) and pre_node.tag.lower().endswith(tag) and \
                                (pre_node.tail is None or pre_node.tail.decode('utf-8').isspace()):
                            found |= self.combine_same_tags_sibling(this_node, pre_node, tag)

        except Exception as e:
            QMessageBox.information(self.gui, "Crawler Err", "error({0}): {1}".format(type(e), e.args))
            return False
        else:
            return found

    def combine_same_tags_sibling(self, this_node, pre_node, tag):
        if this_node is None or pre_node is None or tag is None:
            return False

        """ node members:
                node.['_init', 'addnext', 'addprevious', 'append', 'attrib', 'base',
                      'clear', 'extend', 'find', 'findall', 'findtext', 'get', 'getchildren',
                      'getiterator', 'getnext', 'getparent', 'getprevious', 'getroottree',
                      'index', 'insert', 'items', 'iter', 'iterancestors', 'iterchildren',
                      'iterdescendants', 'iterfind', 'itersiblings', 'itertext', 'keys',
                      'makeelement', 'nsmap', 'prefix', 'remove', 'replace', 'set',
                      'sourceline', 'tag', 'tail', 'text', 'values', 'xpath']
        """

        done = False
        try:
            __isEqualNext = True
            pre_node_keys = [] if pre_node.keys() is None else pre_node.keys()
            this_node_keys = [] if this_node.keys() is None else this_node.keys()
            # Check all keys of two nodes without duplicate key:
            for key in (pre_node_keys + list(set(this_node_keys) - set(pre_node_keys))):
                if key.lower() == "dir":
                    pre_node.attrib.pop(key, 0)  # remove 'dir' attribute
                    this_node.attrib.pop(key, 0)  # remove 'dir' attribute
                elif key.lower() == "class" or key.lower() == "style":
                    if not (key in this_node_keys and key in pre_node_keys and
                            set(pre_node.attrib[key].split()) == set(this_node.attrib[key].split())):
                        __isEqualNext = False
                        break

            # If the this node is same by preview node
            if __isEqualNext:
                # Combine this_node by pre_node
                pre_node.text = "" if pre_node.text is None else pre_node.text
                pre_node_tail = "" if pre_node.tail is None else pre_node.tail
                this_children = this_node.getchildren()
                pre_children = pre_node.getchildren()

                if this_children is not None and len(this_children) > 0:
                    # Add this node children's to preview node
                    pre_node.extend(this_children)

                if this_node.text is not None:
                    # add next node text and tail to end (tail) of this node children's
                    if pre_children is not None and len(pre_children) > 0:
                        last_pre_node_child = pre_children[len(pre_children)-1]
                        last_pre_node_child.tail = "" if last_pre_node_child.tail is None else last_pre_node_child.tail
                        last_pre_node_child.tail += this_node.text
                    else:
                        pre_node.text += pre_node_tail + this_node.text

                    # add next node tail to following of preview node tail
                    pre_node.tail = this_node.tail

                # at the end remove this node
                this_node.getparent().remove(this_node)

                done = True
        except Exception as e:
            QMessageBox.information(self.gui, "Sibling Err", "error({0}): {1}".format(type(e), e.args))
            return False
        else:
            return done

    def remove_extra_tags(self, tag):
        done = False
        try:
            # The book being edited as a container object
            container = self.current_container

            for name, media_type in container.mime_map.iteritems():
                if media_type in OEB_DOCS:  # A HTML file. Parsed HTML files are lxml elements
                    for body in XPath('//h:body')(container.parsed(name)):  # read xml nodes
                        done |= self.remove_tag(body, tag)
                        container.dirty(name)

            # Tell the container that we have changed
            if done:
                self.cleanasawhistle = False
        except Exception as e:
            QMessageBox.information(self.gui, "Remove Extra Tags Err", "error({0}): {1}".format(type(e), e.args))
            return False
        else:
            return done

    def remove_tag(self, this_node, tag):
        found = False

        if this_node is None or tag is None:
            return found

        try:
            if this_node.tag.lower().endswith(tag):
                # remove this node
                this_node.getparent().remove(this_node)
                found = True
            else:
                children = this_node.getchildren()
                if children is not None:
                    count = len(children)
                    if count > 0:  # Crow all child
                        # 1 <-- last
                        for index in range(count - 1, -1, -1):
                            found |= self.remove_tag(children[index], tag)
        except Exception as e:
            QMessageBox.information(self.gui, "Remove Tag Err", "error({0}): {1}".format(type(e), e.args))
            return False
        else:
            return found

    @staticmethod
    def get_members(class_name):
        members = [attr for attr in dir(class_name) if not attr.startswith("__")]
        # add 'not callable(getattr(class_name, attr))' condition to show just variables without methods
        return members

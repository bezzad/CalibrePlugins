#!/usr/bin/env python2
# vim:fileencoding=utf-8
from __future__ import (unicode_literals, division, absolute_import,
                        print_function)

import re
from PyQt5.Qt import QAction, QMenu, QApplication, QMessageBox
from calibre.gui2.tweak_book.plugin import Tool
from calibre.ebooks.oeb.base import XPath, OEB_DOCS, OPF_MIME
from calibre.utils.config import JSONConfig


######################################################################################################
################################## Change english num to persian in sup  #############################
######################################################################################################
class ChangeSupEnglishNum(Tool):
    #: Set this to a unique name it will be used as a key
    name = 'ChangeSupEnglishNum'

    #: If True the user can choose to place this tool in the plugins toolbar
    allowed_in_toolbar = True

    #: If True the user can choose to place this tool in the plugins menu
    allowed_in_menu = True

    def create_action(self, for_toolbar=True):
        # Create an action, this will be added to the plugins toolbar and
        # the plugins menu
        ac = QAction(get_icons('images/convert_num.png'), 'فارسی کردن اعداد بالانویس', self.gui)
        if not for_toolbar:
            # Register a keyboard shortcut for this toolbar action. We only
            # register it for the action created for the menu, not the toolbar,
            # to avoid a double trigger
            self.register_shortcut(ac, 'edit-spans-divs', default_keys=('Ctrl+Shift+Alt+E',))
        ac.triggered.connect(self.add_persian_and_page_direction)
        return ac

    def add_persian_and_page_direction(self):
        self.boss.commit_all_editors_to_container()
        self.boss.add_savepoint('Before: ChangeSupEnglishNum')
        container = self.current_container  # The book being edited as a container object
        for name, media_type in container.mime_map.iteritems():
            if media_type in OEB_DOCS:
                # The prefix // means search at any level of the document.
                for item in XPath('//h:sup/h:sup/h:a | //h:sup/h:a/h:sup | //h:a/h:sup')(container.parsed(name)):
                    if item.text is not None:
                        item.text = re.sub(r"0", r"۰", item.text)
                        item.text = re.sub(r"1", r"۱", item.text)
                        item.text = re.sub(r"2", r"۲", item.text)
                        item.text = re.sub(r"3", r"۳", item.text)
                        item.text = re.sub(r"4", r"۴", item.text)
                        item.text = re.sub(r"5", r"۵", item.text)
                        item.text = re.sub(r"6", r"۶", item.text)
                        item.text = re.sub(r"7", r"۷", item.text)
                        item.text = re.sub(r"8", r"۸", item.text)
                        item.text = re.sub(r"9", r"۹", item.text)
                        container.dirty(name)

        # Show the user what changes we have made, allowing her to
        # revert them if necessary
        self.boss.show_current_diff()

        # Update the editor UI to take into account all the changes we
        # have made
        self.boss.apply_container_update_to_gui()


######################################################################################################
###################################### Add persian and page direction  ###############################
######################################################################################################
class AddPersianAndDirection(Tool):
    #: Set this to a unique name it will be used as a key
    name = 'AddPersianAndDirection'

    #: If True the user can choose to place this tool in the plugins toolbar
    allowed_in_toolbar = True

    #: If True the user can choose to place this tool in the plugins menu
    allowed_in_menu = True

    def create_action(self, for_toolbar=True):
        # Create an action, this will be added to the plugins toolbar and
        # the plugins menu
        ac = QAction(get_icons('images/persian.png'), 'افزودن زبان فارسی و جهت ورق خوردن', self.gui)
        if not for_toolbar:
            # Register a keyboard shortcut for this toolbar action. We only
            # register it for the action created for the menu, not the toolbar,
            # to avoid a double trigger
            self.register_shortcut(ac, 'edit-spans-divs', default_keys=('Ctrl+Shift+Alt+E',))
        ac.triggered.connect(self.add_persian_and_page_direction)
        return ac

    def add_persian_and_page_direction(self):
        self.boss.commit_all_editors_to_container()
        self.boss.add_savepoint('Before: AddPersianAndDirection')
        container = self.current_container  # The book being edited as a container object
        persianResult = 'false'
        directionResult = 'false'
        for name, media_type in container.mime_map.iteritems():
            if media_type in OPF_MIME:
                # The prefix // means search at any level of the document.
                # for item in XPath('//h:spine')(container.parsed(name)):
                for item in container.parsed(name):
                    if item.tag == '{http://www.idpf.org/2007/opf}spine':
                        item.attrib['page-progression-direction'] = 'rtl'
                        directionResult = 'true'

                    for i in item:
                        if i.tag == '{http://purl.org/dc/elements/1.1/}language':
                            i.text = 'fa'
                            persianResult = 'true'

                if directionResult == 'true' and persianResult == 'true':
                    QMessageBox.information(self.gui, "salam", "کتاب فارسی شد" + "\n" + "جهت ورق خوردن راست به چپ شد")
                    container.dirty(name)
                    # Update the editor UI to take into account all the changes we
                    # have made
                    self.boss.apply_container_update_to_gui()
                else:
                    QMessageBox.information(self.gui,
                                            "salam", "خطا در انجام عملیات" + "\n" + "لطفا به صورت دستی انجام دهید")


######################################################################################################
###################################### Persian momayez and date  #####################################
######################################################################################################
class FixPersianDateAndMomayez(Tool):
    #: Set this to a unique name it will be used as a key
    name = 'FixPersianDateAndMomayez'

    #: If True the user can choose to place this tool in the plugins toolbar
    allowed_in_toolbar = True

    #: If True the user can choose to place this tool in the plugins menu
    allowed_in_menu = True

    def create_action(self, for_toolbar=True):
        # Create an action, this will be added to the plugins toolbar and
        # the plugins menu
        ac = QAction(get_icons('images/momayez.png'), 'درست کردن تاریخ و ممیز فارسی', self.gui)
        # self.restore_prefs()
        if not for_toolbar:
            # Register a keyboard shortcut for this toolbar action. We only
            # register it for the action created for the menu, not the toolbar,
            # to avoid a double trigger
            self.register_shortcut(ac, 'smarter-punctuation', default_keys=('Ctrl+Shift+Alt+S',))
        ac.triggered.connect(self.brows_html_files)
        return ac

    def brows_html_files(self):
        # Ensure any in progress editing the user is doing is present in the container
        self.boss.commit_all_editors_to_container()

        # create a restore point so that the user can undo all changes we make.
        self.boss.add_savepoint('Before: FixPersianDateAndMomayez')

        container = self.current_container  # The book being edited as a container object

        for name, media_type in container.mime_map.iteritems():
            if media_type in OEB_DOCS:
                # The prefix // means search at any level of the document.
                for item in container.parsed(name):
                    for child in item:
                        self.pars_html(child)
                container.dirty(name)

        # Show the user what changes we have made, allowing her to
        # revert them if necessary
        self.boss.show_current_diff()

        # Update the editor UI to take into account all the changes we
        # have made
        self.boss.apply_container_update_to_gui()

    def pars_html(self, root):
        self.fix_html(root)
        for child in root:
            self.pars_html(child)

    def fix_html(self, element):
        # fix momayez with /
        if element.text is not None:
            element.text = re.sub(r"([۰-۹]+)/([۰-۹]+)", r"\2/\1", element.text)
        if element.tail is not None:
            element.tail = re.sub(r"([۰-۹]+)/([۰-۹]+)", r"\2/\1", element.tail)

        # fix date
        if element.text is not None:
            element.text = re.sub(r"([۰-۹]+)/([۰-۹]+)/([۰-۹]+)", r"\3/\1/\2", element.text)
        if element.tail is not None:
            element.tail = re.sub(r"([۰-۹]+)/([۰-۹]+)/([۰-۹]+)", r"\3/\1/\2", element.tail)


######################################################################################################
###################################### Copy Nim Fasele ###############################################
######################################################################################################
class CopyNimFasele(Tool):
    name = 'CopyNimFasele'

    #: If True the user can choose to place this tool in the plugins toolbar
    allowed_in_toolbar = True

    #: If True the user can choose to place this tool in the plugins menu
    allowed_in_menu = True

    def create_action(self, for_toolbar=True):
        # Create an action, this will be added to the plugins toolbar and
        # the plugins menu
        ac = QAction(get_icons('images/space.png'), _('کپی کردن نیم فاصله'), self.gui)
        if not for_toolbar:
            # Register a keyboard shortcut for this toolbar action. We only
            # register it for the action created for the menu, not the toolbar,
            # to avoid a double trigger
            self.register_shortcut(ac, 'css-cms-to-ems', default_keys=('Shift+Space',))
        ac.triggered.connect(self.copy_to_clipboard)
        return ac

    def copy_to_clipboard(self):
        cb = QApplication.clipboard()
        cb.clear()
        cb.setText('‌')


######################################################################################################
#######################################  Fix Images to Center of <p>  ################################
######################################################################################################
class ImagesCentralizer(Tool):
    #: Set this to a unique name it will be used as a key
    name = 'ImagesCentralizer'

    #: If True the user can choose to place this tool in the plugins toolbar
    allowed_in_toolbar = True

    #: If True the user can choose to place this tool in the plugins menu
    allowed_in_menu = True

    def create_action(self, for_toolbar=True):
        # Create an action, this will be added to the plugins toolbar and
        # the plugins menu
        ac = QAction(get_icons('images/center_images.png'), 'وسط چین کردن عکس ها', self.gui)
        if not for_toolbar:
            # Register a keyboard shortcut for this toolbar action. We only
            # register it for the action created for the menu, not the toolbar,
            # to avoid a double trigger
            self.register_shortcut(ac, 'images-centralizer', default_keys=('Ctrl+Shift+W',))
        ac.triggered.connect(self.images_centraler)
        return ac

    def get_specific_parent(self, element, tags):
        if element is None:
            return None

        parent = element.getparent()
        if parent is not None:
            for tag in tags:
                if parent.tag.lower().endswith('}' + tag):
                    return parent

        return self.get_specific_parent(parent, tags)

    def images_centraler(self):
        try:
            self.boss.commit_all_editors_to_container()
            self.boss.add_savepoint('Before: ImagesCentral')
            container = self.current_container  # The book being edited as a container object

            for name, media_type in container.mime_map.iteritems():
                if media_type in OEB_DOCS:
                    # The prefix // means search at any level of the document.
                    for img in XPath('//h:img')(container.parsed(name)):
                        p = self.get_specific_parent(img, ['p', 'div', 'ul', 'li', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6'])
                        if p is not None:
                            p.attrib['style'] = \
                                '' if 'style' not in map(lambda x: x.lower(), p.keys()) else p.attrib['style']
                            if re.search('text-align:[\ \w]*[;]?', p.attrib['style'], re.IGNORECASE):
                                # if exist this style, so replace it by center type
                                p.attrib['style'] = re.sub('text-align:[\ \w]*[;]?',
                                                           'text-align:center;',
                                                           p.attrib['style'], flags=re.I)
                            else:
                                p.attrib['style'] += 'text-align:center;'
                            container.dirty(name)
        except Exception as e:
            QMessageBox.information(self.gui, "main Err", "error({0}): {1}".format(type(e), e.args))
        else:
            # Show the user what changes we have made, allowing her to
            # revert them if necessary
            self.boss.show_current_diff()
            #
            # Update the editor UI to take into account all the changes we have made
            self.boss.apply_container_update_to_gui()



######################################################################################################
###################################### see Last Changes ##############################################
######################################################################################################
# class seeLastChanges(Tool):
#     name = 'seeLastChanges'
#
#     #: If True the user can choose to place this tool in the plugins toolbar
#     allowed_in_toolbar = True
#
#     #: If True the user can choose to place this tool in the plugins menu
#     allowed_in_menu = True
#
#     def create_action(self, for_toolbar=True):
#         # Create an action, this will be added to the plugins toolbar and
#         # the plugins menu
#         ac = QAction(get_icons('images/space.png'), 'مشاهده آخرین تغییرات ذخیره نشده', self.gui)
#         if not for_toolbar:
#             # Register a keyboard shortcut for this toolbar action. We only
#             # register it for the action created for the menu, not the toolbar,
#             # to avoid a double trigger
#             self.register_shortcut(ac, 'css-cms-to-ems', default_keys=('Shift+Space',))
#         ac.triggered.connect(self.see_last_changes)
#         return ac
#
#     def see_last_changes(self):
#         # Show the user what changes we have made, allowing her to
#         # revert them if necessary
#         self.boss.show_current_diff()
#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Copyright 2010 Asidev s.r.l.

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

import ConfigParser
import logging
import StringIO

from aybu.core.utils.exceptions import ValidationError, ConstraintError
from . test_base import BaseTests

from aybu.controlpanel.libs.controllers.node import move, delete
from aybu.controlpanel.libs.controllers.node import _sanitize_menu
from aybu.controlpanel.libs.controllers.node import _create_structure
from aybu.controlpanel.libs.controllers.node import _get_item_info
from aybu.core.models import Menu, Page, Section, ExternalLink
from aybu.core.models import Setting, SettingType, PageInfo, MenuInfo
from aybu.core.models import InternalLink, Language
from aybu.core.models import default_data_from_config
from aybu.core.models import populate

from sqlalchemy.sql import func

log = logging.getLogger(__name__)


class NodeControllersTests(BaseTests):

    """
    def test_index(self):
        raise NotImplementedError()

    def test_create(self):
        raise NotImplementedError()

    def test_update(self):
        raise NotImplementedError()

    def test_search(self):
        raise NotImplementedError()
    """

    def test_sanitize_menu(self):

        menu_1 = Menu(id=1, parent=None, weight=1)
        self.session.add(menu_1)

        max_menus = Setting(name=u'max_menus',
                            value=u'-1',
                            ui_administrable=False,
                            type=SettingType(name=u'integer', raw_type=u'int'))
        self.session.add(max_menus)

        # Testing negative value for max_menus
        menus = _sanitize_menu(self.session)
        self.assertIn(menu_1, menus)

        # Testing not integer value for max_menus
# FIXME: this test is not needed anymore, remove the
# function from node controller.
#        self.session.query(Setting).update(dict(value='test'))
#        menus = _sanitize_menu(self.session)
#        self.assertIn(menu_1, menus)

        # Creating second menu with children and testing if sanitize
        # correctly move the children from second menu to first one
        menu_2 = Menu(id=2, parent=None, weight=2)
        self.session.add(menu_2)

        page_1 = Page(id=3, parent=menu_2, weight=1)
        self.session.add(page_1)

        page_2 = Page(id=4, parent=menu_2, weight=2)
        self.session.add(page_2)

        menus = _sanitize_menu(self.session)
        self.assertIn(menu_1, menus)
        self.assertNotIn(menu_2, menus)
        menu_1_children = menu_1.children
        self.assertIn(page_1, menu_1_children)
        self.assertIn(page_2, menu_1_children)

        # Creating second menu with children and testing if sanitize
        # correctly move the children from second menu to first one
        max_menus.value = 3
        menus = _sanitize_menu(self.session)
        menu_2 = self.session.query(Menu).filter(Menu.weight == 2).one()
        menu_3 = self.session.query(Menu).filter(Menu.weight == 3).one()
        self.assertIn(menu_1, menus)
        self.assertIn(menu_2, menus)
        self.assertIn(menu_3, menus)

    def test_create_structure(self):
        max_menus = Setting(name=u'max_menus',
                            value=u'1',
                            ui_administrable=False,
                            type=SettingType(name=u'integer', raw_type=u'int'))
        self.session.add(max_menus)
        it = Language(lang=u'it', country=u'it')
        self.session.add(it)
        en = Language(lang=u'en', country=u'gb')
        self.session.add(en)
        menu_1 = Menu(id=1, parent=None, weight=1)
        self.session.add(menu_1)
        menu_info_1 = MenuInfo(label=u'Menu Principale', node=menu_1, lang=it)
        self.session.add(menu_info_1)

        expected_dict = dict(id=1, url=u'it', button_label=u'Menu Principale',
                             title='---', iconCls='folder', type='Menu',
                             enabled=True, hidden=False, checked=False,
                             children=[], expanded=False, home=False,
                             leaf=True, allowChildren=True)
        menu_dict = _create_structure(self.session, it)
        self.assertDictEqual(expected_dict, menu_dict[0])

    def test_get_item_info(self):
        file_ = StringIO.StringIO(
"""
[app:aybu-website]
default_data = data/default_data.json
""")
        config = ConfigParser.ConfigParser()
        config.readfp(file_)
        data = default_data_from_config(config)

        populate(self.config, data)

        it = self.session.query(Language).filter(Language.lang == u'it').one()

        home = Page.get_homepage(self.session)
        home_info = PageInfo.get_homepage(self.session, it)

        expected_dict = dict(id=home.id, url=home_info.url_part,
                             home=home.home, button_label=home_info.label,
                             title=home_info.title, type=home.type,
                             iconCls=home.type, enabled=home.enabled,
                             hidden=home.hidden, checked=False,
                             allowChildren=True, expanded=False, leaf=True,
                             children=[])

        home_dict = _get_item_info(self.session, home, it)
        self.assertDictEqual(expected_dict, home_dict)

        section = self.session.query(Section).order_by(func.random()).first()
        section_info = section.get_translation(self.session, it)
        expected_dict = dict(id=section.id, url=section_info.url_part,
                             home=False, button_label=section_info.label,
                             title=section_info.title, type=section.type,
                             iconCls=section.type, enabled=section.enabled,
                             hidden=section.hidden, checked=False,
                             allowChildren=True, expanded=False, leaf=True,
                             children=[])
        if section.children:
            expected_dict['leaf'] = False
            expected_dict['expanded'] = True
        section_dict = _get_item_info(self.session, section, it)
        self.assertDictEqual(expected_dict, section_dict)

        external_link = self.session.query(ExternalLink).\
                             order_by(func.random()).first()
        external_link_info = external_link.get_translation(self.session, it)
        expected_dict = dict(id=external_link.id,
                             url=external_link_info.ext_url,
                             home=False, button_label=external_link_info.label,
                             title='---', children=[],
                             type=external_link.type,
                             iconCls=external_link.type,
                             enabled=external_link.enabled,
                             hidden=external_link.hidden, checked=False,
                             allowChildren=False, expanded=False, leaf=True)
        external_link_dict = _get_item_info(self.session, external_link, it)
        self.assertDictEqual(expected_dict, external_link_dict)

        internal_link = self.session.query(InternalLink).\
                             order_by(func.random()).first()
        internal_link_info = internal_link.get_translation(self.session, it)
        internal_link_url = internal_link.linked_to.\
                                          get_translation(self.session, it).url
        expected_dict = dict(id=internal_link.id, url=internal_link_url,
                             home=False, button_label=internal_link_info.label,
                             title='---', children=[],
                             type=internal_link.type,
                             iconCls=internal_link.type,
                             enabled=internal_link.enabled,
                             hidden=internal_link.hidden, checked=False,
                             allowChildren=False, expanded=False, leaf=True)
        internal_link_dict = _get_item_info(self.session, internal_link, it)
        self.assertDictEqual(expected_dict, internal_link_dict)

        menu_2 = Menu(parent=None, weight=2)
        self.session.add(menu_2)
        menu_info_2 = MenuInfo(label=u'Menu 2', node=menu_2, lang=it)
        self.session.add(menu_info_2)

        page_1 = Page(parent=menu_2, weight=1)
        self.session.add(page_1)
        page_info_1 = PageInfo(label='Test', title='Pagina Test',
                               url_part='pagina_test',
                               url='/it/pagina_test.html', node=page_1,
                               lang=it)
        self.session.add(page_info_1)
        self.session.flush()

        menu_dict = dict(id=menu_2.id, url=u'it', button_label=u'Menu 2',
                         title='---', iconCls='folder', type='Menu',
                         enabled=True, hidden=False, checked=False,
                         children=[], expanded=True, home=False,
                         leaf=False, allowChildren=True)

        page_dict = dict(id=page_1.id, url=page_info_1.url_part,
                         home=page_1.home, button_label=page_info_1.label,
                         title=page_info_1.title, type=page_1.type,
                         iconCls=page_1.type, enabled=page_1.enabled,
                         hidden=page_1.hidden, checked=False,
                         allowChildren=True, expanded=False, leaf=True,
                         children=[])
        menu_dict['children'].append(page_dict)
        result_dict = _get_item_info(self.session, menu_2, it, recurse=True)
        self.assertDictEqual(menu_dict, result_dict)


    def test_delete(self):
        #it = Language(lang=u'it', country=u'it')
        #en = Language(lang=u'en', country=u'gb')

        menu = Menu(id=1, parent=None, weight=1)

        page = Page(id=2, parent=menu, weight=1)
        """
        page_it = NodeInfo(label=u'Home', title=u'Home', url_part=u'index',
                           url=u'/it/index.html', node=page, lang=it)
        page_en = NodeInfo(label=u'Home', title=u'Home', url_part=u'index',
                           url=u'/en/index.html', node=page, lang=en)
        """

        section = Section(id=3, parent=menu, weight=2)
        """
        section_it = NodeInfo(label=u'Azienda', title=u'Azienda',
                              url_part=u'azienda', url=u'', node=section,
                              lang=it)
        section_en = NodeInfo(label=u'Company', title=u'Company',
                              url_part=u'company', url=u'', node=section,
                              lang=en)
        """

        external_link = ExternalLink(id=4, parent=menu, weight=3)
        """
        external_link_it = NodeInfo(label=u'Sviluppatore',
                                    title=u'Sviluppatore', url_part=u'',
                                    url=u'', node=external_link, lang=it)
        external_link_en = NodeInfo(label=u'Developer', title=u'Developer',
                                    url_part=u'', url=u'', node=external_link,
                                    lang=en)
        """

        internal_link = InternalLink(id=5, parent=menu, weight=4)
        """
        internal_link_it = NodeInfo(label=u'Sviluppatore',
                                    title=u'Sviluppatore', url_part=u'',
                                    url=u'', node=internal_link, lang=it)
        internal_link_en = NodeInfo(label=u'Developer', title=u'Developer',
                                    url_part=u'', url=u'', node=internal_link,
                                    lang=en)
        """

        child_page = Page(id=6, parent=page, weight=1)
        child_section = Section(id=7, parent=page, weight=2)

        second_menu = Menu(id=8, parent=None, weight=2)
        another_page = Page(id=9, parent=second_menu, weight=1)
        another_section = Section(id=10, parent=second_menu, weight=2)

        #contact_page = Page(id=11, parent=menu, weight=1)

        """
        - menu(1)
            - page(2)
                - child_page(6)
                - child_section(7)
            - section(3)
            - external_link(4)
            - internal_link(5)
        - second_menu(8)
            - another_page(9)
            - another_section(10)
        """

        for obj in (menu, page, section, external_link, internal_link,
                    child_page, child_section, second_menu, another_page,
                    another_section):
            self.session.add(obj)

        self.session.commit()

        self.assertEqual(page, Page.get_homepage(self.session))

        # Trying to delete page(2)
        delete(self.session, 2)
        # After this the new structure should be
        """
        - menu(1)
            - child_page(6)
            - child_section(7)
            - section(3)
            - external_link(4)
            - internal_link(5)
        - second_menu(8)
            - another_page(9)
            - another_section(10)
        """
        # To test it I have to check:
        # - child_page(6) has weight 1
        # - child_page(6) has parent menu(1)
        # - child_section(7) has weight 2
        # - child_section(7) has parent menu(1)
        # - section(3) has weight 3
        # - external_link(4) has weight 4
        # - internal_link(5) has weight 5
        self.assertEqual(1, child_page.weight)
        self.assertEqual(menu, child_page.parent)
        self.assertEqual(2, child_section.weight)
        self.assertEqual(menu, child_section.parent)
        self.assertEqual(3, section.weight)
        self.assertEqual(4, external_link.weight)
        self.assertEqual(5, internal_link.weight)
        # Checking the homepage is now child_page(6)
        self.assertEqual(child_page, Page.get_homepage(self.session))

        # Trying to delete section(3)
        delete(self.session, 3)
        # After this the structure is
        """
        - menu(1)
            - child_page(6)
            - child_section(7)
            - external_link(4)
            - internal_link(5)
        - second_menu(8)
            - another_page(9)
            - another_section(10)
        """
        # To test it I have to check:
        # - child_page(6) has weight 1
        # - child_section(7) has weight 2
        # - external_link(4) has weight 3
        # - internal_link(5) has weight 4
        self.assertEqual(1, child_page.weight)
        self.assertEqual(2, child_section.weight)
        self.assertEqual(3, external_link.weight)
        self.assertEqual(4, internal_link.weight)

        # Trying to delete child_page(6)
        delete(self.session, 6)
        # After this the structure is
        """
        - menu(1)
            - child_section(7)
            - external_link(4)
            - internal_link(5)
        - second_menu(8)
            - another_page(9)
            - another_section(10)
        """
        # To test it I have to check:
        # - child_section(7)
        # - external_link(4)
        # - internal_link(5)
        self.assertEqual(1, child_section.weight)
        self.assertEqual(2, external_link.weight)
        self.assertEqual(3, internal_link.weight)
        # Checking the homepage is now another_page(9)
        self.assertEqual(another_page, Page.get_homepage(self.session))

        # Trying to delete internal_link(5)
        delete(self.session, 5)
        # After this the structure is
        """
        - menu(1)
            - child_section(7)
            - external_link(4)
        - second_menu(8)
            - another_page(9)
            - another_section(10)
        """
        # To test it I have to check:
        # - child_section(7)
        # - external_link(4)
        self.assertEqual(1, child_section.weight)
        self.assertEqual(2, external_link.weight)

        # Trying to delete menu(1). This operation should not be allowed
        with self.assertRaises(ValidationError):
            delete(self.session, 1)

        # Trying to delete second_menu(8). This operation should not be allowed
        with self.assertRaises(ValidationError):
            delete(self.session, 8)

        # Trying to delete the last page.  This operation should not be allowed
        with self.assertRaises(ConstraintError):
            delete(self.session, 9)

    def test_move(self):
        #it = Language(lang=u'it', country=u'it')
        #en = Language(lang=u'en', country=u'gb')

        menu = Menu(id=1, parent=None, weight=1)

        page = Page(id=2, parent=menu, weight=1)
        """
        page_it = NodeInfo(label=u'Home', title=u'Home', url_part=u'index',
                           url=u'/it/index.html', node=page, lang=it)
        page_en = NodeInfo(label=u'Home', title=u'Home', url_part=u'index',
                           url=u'/en/index.html', node=page, lang=en)
        """

        section = Section(id=3, parent=menu, weight=2)
        """
        section_it = NodeInfo(label=u'Azienda', title=u'Azienda',
                              url_part=u'azienda', url=u'', node=section,
                              lang=it)
        section_en = NodeInfo(label=u'Company', title=u'Company',
                              url_part=u'company', url=u'', node=section,
                              lang=en)
        """

        external_link = ExternalLink(id=4, parent=menu, weight=3)
        """
        external_link_it = NodeInfo(label=u'Sviluppatore',
                                    title=u'Sviluppatore', url_part=u'',
                                    url=u'', node=external_link, lang=it)
        external_link_en = NodeInfo(label=u'Developer', title=u'Developer',
                                    url_part=u'', url=u'', node=external_link,
                                    lang=en)
        """

        internal_link = InternalLink(id=5, parent=menu, weight=4)
        """
        internal_link_it = NodeInfo(label=u'Sviluppatore',
                                    title=u'Sviluppatore', url_part=u'',
                                    url=u'', node=internal_link, lang=it)
        internal_link_en = NodeInfo(label=u'Developer', title=u'Developer',
                                    url_part=u'', url=u'', node=internal_link,
                                    lang=en)
        """

        child_page = Page(id=6, parent=page, weight=1)
        child_section = Section(id=7, parent=page, weight=2)

        second_menu = Menu(id=8, parent=None, weight=2)
        another_page = Page(id=9, parent=second_menu, weight=1)
        another_section = Section(id=10, parent=second_menu, weight=2)

        #contact_page = Page(id=11, parent=menu, weight=1)

        """
        - menu(1)
            - page(2)
                - child_page(6)
                - child_section(7)
            - section(3)
            - external_link(4)
            - internal_link(5)
        - second_menu(8)
            - another_page(9)
            - another_section(10)
        """

        for obj in (menu, page, section, external_link, internal_link,
                    child_page, child_section, second_menu, another_page,
                    another_section):
            self.session.add(obj)

        self.session.commit()

        # Trying to move page(9) as child of page(2) after child_page(6)
        move(self.session, 9, 2, 6)
        # After this the new structure should be
        """
        - menu(1)
            - page(2)
                - child_page(6)
                - another_page(9)
                - child_section(7)
            - section(3)
            - external_link(4)
            - internal_link(5)
        - second_menu(8)
            - another_section(10)
        """
        # To test it I have to check:
        # - another_page(9) has weight 2
        # - child_section(7) has weight 3
        # - another_section(10) has weight 1
        self.assertEqual(2, another_page.weight)
        self.assertEqual(3, child_section.weight)
        self.assertEqual(1, another_section.weight)

        # Moving back another_page (9) to test move with no previous_node_id
        move(self.session, 9, 8, None)
        # After this the structure is newly
        """
        - menu(1)
            - page(2)
                - child_page(6)
                - child_section(7)
            - section(3)
            - external_link(4)
            - internal_link(5)
        - second_menu(8)
            - another_page(9)
            - another_section(10)
        """
        # To test it I have to check:
        # - another_page(9) has weight 1
        # - child_section(7) has weight 2
        # - another_section(10) has weight 2
        self.assertEqual(1, another_page.weight)
        self.assertEqual(2, child_section.weight)
        self.assertEqual(2, another_section.weight)

        # Moving external_link(4) as last child of page(2).
        move(self.session, 4, 2, 7)
        # After this the structure is newly
        """
        - menu(1)
            - page(2)
                - child_page(6)
                - child_section(7)
                - external_link(4)
            - section(3)
            - internal_link(5)
        - second_menu(8)
            - another_page(9)
            - another_section(10)
        """
        # To test it I have to check:
        # - external_link(4) has weight 3
        # - internal_link(5) has weight 3
        self.assertEqual(3, external_link.weight)
        self.assertEqual(3, internal_link.weight)

        # Testing move without really change the position to the node.
        # This should debug the control when the nove is not really moved
        # Moving child_section(7) without really move it
        move(self.session, 7, 2, 6)
        # The Tree is the same
        # To test it I have to check:
        # - child_page(6) has weight 1
        # - child_section(7) has weight 2
        # - external_link(4) has weight 3
        self.assertEqual(1, child_page.weight)
        self.assertEqual(2, child_section.weight)
        self.assertEqual(3, external_link.weight)

        # Moving child_section(7) as only child of section(3)
        # This test again move with no previous_node_id
        move(self.session, 7, 3, None)
        # After this the structure should be
        """
        - menu(1)
            - page(2)
                - child_page(6)
                - external_link(4)
            - section(3)
                - child_section(7)
            - internal_link(5)
        - second_menu(8)
            - another_page(9)
            - another_section(10)
        """
        # To test it I hev to check:
        # - child_page(6) has weight 1
        # - external_link(4) has weight 2
        # - child_section(7) has weight 1
        self.assertEqual(1, child_page.weight)
        self.assertEqual(2, external_link.weight)
        self.assertEqual(1, child_section.weight)

        # Checking the function does not allow to move a Menu
        with self.assertRaises(ValidationError):
            move(self.session, 1, 8, None)

        # Checking the model garantuee the contraint trying to move nodes
        # as children of internal_link or external_link
        with self.assertRaises(ValidationError):
            move(self.session, 7, 5, None)

        with self.assertRaises(ValidationError):
            move(self.session, 7, 4, None)

        # Testing all None as argument
        with self.assertRaises(Exception):
            move(self.session, None, None, None)

        # Testing a node cannot be moved with no parent
        with self.assertRaises(Exception):
            move(self.session, 2, None, None)

        # Testing a node cannot be moved as child of a node that does not exist
        with self.assertRaises(Exception):
            move(self.session, None, 54, None)

        # Testing some other None combination
        with self.assertRaises(Exception):
            move(self.session, None, None, 2)

        # Testing a node that not exists cannot be moved
        # as child of a node that does not exist
        with self.assertRaises(Exception):
            move(self.session, 33, 54, None)

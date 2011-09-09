
from pyramid import testing
import logging
try:
    import unittest2 as unittest
except:
    import unittest

from aybu.core.utils.exceptions import ValidationError
from aybu.core.tests.test_models.test_base import BaseTests

from aybu.controlpanel.libs.controllers.node import move
from aybu.controlpanel.models import Node, Menu, Page, Section, ExternalLink
from aybu.controlpanel.models import InternalLink, NodeInfo, Language

log = logging.getLogger(__name__)


class NodeControllersTests(BaseTests):

    """
    def test_index(self):
        raise NotImplementedError()

    def test_create(self):
        raise NotImplementedError()

    def test_update(self):
        raise NotImplementedError()

    def test_delete(self):
        raise NotImplementedError()

    def test_search(self):
        raise NotImplementedError()
    """

    def test_move(self):
        it = Language(lang=u'it', country=u'it')
        en = Language(lang=u'en', country=u'gb')

        menu = Menu(id=1, parent=None, weight=1)

        page = Page(id=2, parent=menu, weight=1)
        page_it = NodeInfo(label=u'Home', title=u'Home', url_part=u'index',
                           url=u'/it/index.html', node=page, lang=it)
        page_en = NodeInfo(label=u'Home', title=u'Home', url_part=u'index',
                           url=u'/en/index.html', node=page, lang=en)

        section = Section(id=3, parent=menu, weight=2)
        section_it = NodeInfo(label=u'Azienda', title=u'Azienda',
                              url_part=u'azienda', url=u'', node=section, lang=it)
        section_en = NodeInfo(label=u'Company', title=u'Company',
                              url_part=u'company', url=u'', node=section, lang=en)

        external_link = ExternalLink(id=4, parent=menu, weight=3)
        external_link_it = NodeInfo(label=u'Sviluppatore',
                                    title=u'Sviluppatore', url_part=u'',
                                    url=u'', node=external_link, lang=it)
        external_link_en = NodeInfo(label=u'Developer', title=u'Developer',
                                    url_part=u'', url=u'', node=external_link,
                                    lang=en)

        internal_link = InternalLink(id=5, parent=menu, weight=4)
        internal_link_it = NodeInfo(label=u'Sviluppatore',
                                    title=u'Sviluppatore', url_part=u'',
                                    url=u'', node=internal_link, lang=it)
        internal_link_en = NodeInfo(label=u'Developer', title=u'Developer',
                                    url_part=u'', url=u'', node=internal_link,
                                    lang=en)

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











from pyramid import testing
import logging
try:
    import unittest2 as unittest
except:
    import unittest

from aybu.core.tests.test_models.test_base import BaseTests
from aybu.controlpanel.models import Menu, Page, Section, ExternalLink
from aybu.controlpanel.models import InternalLink

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
        menu = Menu(id=1, parent=None, weight=1)
        page = Page(id=2, parent=menu, weight=1)
        section = Section(id=3, parent=menu, weight=2)
        external_link = ExternalLink(id=4, parent=menu, weight=3)
        internal_link = InternalLink(id=5, parent=menu, weight=4)

        child_page = Page(id=6, parent=page, weight=1)
        child_section = Section(id=7, parent=page, weight=2)

        second_menu = Menu(id=8, parent=None, weight=2)
        another_page = Page(id=9, parent=second_menu, weight=1)
        another_section = Section(id=10, parent=second_menu, weight=2)

        """
        - menu
            - page
                - child_page
                - child_section
            - section
            - external_link
            - internal_link

        - second_menu
            - another_page
            - another_section
        """

        for obj in (menu, page, section, external_link, internal_link,
                    child_page, child_section, second_menu, another_page,
                    another_section):
            self.session.add(obj)

        self.session.commit()

# -*- coding: utf-8 -*-
"""Setup tests for this package."""
from theming.toolkit.portlets.testing import THEMING_TOOLKIT_PORTLETS_INTEGRATION_TESTING  # noqa
from plone import api

import unittest2 as unittest


class TestSetup(unittest.TestCase):
    """Test that theming.toolkit.portlets is properly installed."""

    layer = THEMING_TOOLKIT_PORTLETS_INTEGRATION_TESTING

    def setUp(self):
        """Custom shared utility setup for tests."""
        self.portal = self.layer['portal']
        self.installer = api.portal.get_tool('portal_quickinstaller')

    def test_product_installed(self):
        """Test if theming.toolkit.portlets is installed with portal_quickinstaller."""
        self.assertTrue(self.installer.isProductInstalled('theming.toolkit.portlets'))

    def test_uninstall(self):
        """Test if theming.toolkit.portlets is cleanly uninstalled."""
        self.installer.uninstallProducts(['theming.toolkit.portlets'])
        self.assertFalse(self.installer.isProductInstalled('theming.toolkit.portlets'))

    def test_browserlayer(self):
        """Test that IThemingToolkitPortletsLayer is registered."""
        from theming.toolkit.portlets.interfaces import IThemingToolkitPortletsLayer
        from plone.browserlayer import utils
        self.assertIn(IThemingToolkitPortletsLayer, utils.registered_layers())

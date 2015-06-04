# -*- coding: utf-8 -*-
from plone.app.robotframework.testing import REMOTE_LIBRARY_BUNDLE_FIXTURE
from plone.app.testing import applyProfile
from plone.app.testing import FunctionalTesting
from plone.app.testing import IntegrationTesting
from plone.app.testing import PLONE_FIXTURE
from plone.app.testing import PloneSandboxLayer
from plone.testing import z2
from zope.configuration import xmlconfig

import theming.toolkit.portlets


class ThemingToolkitPortletsLayer(PloneSandboxLayer):

    defaultBases = (PLONE_FIXTURE,)

    def setUpZope(self, app, configurationContext):
        xmlconfig.file(
            'configure.zcml',
            theming.toolkit.portlets,
            context=configurationContext
        )

    def setUpPloneSite(self, portal):
        applyProfile(portal, 'theming.toolkit.portlets:default')


THEMING_TOOLKIT_PORTLETS_FIXTURE = ThemingToolkitPortletsLayer()


THEMING_TOOLKIT_PORTLETS_INTEGRATION_TESTING = IntegrationTesting(
    bases=(THEMING_TOOLKIT_PORTLETS_FIXTURE,),
    name='ThemingToolkitPortletsLayer:IntegrationTesting'
)


THEMING_TOOLKIT_PORTLETS_FUNCTIONAL_TESTING = FunctionalTesting(
    bases=(THEMING_TOOLKIT_PORTLETS_FIXTURE,),
    name='ThemingToolkitPortletsLayer:FunctionalTesting'
)


THEMING_TOOLKIT_PORTLETS_ACCEPTANCE_TESTING = FunctionalTesting(
    bases=(
        THEMING_TOOLKIT_PORTLETS_FIXTURE,
        REMOTE_LIBRARY_BUNDLE_FIXTURE,
        z2.ZSERVER_FIXTURE
    ),
    name='ThemingToolkitPortletsLayer:AcceptanceTesting'
)

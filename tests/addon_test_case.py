# SPDX-License-Identifier: MIT OR GPL-3.0-or-later
from unittest import TestCase

import bpy

TEST_MODULE = "io_scene_vrm"
INSTALLED_MODULE = "vrm"


class AddonTestCase(TestCase):
    installed_module_disabled: bool = False

    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()

        if any(
            addon.module == INSTALLED_MODULE for addon in bpy.context.preferences.addons
        ):
            bpy.ops.preferences.addon_disable(module=INSTALLED_MODULE)
            cls.installed_module_disabled = True

        bpy.ops.preferences.addon_enable(module=TEST_MODULE)

    def setUp(self) -> None:
        super().setUp()
        bpy.ops.wm.read_homefile(use_empty=True)

    @classmethod
    def tearDownClass(cls) -> None:
        super().tearDownClass()

        bpy.ops.preferences.addon_disable(module=TEST_MODULE)

        if cls.installed_module_disabled:
            bpy.ops.preferences.addon_enable(module=INSTALLED_MODULE)
            cls.installed_module_disabled = False

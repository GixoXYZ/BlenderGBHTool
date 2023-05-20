# SPDX-License-Identifier: GPL-2.0-or-later

from bpy.types import Panel

from .. constants import GBH_PACKAGE
from . common_ui import GBHBasePanel
from . import rig_ui_modules as modules


class VIEW3D_PT_rig_ui_main(Panel, GBHBasePanel):
    bl_label = "Rigging"
    bl_idname = "VIEW3D_PT_rig_ui_main"
    bl_options = {"DEFAULT_CLOSED"}

    @classmethod
    def poll(cls, context):
        wm = context.window_manager
        gbh_panels = wm.gbh_panels
        pref = context.preferences.addons[GBH_PACKAGE].preferences
        return pref.panel_rig_switch and gbh_panels.panel_rig_switch

    def draw_header(self, context):
        self.layout.label(text="", icon="GROUP_BONE")

    def draw(self, context):
        layout = self.layout
        modules.rig_armature_creation(layout, context)


classes = (
    VIEW3D_PT_rig_ui_main,
)


def register():
    from bpy.utils import register_class
    for cls in classes:
        register_class(cls)


def unregister():
    from bpy.utils import unregister_class
    for cls in reversed(classes):
        unregister_class(cls)

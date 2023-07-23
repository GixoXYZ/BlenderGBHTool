# SPDX-License-Identifier: GPL-2.0-or-later

from bpy.types import Panel

from ..global_variables import GBH_PACKAGE
from . common_ui import GBHBasePanel
from . import update_ui_modules as modules


class VIEW3D_PT_update_ui_main(Panel, GBHBasePanel):
    bl_label = "Update"
    bl_idname = "VIEW3D_PT_update_ui_main"

    @classmethod
    def poll(cls, context):
        wm = context.window_manager
        gbh_panels = wm.gbh_panels
        pref = context.preferences.addons[GBH_PACKAGE].preferences
        return pref.update_available and pref.panel_update_switch and gbh_panels.panel_update_switch

    def draw_header(self, context):
        self.layout.label(text="", icon="FILE_REFRESH")

    def draw(self, context):
        layout = self.layout
        modules.update_version_info(context, layout)
        modules.update_message(context, layout)
        modules.update_changelog(context, layout)
        modules.update_download(context, layout)


classes = (
    VIEW3D_PT_update_ui_main,
)


def register():
    from bpy.utils import register_class
    for cls in classes:
        register_class(cls)


def unregister():
    from bpy.utils import unregister_class
    for cls in reversed(classes):
        unregister_class(cls)

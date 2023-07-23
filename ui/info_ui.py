# SPDX-License-Identifier: GPL-2.0-or-later

from bpy.types import Panel

from . common_ui import GBHBasePanel
from .. import global_variables as gv
from . import info_ui_modules as modules


class VIEW3D_PT_info_ui_main(Panel, GBHBasePanel):
    bl_label = "Info"
    bl_idname = "VIEW3D_PT_info_ui_main"
    bl_options = {"DEFAULT_CLOSED"}

    @classmethod
    def poll(cls, context):
        wm = context.window_manager
        gbh_panels = wm.gbh_panels
        pref = context.preferences.addons[gv.GBH_PACKAGE].preferences
        return pref.panel_info_switch and gbh_panels.panel_info_switch

    def draw_header(self, context):
        self.layout.label(text="", icon="INFO")

    def draw(self, context):
        layout = self.layout

        box = layout.box()
        col = box.column()
        # col.operator("gbh.testing")
        col.label(text="Links")

        links = {
            "Docs": {"url": gv.URL_DOCS, "icon": "Docs"},
            "Contact": {"url": gv.URL_CONTACT, "icon": "Contact"},
            "Gumroad": {"url": gv.URL_GUMROAD, "icon": "Gumroad"},
            "Github": {"url": gv.URL_GITHUB, "icon": "Github"},
            "Report Problems": {"url": gv.URL_ISSUE, "icon": "Issue"},
        }

        for key, button_data in links.items():
            modules.info_button(context, col, key,
                                button_data["icon"], button_data["url"])

        box = layout.box()
        col = box.column()
        col.label(text="Common Pitfalls")
        modules.info_pitfalls(col, context)


classes = (
    VIEW3D_PT_info_ui_main,
)


def register():
    from bpy.utils import register_class
    for cls in classes:
        register_class(cls)


def unregister():
    from bpy.utils import unregister_class
    for cls in reversed(classes):
        unregister_class(cls)

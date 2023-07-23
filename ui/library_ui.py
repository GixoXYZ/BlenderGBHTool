# SPDX-License-Identifier: GPL-2.0-or-later

import bpy
from bpy.types import Panel

from ..global_variables import GBH_PACKAGE
from . common_ui import GBHBasePanel
from . import library_ui_modules as modules


class VIEW3D_PT_library_ui_main(Panel, GBHBasePanel):
    bl_label = "Library"
    bl_idname = "VIEW3D_PT_library_ui_main"
    bl_options = {"DEFAULT_CLOSED"}

    @classmethod
    def poll(cls, context):
        wm = context.window_manager
        gbh_panels = wm.gbh_panels
        pref = context.preferences.addons[GBH_PACKAGE].preferences
        return pref.panel_lib_switch and gbh_panels.panel_lib_switch

    def draw_header(self, context):
        self.layout.label(text="", icon="ASSET_MANAGER")

    def draw(self, context):
        layout = self.layout
        pref = context.preferences.addons[GBH_PACKAGE].preferences
        wm = context.window_manager
        gbh_lib = wm.gbh_lib

        box = layout
        col = box.column()
        header = col.box()
        modules.lib_settings_header(context, header)

        if gbh_lib.lib_settings_switch:
            modules.lib_settings_menu(context, header)

        modules.lib_categories_and_search(col)

        col = box.column()
        modules.lib_pages(col)

        grid = col.grid_flow(even_columns=True, even_rows=True, row_major=True)

        if pref.lib_list_view:
            layout = col

        if not pref.lib_list_view:
            layout = grid

        if gbh_lib.asset_category == "NODES":
            modules.lib_nodes_grid(context, layout)
        elif gbh_lib.asset_category == "MATERIALS":
            modules.lib_materials_grid(context, layout)


classes = (
    VIEW3D_PT_library_ui_main,
)


def register():
    from bpy.utils import register_class
    for cls in classes:
        register_class(cls)


def unregister():
    from bpy.utils import unregister_class
    for cls in reversed(classes):
        unregister_class(cls)

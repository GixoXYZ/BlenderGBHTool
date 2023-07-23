# SPDX-License-Identifier: GPL-2.0-or-later

from bpy.types import Menu
import bpy
from .. import global_variables as gv


class VIEW3D_MT_PIE_gbh_panel_toggle(Menu):
    bl_label = "Screen Area Tiling"

    def draw(self, context):
        pref = bpy.context.preferences.addons[gv.GBH_PACKAGE].preferences
        layout = self.layout

        pie = layout.menu_pie()

        if pref.panel_hair_cards_switch:
            pie.operator(
                "gbh.panel_focus",
                text="Hair Card",
                icon="TEXTURE"
            ).panel_id = "panel_hair_cards_switch"

        if pref.panel_convert_switch:
            pie.operator(
                "gbh.panel_focus",
                text="Convert Hair",
                icon="UV_SYNC_SELECT"
            ).panel_id = "panel_convert_switch"

        if pref.panel_lib_switch:
            pie.operator(
                "gbh.panel_focus",
                text="Library",
                icon="ASSET_MANAGER"
            ).panel_id = "panel_lib_switch"

        if pref.panel_rig_switch:
            pie.operator(
                "gbh.panel_focus",
                text="Rigging",
                icon="GROUP_BONE"
            ).panel_id = "panel_rig_switch"

        pie.operator(
            "gbh.panel_unfocus",
            text="Show All",
            icon="LOOP_BACK"
        )


classes = (
    VIEW3D_MT_PIE_gbh_panel_toggle,
)


def register():
    from bpy.utils import register_class
    for cls in classes:
        register_class(cls)


def unregister():
    from bpy.utils import unregister_class
    for cls in reversed(classes):
        unregister_class(cls)

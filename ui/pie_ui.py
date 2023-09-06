# SPDX-License-Identifier: GPL-2.0-or-later

from bpy.types import Menu
import bpy
from .. import global_variables as gv


class VIEW3D_MT_PIE_gbh_panel_toggle(Menu):
    bl_label = "GBH Tool"

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


class VIEW3D_MT_PIE_gbh_rig(Menu):
    bl_label = "GBH Tool"

    # TODO: Test rig pie menu in different scenarios.
    def draw(self, context):
        layout = self.layout
        pie = layout.menu_pie()

        section_weights = pie.column()
        box = section_weights.box()
        box.label(text="Weights")
        col = box.column()
        col.scale_y = 1.3
        quantize = col.operator("object.vertex_group_quantize", text="Quantize for the Selection")
        levels = col.operator("object.vertex_group_levels", text="Levels for the Selection")
        smooth = col.operator("object.vertex_group_smooth", text="Smooth for the Selection")

        section_selection = pie.column()
        box = section_selection.box()
        box.label(text="Selection")
        col = box.column()
        col.scale_y = 1.3
        col.operator("gbh.select_similar_bones", text="Select Similar Bones by Name")
        col.operator("gbh.select_all_bones")

        try:
            quantize.group_select_mode = "BONE_SELECT"
            quantize.steps = 4

            levels.group_select_mode = "BONE_SELECT"
            levels.offset = 0
            levels.gain = 1

            smooth.group_select_mode = "BONE_SELECT"
            smooth.factor = 0.5
            smooth.repeat = 1
            smooth.expand = 0

        except TypeError:
            section_weights.enabled = False
            section_selection.enabled = False


classes = (
    VIEW3D_MT_PIE_gbh_panel_toggle,
    VIEW3D_MT_PIE_gbh_rig,

)


def register():
    from bpy.utils import register_class
    for cls in classes:
        register_class(cls)


def unregister():
    from bpy.utils import unregister_class
    for cls in reversed(classes):
        unregister_class(cls)

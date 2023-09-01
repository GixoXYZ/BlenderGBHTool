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

    def draw(self, context):
        scene = context.scene
        wm = context.window_manager
        gbh_rig = wm.gbh_rig
        pref = bpy.context.preferences.addons[gv.GBH_PACKAGE].preferences
        layout = self.layout

        pie = layout.menu_pie()

        # TODO Use panel UI and wp_pie properties instead.
        section_weights = pie.column()
        box = section_weights.box()
        box.label(text="Quantize")
        col = box.column()
        col.prop(
            gbh_rig,
            "wp_pie_quantize_steps",
        )
        col = box.column()
        col.scale_y = 1.3
        quantize = col.operator("object.vertex_group_quantize", text="Quantize for the Selection")

        box = section_weights.box()
        box.label(text="Levels")
        col = box.column()
        col.prop(
            gbh_rig,
            "wp_pie_levels_offset",
        )
        col.prop(
            gbh_rig,
            "wp_pie_level_gain",
        )
        col = box.column()
        col.scale_y = 1.3
        levels = col.operator("object.vertex_group_levels", text="Levels for the Selection")

        box = section_weights.box()
        box.label(text="Smooth")
        col = box.column()
        col.prop(
            gbh_rig,
            "wp_pie_smooth_factor",
        )
        col.prop(
            gbh_rig,
            "wp_pie_smooth_iterations",
        )
        col.prop(
            gbh_rig,
            "wp_pie_smooth_expand",
        )
        col = box.column()
        col.scale_y = 1.3
        smooth = col.operator("object.vertex_group_smooth", text="Smooth for the Selection")

        section_selection = pie.column()
        box = section_selection.box()
        box.label(text="Selection")
        col = box.column()
        col.scale_y = 1.3
        col.operator("gbh.select_similar_bones")
        col.operator("gbh.select_all_bones")

        try:
            quantize.group_select_mode = "BONE_SELECT"
            quantize.steps = gbh_rig.wp_pie_quantize_steps

            levels.group_select_mode = "BONE_SELECT"
            levels.offset = gbh_rig.wp_pie_levels_offset
            levels.gain = gbh_rig.wp_pie_level_gain

            smooth.group_select_mode = "BONE_SELECT"
            smooth.factor = gbh_rig.wp_pie_smooth_factor
            smooth.repeat = gbh_rig.wp_pie_smooth_iterations
            smooth.expand = gbh_rig.wp_pie_smooth_expand

        except TypeError as e:
            print(e)
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

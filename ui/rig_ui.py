# SPDX-License-Identifier: GPL-2.0-or-later

import bpy
from bpy.types import Panel

from ..global_variables import GBH_PACKAGE
from . common_ui import GBHBasePanel, box_sub_panel


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
        self._rig_armature_creation(layout, context)
        self._rig_weight_paint(layout, context)

    def _rig_armature_creation(self, layout, context):
        scene = context.scene
        wm = context.window_manager
        gbh_rig = wm.gbh_rig
        title = "Armature Creation"
        sub_panel = box_sub_panel(
            layout,
            "ARMATURE_DATA",
            title,
            gbh_rig,
            "rig_armature_creation",
            False
        )
        if sub_panel[0]:
            body = sub_panel[2]
            if not scene.hair_object:
                row = body.row()
                row.label(text="Please select a hair object.", icon="INFO")
                return

            armature_name = f"{scene.hair_object.name}_Armature"
            existing_armature = bpy.data.objects.get(armature_name)
            if not existing_armature:
                col = body.column()
                col.operator("gbh.hair_to_armature", text="Generate Armature")
                return

            box = body.box()
            col = box.column()
            col.label(text="Properties")
            col.prop(
                gbh_rig,
                "rig_res",
                text="Number of Bones in Each Chain"
            )
            col.prop(
                gbh_rig,
                "rig_density",
                text="Density of Bone Chains(%)",
                slider=True,
            )

            icon = "SORT_ASC" if gbh_rig.rig_reverse else "SORT_DESC"

            col.prop(
                gbh_rig,
                "rig_reverse",
                text="Reverse Chains Direction",
                icon=icon
            )
            col = box.column()
            col.prop(
                gbh_rig,
                "rig_add_parent_bone",
                text="Add Parent Bone",
                icon="BONE_DATA"
            )
            if gbh_rig.rig_add_parent_bone:
                col.prop(gbh_rig, "rig_parent_size")

            col = box.column(align=True)
            col.prop(gbh_rig, "rig_start", text="Chains Start Point Trim")
            col.prop(gbh_rig, "rig_end", text="Chains End Point Trim")

            box = body.box()
            col = box.column()
            icon = "RADIOBUT_ON" if gbh_rig.rig_live_preview else "RADIOBUT_OFF"
            col.prop(
                gbh_rig,
                "rig_live_preview",
                text="Live Preview",
                icon=icon
            )
            col.operator("gbh.hair_to_armature", text="Update Armature")

            box = body.box()
            col = box.column()
            icon = "MODIFIER" if gbh_rig.rig_use_mods else "MODIFIER_DATA"
            col.prop(
                gbh_rig,
                "rig_use_mods",
                text="Use Hair Object's Modifiers",
                icon=icon
            )
            col.label(
                text="Using object's modifiers could result in freezing of Blender.",
                icon="INFO"
            )

            if not gbh_rig.rig_use_mods:
                return
            if unused_mods := eval(gbh_rig.rig_not_used_mods):
                for mod in unused_mods:
                    col = box.column()
                    col.label(
                        text=f'"{mod}" node group is not being used.',
                        icon="DOT"
                    )

    def _rig_weight_paint(self, layout, context):
        scene = context.scene
        wm = context.window_manager
        gbh_rig = wm.gbh_rig
        title = "Weight Paint"
        sub_panel = box_sub_panel(
            layout,
            "WPAINT_HLT",
            title,
            gbh_rig,
            "rig_weight_paint",
            False
        )
        if sub_panel[0]:
            body = sub_panel[2]
            if not scene.hair_object:
                row = body.row()
                row.label(text="Please select a hair object.", icon="INFO")
                return

            armature_name = f"{scene.hair_object.name}_Armature"
            existing_armature = bpy.data.objects.get(armature_name)

            if not existing_armature:
                row = body.row()
                row.label(text="Please generate armature first.", icon="INFO")
                return
            box = body.box()
            col = box.column()
            col.label(text="Clear Weight Paint from Roots")
            col.prop(
                gbh_rig,
                "wp_clear_from_roots_switch",
            )
            col = box.column()
            col.enabled = gbh_rig.wp_clear_from_roots_switch
            col.prop(
                gbh_rig,
                "wp_clear_from_roots_distance",
            )

            box = body.box()
            col = box.column()
            col.label(text="Levels")

            col.prop(
                gbh_rig,
                "wp_tweak_levels_switch",
            )
            col = box.column()
            col.enabled = gbh_rig.wp_tweak_levels_switch
            col.prop(
                gbh_rig,
                "wp_levels_offset",
            )
            col.prop(
                gbh_rig,
                "wp_level_gain",
                slider=True,
            )

            box = body.box()
            col = box.column()
            col.label(text="Smoothing")

            col.prop(
                gbh_rig,
                "wp_smooth_switch",
            )
            col = box.column()
            col.enabled = gbh_rig.wp_smooth_switch
            col.prop(
                gbh_rig,
                "wp_smooth_factor",
                slider=True,
            )
            col.prop(
                gbh_rig,
                "wp_smooth_iterations",
            )
            col.prop(
                gbh_rig,
                "wp_smooth_expand",
            )

            box = body.box()
            col = box.column()
            if gbh_rig.rig_use_mods:
                col.prop(
                    gbh_rig,
                    "wp_fix_braids_switch",
                )
            col.operator("gbh.automatic_weight_paint")


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

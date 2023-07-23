# SPDX-License-Identifier: GPL-2.0-or-later

from bpy.types import UIList

from ..global_variables import LIST_ROWS
from . common_ui import clear_pointer_if_object_deleted


class OBJECT_UL_ui_presets_list(UIList):

    def draw_item(self, context, layout, data, item, icon, active_data, active_propname):
        if self.layout_type in {"DEFAULT", "COMPACT"}:
            layout.label(text=item.name)
        elif self.layout_type in {"GRID"}:
            layout.alignment = "CENTER"
            layout.label(text="", icon_value=icon)


def ui_hair_object(context, box):
    scene = context.scene

    # Close tweak panel if object was deleted
    clear_pointer_if_object_deleted(context, scene, "hair_object")

    row = box.column(align=True)
    row.label(text="Select Hair Object")
    row = box.row()
    row.prop(scene, "hair_object", text="")


def ui_hair_presets(context, layout):
    scene = context.scene
    wm = context.window_manager
    gbh_presets = wm.gbh_presets

    col = layout.column()
    col.prop(gbh_presets, "presets_hair_type", text="")
    if scene.hair_object or gbh_presets.presets_hair_type == "OBJECT":
        if gbh_presets.presets_hair_type != "NONE":

            col.template_list("OBJECT_UL_ui_presets_list", "", wm, "gbh_presets_list",
                              gbh_presets, "presets_list_index", rows=LIST_ROWS)

            box = col.box()
            row = box.row()
            row.label(text="Save Modifications as a Preset")
            sub_row = row.row()
            sub_row.alignment = "RIGHT"
            sub_row.operator("gbh.refresh_presets",
                             text="", icon="FILE_REFRESH")

            rem_button = sub_row.row()
            presets_list = wm.gbh_presets_list
            rem_button.enabled = len(presets_list) > 0
            rem_button.alert = len(presets_list) > 0
            rem_button.operator("gbh.remove_preset", text="", icon="REMOVE")

            row = box.row(align=True)
            row.enabled = scene.hair_object != None
            row.prop(gbh_presets, "new_preset_name", text="Name")
            row.operator("gbh.save_preset", text="", icon="ADD")

            col = box.column()
            col.scale_y = 1.5

            presets_list = wm.get("gbh_presets_list")

            if presets_list:
                if gbh_presets.presets_hair_type == "OBJECT":
                    text = "Import Hair Object to File"

                else:
                    # col.alert = True
                    text = "Apply Selected Preset to the Hair Object"

                col.operator("gbh.load_preset", text=text)

    else:
        col.separator()
        col.label(
            text='Select an object or switch to "Hair Objects" presets',
            icon="INFO"
        )


def ui_mod_copy(context, layout):
    scene = context.scene
    wm = context.window_manager
    gbh_mods = wm.gbh_mods

    box = layout.box()
    row = box.row()

    clear_pointer_if_object_deleted(context, gbh_mods, "mod_copy_object")

    row.label(text="Object to Copy from")
    if scene.hair_object:
        row.prop(gbh_mods, "mod_copy_object", text="")
        if gbh_mods.mod_copy_object:
            row = box.row()
            # row.alert = True
            row.operator("gbh.copy_mods_from")
    else:
        row = box.row()
        row.label(text="Select a hair object", icon="INFO")


classes = (
    OBJECT_UL_ui_presets_list,
)


def register():
    from bpy.utils import register_class
    for cls in classes:
        register_class(cls)


def unregister():
    from bpy.utils import unregister_class
    for cls in reversed(classes):
        unregister_class(cls)

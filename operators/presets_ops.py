# SPDX-License-Identifier: GPL-2.0-or-later

import bpy
import os
from bpy.types import Operator

from . import common_functions as cf
from .. import global_variables as gv

MAX_PRESET = 150

blend_files = []


def _get_path(context):
    wm = bpy.context.window_manager
    gbh_presets = wm.gbh_presets
    if context.active_object:
        bpy.ops.object.mode_set(mode="OBJECT")

    # Get presets path.
    path = os.path.join(gv.DIR_PRESETS, f"{gbh_presets.presets_hair_type}/")
    return path


def _write_to_file(self, path, name):
    data_blocks = {*bpy.context.selected_objects, }
    bpy.data.libraries.write(
        path + name + ".blend",
        data_blocks,
        compress=True,
        fake_user=True
    )


def _get_preset_file_name():
    wm = bpy.context.window_manager
    gbh_presets = wm.gbh_presets
    preset_index = gbh_presets.presets_list_index
    return bpy.context.window_manager["gbh_presets_list"][preset_index]["name"]


def _get_preset_file_loc(context, file_name):
    path = _get_path(context)
    return path + file_name + ".blend"


def refresh_presets_list(self, context):
    path = _get_path(context)
    wm = context.window_manager
    gbh_presets = wm.gbh_presets

    wm.gbh_presets_list.clear()
    blend_files.clear()

    if gbh_presets.presets_hair_type == "NONE":
        return

    try:
        files = [files for files in os.listdir(
            path) if os.path.isfile(os.path.join(path, files))]

        for file in files:
            if file.endswith(".blend"):
                blend_files.append(file[:-len(".blend")])

        for blend_file in blend_files:
            preset = wm.gbh_presets_list.add()
            preset.name = blend_file

    except FileNotFoundError as err:
        print(f"GBH Tool: {err}")
        err = f"Error: presets/{gbh_presets.presets_hair_type} directory has been moved or removed. Recreate directory or reinstall add-on."
        self.report({"ERROR"}, err)


"""
---------------------------------------------------------------------
Operators
---------------------------------------------------------------------
"""


class GBH_OT_save_preset(Operator):
    bl_idname = "gbh.save_preset"
    bl_label = "Save Preset"
    bl_description = "Save your modifications as a preset"

    def execute(self, context):
        scene = context.scene
        wm = context.window_manager
        gbh_presets = wm.gbh_presets
        object_name = gbh_presets.new_preset_name
        source_object = scene.hair_object
        # Save preset if it doesn't already exists, the name is not blank and the list items count is under 100.
        if object_name and object_name not in blend_files and len(blend_files) < 100:
            dif_name_than_hair = source_object.name != object_name
            if dif_name_than_hair:
                presets_type = gbh_presets.presets_hair_type
                if presets_type != "OBJECT":
                    dummy_object = cf.create_new_item(
                        context,
                        scene,
                        object_name,
                        "CURVES"
                    )
                    cf.copy_modifiers(context, source_object, dummy_object, True)
                else:
                    dummy_object = cf.duplicate_item(
                        context,
                        source_object,
                        object_name,
                        False,
                        False
                    )
                cf.set_active_object(context, dummy_object)

            else:
                cf.set_active_object(context, scene.hair_object)

            path = _get_path(context)
            _write_to_file(self, path, object_name)

            if dif_name_than_hair:
                cf.delete_item(dummy_object.data)

            gbh_presets.property_unset("new_preset_name")
            refresh_presets_list(self, context)

        elif object_name in blend_files:
            err = "Name is already used."
            self.report({"ERROR"}, err)

        elif len(blend_files) >= MAX_PRESET:
            err = f"Maximum presets per category is {MAX_PRESET}."
            self.report({"ERROR"}, err)

        else:
            err = "Preset name can't be blank."
            self.report({"ERROR"}, err)

        return {"FINISHED"}


class GBH_OT_remove_preset(Operator):
    bl_idname = "gbh.remove_preset"
    bl_label = "Remove Selected Preset"
    bl_description = "Remove selected preset from add-on permanently"

    def execute(self, context):
        wm = context.window_manager
        file_name = _get_preset_file_name()
        file_loc = _get_preset_file_loc(context, file_name)

        try:
            os.remove(file_loc)
            refresh_presets_list(self, context)
            gbh_presets = wm.gbh_presets

            # Change presets list index when removing and object to avoid index out of range error.
            if gbh_presets.presets_list_index > 0:
                gbh_presets.presets_list_index -= 1

            else:
                gbh_presets.presets_list_index -= 0

        except OSError as err:
            print(f"GBH Tool: {err}")
            err = "Preset is no longer available, refresh presets to update the list."
            self.report({"ERROR"}, err)

        return {"FINISHED"}


class GBH_OT_load_preset(Operator):
    bl_idname = "gbh.load_preset"
    bl_label = "Apply Preset to Object"
    bl_description = "Remove object's existing modifiers and apply selected preset to it"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        scene = context.scene
        wm = context.window_manager
        gbh_presets = wm.gbh_presets
        presets_list = wm.get("gbh_presets_list")
        pref = context.preferences.addons[gv.GBH_PACKAGE].preferences

        # Check if presets list is not empty.
        file_name = _get_preset_file_name()
        file_loc = _get_preset_file_loc(context, file_name)
        object_path = file_loc
        obj = cf.append_object(self, object_path, file_name)

        if gbh_presets.presets_hair_type != "OBJECT":
            cf.copy_modifiers(context, obj, scene.hair_object, True)
            cf.delete_item(obj.data)
            active_object = scene.hair_object

        elif pref.presets_place_at_cursor_location:
            obj.location = bpy.context.scene.cursor.location
            active_object = obj

        else:
            active_object = obj

        cf.set_active_object(context, active_object)

        return {"FINISHED"}


class GBH_OT_refresh_list(Operator):
    bl_idname = "gbh.refresh_presets"
    bl_label = "Refresh Presets List"
    bl_description = "Refresh presets list"

    def execute(self, context):
        refresh_presets_list(self, context)

        return {"FINISHED"}


classes = (
    GBH_OT_refresh_list,
    GBH_OT_save_preset,
    GBH_OT_load_preset,
    GBH_OT_remove_preset,
)


def register():
    from bpy.utils import register_class
    for cls in classes:
        register_class(cls)


def unregister():
    from bpy.utils import unregister_class
    for cls in reversed(classes):
        unregister_class(cls)

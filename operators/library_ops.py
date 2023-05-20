# SPDX-License-Identifier: GPL-2.0-or-later

import bpy
import os
import subprocess
import re
from bpy.app.handlers import persistent
from bpy.types import Operator
from bpy.props import IntProperty, StringProperty

from .. import constants as const
from . import common_functions as cf


LIB_REFRESHED = "Library reloaded."
NO_BLEND_FILE = "No .blend file found in the selected directory."

_blends_collection = []
_materials_collection = []
_node_groups_collection = []
_filtered_materials_collection = []
_filtered_node_groups_collection = []


def get_materials():
    return _filtered_materials_collection


def get_node_groups():
    return _filtered_node_groups_collection


def get_blend_files():
    wm = bpy.context.window_manager
    gbh_lib = wm.gbh_lib
    return _blends_collection if gbh_lib.lib_category == "USER" else None


@persistent
def load_library(self, context):
    pref = bpy.context.preferences.addons[const.GBH_PACKAGE].preferences
    wm = bpy.context.window_manager
    gbh_lib = wm.gbh_lib

    gbh_lib.lib_page_index = 0
    _blends_collection.clear()
    _materials_collection.clear()
    _node_groups_collection.clear()
    _filtered_materials_collection.clear()
    _filtered_node_groups_collection.clear()

    if gbh_lib.lib_category == "GBH":
        gbh_lib.lib_path = const.DIR_LIBRARY

    elif gbh_lib.lib_category == "BLENDER":
        gbh_lib.lib_path = const.DIR_BLENDER_ASSETS

    elif gbh_lib.lib_category == "USER":
        gbh_lib.lib_path = pref.lib_user_folder

    if cf.directory_check(gbh_lib.lib_path):
        _load_blend_file(gbh_lib.lib_path)

    else:
        return True, const.INVALID_PATH

    if not _blends_collection:
        return True, NO_BLEND_FILE

    elif gbh_lib.asset_category == "NODES":
        _load_node_groups(gbh_lib.lib_path)
        return False, LIB_REFRESHED

    elif gbh_lib.asset_category == "MATERIALS":
        _load_materials(gbh_lib.lib_path)
        return False, LIB_REFRESHED


def _load_blend_file(path):
    _blends_collection.clear()
    files = [
        files for files in os.listdir(path) if os.path.isfile(os.path.join(path, files))
    ]
    # List .blend files
    _blends_collection.extend(
        [file for file in files if file.endswith(".blend")]
    )
    _blends_collection.sort()


def _load_materials(path):
    for blend in _blends_collection:
        blend_file = os.path.join(path, blend)
        with bpy.data.libraries.load(blend_file, link=False) as (data_from, data_to):
            # List materials
            _materials_collection.extend(
                [(mat, blend) for mat in filter(None, data_from.materials)]
            )

    _filtered_materials_collection.extend(_materials_collection)
    _filtered_materials_collection.sort()


def _load_node_groups(path):
    for blend in _blends_collection:
        blend_file = os.path.join(path, blend)
        with bpy.data.libraries.load(blend_file, link=False) as (data_from, data_to):
            # List node groups
            _node_groups_collection.extend(
                [(ng, blend) for ng in filter(None, data_from.node_groups)]
            )

    _filtered_node_groups_collection.extend(_node_groups_collection)
    _filtered_node_groups_collection.sort()


def _add_nodes_to_object(self, context, ng_name):
    # If the node tree shown in the library is not of geometry nodes type
    if bpy.data.node_groups[ng_name].type != "GEOMETRY":
        err = "Selected node group is not of type geometry nodes and can't be added to objects."
        self.report({"ERROR"}, err)
        return

    if context.active_object:
        bpy.ops.object.mode_set(mode="OBJECT")

    invalid_type = False
    if context.selected_objects:
        for obj in context.selected_objects:
            valid_types = ["CURVES", "CURVE", "MESH"]
            if obj.type in valid_types:
                if not obj.modifiers.get(ng_name):
                    # Add geometry node modifier then set modifier's node group
                    obj.modifiers.new(name=ng_name, type="NODES")
                # Set modifier's node group
                obj.modifiers[ng_name].node_group = bpy.data.node_groups[ng_name]

            if obj.type not in valid_types:
                # If the selected object's type is not mesh or curve or hair curves
                invalid_type = True

    else:
        err = "No valid active object found. Please select a valid object and try again."
        self.report({"ERROR"}, err)

    if invalid_type:
        err = "The node group can only be added to curves, hair curves or meshes. One or more of the selected objects do not belong to any of these types."
        self.report({"ERROR"}, err)


def lib_search():
    wm = bpy.context.window_manager
    gbh_lib = wm.gbh_lib

    # Set search domain category
    if gbh_lib.asset_category == "MATERIALS":
        original_list = _materials_collection
        filtered_list = _filtered_materials_collection

    else:
        original_list = _node_groups_collection
        filtered_list = _filtered_node_groups_collection

    wanted = gbh_lib.lib_search

    filtered_list.clear()
    gbh_lib.lib_page_index = 0

    if gbh_lib.lib_search == "":
        filtered_list.extend(original_list)

    else:
        for item in original_list:
            if re.search(wanted.lower(), item[0].lower()):
                filtered_list.append(item)

    filtered_list.sort()


"""
---------------------------------------------------------------------
Operators
---------------------------------------------------------------------
"""


class GBH_OT_reload_library(Operator):
    bl_idname = "gbh.reload_library"
    bl_label = "Reload Library"
    bl_description = "Reload library items"

    def execute(self, context):
        err, report = load_library(self, context)

        if err:
            self.report({"ERROR"}, report)
            return {"CANCELLED"}

        else:
            self.report({"INFO"}, report)
            return {"FINISHED"}


class GBH_OT_node_group_append(Operator):
    bl_idname = "gbh.node_group_append"
    bl_label = "Append Node Group"
    bl_description = "Append selected node group to current file"

    nodename: StringProperty(
        name="nodename",
        default="default",
    )

    def execute(self, context):
        # Separate node name and file name
        ng_name = eval(self.nodename)[0]
        blend_name = eval(self.nodename)[1]

        # Blend file path
        wm = bpy.context.window_manager
        gbh_lib = wm.gbh_lib
        blend_path = os.path.join(gbh_lib.lib_path, blend_name)

        # Import selected node group
        cf.append_node_groups(self, context, blend_path, ng_name)
        return {"FINISHED"}


class GBH_OT_node_group_add_to_object(Operator):
    bl_idname = "gbh.node_group_add_to_object"
    bl_label = "Assign Node Group"
    bl_description = "Assign node group to selected hair object in the viewport"
    bl_options = {"REGISTER", "UNDO"}

    nodename: StringProperty(
        name="nodename",
        default="default",
    )

    def execute(self, context):
        scene = context.scene
        pref = bpy.context.preferences.addons[const.GBH_PACKAGE].preferences

        if not pref.lib_add_to_active_object and scene.hair_object:
            obj = scene.hair_object
            cf.set_active_object(context, obj)
            ng_name = eval(self.nodename)[0]
            _add_nodes_to_object(self, context, ng_name)

        elif pref.lib_add_to_active_object and context.active_object:
            ng_name = eval(self.nodename)[0]
            _add_nodes_to_object(self, context, ng_name)

        else:
            # If there's no valid object selected (usually occurs after deleting and object and not selecting a new one)
            err = (
                "No valid active object found. Please select a valid object and try again."
                if pref.lib_add_to_active_object
                else "No hair object is selected. Select an object in add-on's "
                + '"Hair" panel and try again.'
            )
            self.report({"ERROR"}, err)

        return {"FINISHED"}


class GBH_OT_node_group_delete(Operator):
    bl_idname = "gbh.node_group_delete"
    bl_label = "Delete Node Group"
    bl_description = "Delete node group from file"
    bl_options = {"REGISTER", "UNDO"}

    nodename: StringProperty(
        name="nodename",
        default="default",
    )

    def execute(self, context):
        node_groups = bpy.data.node_groups
        ng_name = eval(self.nodename)[0]

        if node_groups.get(ng_name):
            cf.delete_item(node_groups[ng_name])
            return {"FINISHED"}

        else:
            return {"CANCELLED"}


class GBH_OT_material_append(Operator):
    bl_idname = "gbh.material_append"
    bl_label = "Append Material"
    bl_description = "Append selected material to current file"

    matname: StringProperty(
        name="matname",
        default="default",
    )

    def execute(self, context):
        # Separate material name and file name
        mat_name = eval(self.matname)[0]
        blend_name = eval(self.matname)[1]

        # Blend file path
        wm = bpy.context.window_manager
        gbh_lib = wm.gbh_lib
        blend_path = os.path.join(gbh_lib.lib_path, blend_name)

        # Import selected material
        cf.append_materials(self, context, blend_path, mat_name)
        return {"FINISHED"}


class GBH_OT_material_delete(Operator):
    bl_idname = "gbh.material_delete"
    bl_label = "Delete Material"
    bl_description = "Delete selected material from file"
    bl_options = {"REGISTER", "UNDO"}

    matname: StringProperty(
        name="matname",
        default="default",
    )

    def execute(self, context):
        materials = bpy.data.materials
        mat_name = eval(self.matname)[0]
        if not materials.get(mat_name):
            return {"CANCELLED"}

        images = bpy.data.images
        orphan_images_list = [img for img in images if not img.users]
        # Delete material
        cf.delete_item(materials[mat_name])
        # Delete newly orphaned images
        for img in images:
            if not img.users and img not in orphan_images_list:
                images.remove(img)

        return {"FINISHED"}


class GBH_OT_open_user_lib(Operator):
    bl_idname = "gbh.open_user_lib"
    bl_label = "Open User's Library Directory"
    bl_description = "Open user's library directory and load geometry nodes from .blend files"

    def execute(self, context):
        wm = bpy.context.window_manager
        gbh_lib = wm.gbh_lib
        # Change category to user when setting user's library directory
        gbh_lib.lib_category = "USER"

        err, report = load_library(self, context)

        if err:
            self.report({"ERROR"}, report)
            return {"CANCELLED"}

        else:
            self.report({"INFO"}, report)
            return {"FINISHED"}


class GBH_OT_close_user_lib(Operator):
    bl_idname = "gbh.close_user_lib"
    bl_label = "Close User's Library Directory"
    bl_description = "Close user's library and clear user's items from list"

    def execute(self, context):
        pref = bpy.context.preferences.addons[const.GBH_PACKAGE].preferences

        # Clear listed items
        _blends_collection.clear()
        _materials_collection.clear()
        _node_groups_collection.clear()
        _filtered_materials_collection.clear()
        _filtered_node_groups_collection.clear()

        # Unset loaded directory
        pref.property_unset("lib_user_folder")
        return {"FINISHED"}


class GBH_OT_open_user_file(Operator):
    bl_idname = "gbh.open_user_file"
    bl_label = "Open User's Library File"
    bl_description = "Open user's library file"

    filename: StringProperty(
        name="filename",
        default="default",
    )

    def execute(self, context):
        pref = bpy.context.preferences.addons[const.GBH_PACKAGE].preferences

        user_lib_path = pref.lib_user_folder
        file_path = os.path.join(user_lib_path, self.filename)

        try:
            if os.path.isfile(file_path):
                subprocess.Popen(["blender", file_path])

        # If no default blender installation is set in the OS
        except (RuntimeError, OSError) as err:
            err = "Couldn't find a Blender installation, try opening your file from your OS."
            self.report({"ERROR"}, err)

        # If file was removed after loading user directory
        if not os.path.isfile(file_path):
            err = "File has been moved or removed."
            self.report({"ERROR"}, err)

        return {"FINISHED"}


class GBH_OT_lib_clear_search(Operator):
    bl_idname = "gbh.lib_clear_search"
    bl_label = "Clear Search Results"
    bl_description = "Clear library search results"

    def execute(self, context):
        wm = bpy.context.window_manager
        gbh_lib = wm.gbh_lib

        gbh_lib.property_unset("lib_search")
        gbh_lib.lib_page_index = 0

        # Clear filtered lists
        _filtered_node_groups_collection.clear()
        _filtered_materials_collection.clear()

        # Set filtered lists to raw lists
        _filtered_node_groups_collection.extend(_node_groups_collection)
        _filtered_materials_collection.extend(_materials_collection)

        # Sort filtered lists
        _filtered_node_groups_collection.sort()
        _filtered_materials_collection.sort()
        return {"FINISHED"}


class GBH_OT_change_lib_page(Operator):
    bl_idname = "gbh.change_lib_page"
    bl_label = "Change Library Page"
    bl_description = "Change library page"

    page_index: IntProperty(
        name="page_index",
        default=0,
    )

    def execute(self, context):
        wm = bpy.context.window_manager
        gbh_lib = wm.gbh_lib

        # Set library page index
        gbh_lib.lib_page_index = self.page_index
        return {"FINISHED"}


classes = (
    GBH_OT_reload_library,
    GBH_OT_node_group_append,
    GBH_OT_node_group_add_to_object,
    GBH_OT_node_group_delete,
    GBH_OT_material_append,
    GBH_OT_material_delete,
    GBH_OT_open_user_lib,
    GBH_OT_close_user_lib,
    GBH_OT_open_user_file,
    GBH_OT_lib_clear_search,
    GBH_OT_change_lib_page,
)


def register():
    from bpy.utils import register_class
    for cls in classes:
        register_class(cls)

    bpy.app.handlers.load_post.append(load_library)


def unregister():
    from bpy.utils import unregister_class
    for cls in reversed(classes):
        unregister_class(cls)

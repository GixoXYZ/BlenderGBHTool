# SPDX-License-Identifier: GPL-2.0-or-later

import bpy
from bpy.types import Operator
from bpy.props import EnumProperty, StringProperty

from . import common_functions as cf


def _attr_or_vertex_group_name_enum_items(self, context):
    scene = context.scene
    obj = scene.hair_object

    # Get available attributes.
    groups = [
        (group.name, f"Point > {group.name}", "") for group in obj.vertex_groups
    ]

    if obj.type == "CURVE":
        attrs = [
            ("tilt", "Point > tilt", ""),
            ("normal_mode", "Spline > normal_mode", ""),
            ("curve_type", "Spline > curve_type", ""),
            ("cyclic", "Spline > cyclic", ""),
            ("radius", "Point > radius", ""),
            ("resolution", "Spline > resolution", ""),
            ("position", "Point > position", "")
        ]
    else:
        attrs = [
            (attr.name, f"{attr.domain.capitalize()} > {attr.name}", "") for attr in obj.data.attributes
        ]
    return groups + attrs


"""
---------------------------------------------------------------------
Operators
---------------------------------------------------------------------
"""


class GBH_OT_modifier_move(Operator):
    bl_idname = "gbh.modifier_move"
    bl_label = "Move Modifier"
    bl_description = "Move selected modifier up/down"

    direction: bpy.props.EnumProperty(
        items=(
            ("UP", "Up", ""),
            ("DOWN", "Down", ""),
        )
    )

    def execute(self, context):
        scene = context.scene
        obj = scene.hair_object
        cf.set_active_object(context, obj)
        idx = obj.selected_mod_index

        try:
            mod = obj.modifiers[idx]

        except (IndexError, AttributeError):
            pass

        else:
            if self.direction == "DOWN" and idx < len(obj.modifiers) - 1:
                if bpy.ops.object.modifier_move_down(modifier=mod.name) == {"FINISHED"}:
                    obj.selected_mod_index += 1

            elif self.direction == "UP" and idx >= 1:
                if bpy.ops.object.modifier_move_up(modifier=mod.name) == {"FINISHED"}:
                    obj.selected_mod_index -= 1

        return {"FINISHED"}


class GBH_OT_modifier_new(Operator):
    bl_idname = "gbh.modifier_new"
    bl_label = "Add New Geometry Nodes Modifier"
    bl_description = "Add a new geometry nodes modifier to the hair object"

    direction: bpy.props.EnumProperty(
        items=(
            ("UP", "Up", ""),
            ("DOWN", "Down", ""),
        )
    )

    def execute(self, context):
        scene = context.scene
        cf.set_active_object(context, scene.hair_object)
        bpy.ops.object.modifier_add(type="NODES")
        return {"FINISHED"}


class GBH_OT_ng_new(Operator):
    bl_idname = "gbh.ng_new"
    bl_label = "Add New Node Group to Modifier"
    bl_description = "Add a new node group to the selected modifier"

    direction: bpy.props.EnumProperty(items=(("UP", "Up", ""),
                                             ("DOWN", "Down", ""),))

    def execute(self, context):
        scene = context.scene
        obj = scene.hair_object
        cf.set_active_object(context, obj)
        mod_list = list(obj.modifiers)
        mod = mod_list[obj.selected_mod_index]
        bpy.ops.object.modifier_set_active(modifier=mod.name)
        bpy.ops.node.new_geometry_node_group_assign()
        return {"FINISHED"}


class GBH_OT_modifier_remove(Operator):
    bl_idname = "gbh.remove_item"
    bl_label = "Remove Modifier"
    bl_description = "Remove selected modifier from object"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        scene = context.scene
        obj = scene.hair_object
        cf.set_active_object(context, obj)
        mod_list = list(obj.modifiers)
        mod = mod_list[obj.selected_mod_index]

        bpy.ops.object.modifier_remove(modifier=mod.name)

        if obj.selected_mod_index > 0:
            obj.selected_mod_index -= 1

        else:
            obj.selected_mod_index == 0

        return {"FINISHED"}


class GBH_OT_input_attr_toggle(Operator):
    bl_idname = "gbh.input_attr_toggle"
    bl_label = "Toggle Attribute Input Field"
    bl_description = "Toggle the attribute input field for the selected input"

    i: StringProperty(
        name="input",
    )

    def execute(self, context):
        scene = context.scene
        ng_index = scene.hair_object.selected_mod_index
        attr = scene.hair_object.modifiers[ng_index][self.i]
        scene.hair_object.modifiers[ng_index][self.i] = 1 if attr == 0 else 0
        return {"FINISHED"}


class GBH_OT_geometry_nodes_attr_search(Operator):
    bl_idname = "gbh.geometry_nodes_attr_search"
    bl_label = "Attribute Search"
    bl_description = "Search attributes and vertex groups for the field"
    bl_options = {"REGISTER", "INTERNAL", "UNDO"}
    bl_property = "attr_or_vertex_group_name"

    attr_or_vertex_group_name: EnumProperty(
        items=_attr_or_vertex_group_name_enum_items
    )
    property_name: StringProperty()

    def execute(self, context):
        scene = context.scene
        obj = scene.hair_object
        active_mod = obj.modifiers[obj.selected_mod_index]
        setattr(active_mod, self.property_name, self.attr_or_vertex_group_name)
        return {"FINISHED"}

    def invoke(self, context, event):
        context.window_manager.invoke_search_popup(self)
        return {"CANCELLED"}


class GBH_OT_apply_modifier(Operator):
    bl_idname = "gbh.apply_item"
    bl_label = "Apply Modifier"
    bl_description = "Apply selected modifier"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        scene = context.scene
        obj = scene.hair_object
        cf.set_active_object(context, obj)
        mod_list = list(obj.modifiers)
        mod = mod_list[obj.selected_mod_index]

        try:
            bpy.ops.object.modifier_apply(modifier=mod.name)

        except RuntimeError as err:
            print(f"GBH Tool: {err}")
            if scene.hair_object.type == "CURVE":
                err = "Cannot apply constructive modifiers on curve. Convert curve in order to apply."

            else:
                err = "Cannot apply modifier."

            self.report({"ERROR"}, err)

        return {"FINISHED"}


# Delete all object's modifiers except then ones generated with GBH Tool.
class GBH_OT_delete_all_mods(Operator):
    bl_idname = "gbh.delete_all_mods"
    bl_label = "Delete All Modifiers"
    bl_description = "Delete all modifiers from selected object"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        scene = context.scene
        obj = scene.hair_object
        cf.set_active_object(context, obj)
        mods = obj.modifiers

        if len(mods) > 0:
            for mod in mods:
                bpy.ops.object.modifier_remove(modifier=mod.name)
            info = "All modifiers are deleted."

        else:
            info = "Object has no modifiers."
        self.report({"INFO"}, info)
        return {"FINISHED"}


class GBH_OT_copy_mods_from(Operator):
    bl_idname = "gbh.copy_mods_from"
    bl_label = "Copy Modifiers from Selected Object"
    bl_description = "Copy and replace all modifiers and node groups from selected object"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        scene = context.scene
        wm = context.window_manager
        gbh_mods = wm.gbh_mods
        target_object = scene.hair_object

        if source_object := gbh_mods.mod_copy_object:
            cf.copy_modifiers(context, source_object, target_object, True)
            gbh_mods.property_unset("mod_copy_object")
            return {"FINISHED"}

        else:
            return {"CANCELLED"}


classes = (
    GBH_OT_ng_new,
    GBH_OT_apply_modifier,
    GBH_OT_modifier_new,
    GBH_OT_modifier_move,
    GBH_OT_modifier_remove,
    GBH_OT_input_attr_toggle,
    GBH_OT_geometry_nodes_attr_search,
    GBH_OT_delete_all_mods,
    GBH_OT_copy_mods_from,
)


def register():
    from bpy.utils import register_class
    for cls in classes:
        register_class(cls)


def unregister():
    from bpy.utils import unregister_class
    for cls in reversed(classes):
        unregister_class(cls)

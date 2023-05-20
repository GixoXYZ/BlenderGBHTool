# SPDX-License-Identifier: GPL-2.0-or-later

import bpy
import os
from bpy.types import Operator

from .. constants import DIR_ASSETS, PRE_MADE_NODES_FILE
from . import common_functions as cf


def _add_parent_bone(scene, armature_name, parent_size):
    # Adding parent bone
    bpy.ops.object.mode_set(mode="EDIT")
    # Get edit bones
    edit_bones = bpy.data.objects[armature_name].data.edit_bones
    # Add new bone
    new_bone = edit_bones.new("parent_bone")
    new_bone.head = (0, 0, 0)
    new_bone.tail = (0, 0, parent_size)

    bones = bpy.data.armatures[armature_name].bones
    for bone in bones:
        if not bone.parent:
            # Select bone by name
            edit_bones.active = edit_bones[bone.name]
            # Set parent of selected bone
            edit_bones.active.parent = edit_bones["parent_bone"]

    bpy.ops.object.mode_set(mode="OBJECT")


def _apply_skin_modifier(context, new_object, armature_name):
    cf.set_active_object(context, new_object)
    # Add skin modifier
    bpy.ops.object.modifier_add(type="SKIN")
    # Set root vertex for converted mesh
    bpy.ops.object.mode_set(mode="EDIT")
    bpy.ops.mesh.select_all(action="SELECT")
    bpy.ops.object.skin_root_mark()
    bpy.ops.object.mode_set(mode="OBJECT")

    if existing_armature := bpy.data.armatures.get(armature_name):
        bpy.data.armatures.remove(existing_armature, do_unlink=True)
    bpy.ops.object.skin_armature_create(modifier="")

    # Change armature name and display mode
    context.object.name = armature_name
    context.object.data.name = armature_name
    context.object.data.display_type = "OCTAHEDRAL"


def _clean_up(dummy_mesh, convert_ng, hair_duple):
    items = [
        dummy_mesh.data,
        bpy.data.node_groups[convert_ng],
        hair_duple.data,
    ]
    for item in items:
        cf.delete_item(item)


def _use_mods(context, hair_object, hair_duple):
    wm = context.window_manager
    gbh_rig = wm.gbh_rig

    cf.copy_modifiers(context, hair_object, hair_duple, False)
    duple_modifiers = []
    duple_modifiers.clear()

    unused_modifiers = []
    unused_modifiers.clear()

    duple_modifiers.extend(
        mod for mod in hair_duple.modifiers if hasattr(mod, "node_group")
    )
    if duple_modifiers:
        for mod in duple_modifiers:
            if hasattr(mod.node_group, "nodes"):
                mesh_node_types = [
                    "CURVE_TO_MESH",
                    "MESH_PRIMITIVE_CONE",
                    "MESH_PRIMITIVE_CUBE",
                    "MESH_PRIMITIVE_CYLINDER",
                    "MESH_PRIMITIVE_GRID",
                    "MESH_PRIMITIVE_ICO_SPHERE",
                    "MESH_PRIMITIVE_CIRCLE",
                    "MESH_PRIMITIVE_LINE",
                    "MESH_PRIMITIVE_UV_SPHERE",
                ]

                if next(
                    (node for node in mod.node_group.nodes if node.type in mesh_node_types),
                    None
                ):
                    unused_modifiers.append(mod.node_group.name)
                    hair_duple.modifiers.remove(mod)

    gbh_rig.rig_not_used = str(unused_modifiers)


"""
---------------------------------------------------------------------
Operators
---------------------------------------------------------------------
"""


class GBH_OT_hair_to_armature(Operator):
    bl_idname = "gbh.hair_to_armature"
    bl_label = "Generate Armature"
    bl_description = "Generates armature for selected hair"

    def execute(self, context):
        scene = context.scene
        wm = context.window_manager
        gbh_rig = wm.gbh_rig
        hair_object = scene.hair_object

        convert_ng = "RigMaker"
        dummy_name = f"{hair_object.name}_ArmMesh"
        duple_name = f"{scene.hair_object.name}_Duple"
        armature_name = f"{scene.hair_object.name}_Armature"
        convert_node_group = bpy.data.node_groups.get(convert_ng)

        location = hair_object.matrix_world.translation
        rotation = hair_object.rotation_euler

        # If rig maker node group doesn't already exist in file
        if not convert_node_group:
            path = os.path.join(DIR_ASSETS, PRE_MADE_NODES_FILE)
            cf.append_node_groups(self, context, path, convert_ng)

        dummy_mesh = cf.create_mesh_object(self, context, dummy_name)

        cf.set_object_location(dummy_mesh, location)
        cf.set_object_rotation(dummy_mesh, rotation)

        hair_duple = cf.duplicate_item(
            context,
            scene,
            hair_object,
            duple_name,
            False
        )
        cf.set_object_location(hair_duple, location)
        cf.set_object_rotation(hair_duple, rotation)

        if gbh_rig.rig_use_mods:
            _use_mods(context, hair_object, hair_duple)

        object_pointer = [[scene, "object_pointer", hair_duple]]

        float_props = [
            [gbh_rig, "rig_density"],
            [gbh_rig, "rig_start"],
            [gbh_rig, "rig_end"],
        ]
        int_props = [
            [gbh_rig, "rig_res"],
        ]
        bool_props = [
            [gbh_rig, "rig_reverse"],
        ]

        cf.set_ng_modifiers(
            dummy_mesh,
            convert_ng,
            pointer_props=object_pointer,
            float_props=float_props,
            int_props=int_props,
            bool_props=bool_props,
        )

        cf.convert_object(context, dummy_mesh, "MESH")

        try:
            _apply_skin_modifier(context, dummy_mesh, armature_name)
            if gbh_rig.rig_add_parent_bone:
                parent_size = gbh_rig.rig_parent_size/100
                _add_parent_bone(scene, armature_name, parent_size)

            _clean_up(dummy_mesh, convert_ng, hair_duple)
            return {"FINISHED"}

        except RuntimeError:
            if existing_armature := bpy.data.armatures.get(armature_name):
                bpy.data.armatures.remove(existing_armature, do_unlink=True)

            _clean_up(dummy_mesh, convert_ng, hair_duple)
            return {"CANCELLED"}


classes = (
    GBH_OT_hair_to_armature,
)


def register():
    from bpy.utils import register_class
    for cls in classes:
        register_class(cls)


def unregister():
    from bpy.utils import unregister_class
    for cls in reversed(classes):
        unregister_class(cls)

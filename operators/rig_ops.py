# SPDX-License-Identifier: GPL-2.0-or-later

import bpy
import os
from bpy.types import Operator
from mathutils import Vector

from ..global_variables import DIR_ASSETS, PRE_MADE_NODES_FILE
from . import common_functions as cf


def _add_parent_bone(scene, context, armature_name, parent_size):
    bone_obj = bpy.data.objects[armature_name]
    cf.set_active_object(context, bone_obj)
    # Adding parent bone
    bpy.ops.object.mode_set(mode="EDIT")
    # Get edit bones
    edit_bones = bone_obj.data.edit_bones
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

    gbh_rig.rig_not_used_mods = str(unused_modifiers)


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
                parent_size = gbh_rig.rig_parent_size / 100
                _add_parent_bone(scene, context, armature_name, parent_size)

            _clean_up(dummy_mesh, convert_ng, hair_duple)
            return {"FINISHED"}

        except RuntimeError:
            if existing_armature := bpy.data.armatures.get(armature_name):
                bpy.data.armatures.remove(existing_armature, do_unlink=True)

            _clean_up(dummy_mesh, convert_ng, hair_duple)
            return {"CANCELLED"}


class GBH_OT_automatic_weight_paint(Operator):
    bl_idname = "gbh.automatic_weight_paint"
    bl_label = "Automatic Weight Paint"
    bl_description = "Automatically adds weight paint to the hair"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        scene = context.scene
        wm = context.window_manager
        gbh_rig = wm.gbh_rig

        if context.active_object:
            bpy.ops.object.mode_set(mode="OBJECT")

        bpy.context.scene["hair_object"].hide_set(False)

        org_hair_object = scene.hair_object
        org_parent_bone = gbh_rig.rig_add_parent_bone
        gbh_rig.rig_add_parent_bone = False

        try:
            bpy.ops.gbh.convert_hair(convert_to="MESH")
            test_mesh = bpy.context.object
            cf.delete_item(test_mesh.data)

        except RuntimeError as e:
            err = "Geometry from hair source does not contain a mesh."
            self.report({"ERROR"}, err)

            return {"CANCELLED"}

        cf.set_active_object(context, scene.hair_object)
        bpy.ops.object.duplicate(linked=False)
        dummy_hair_obj = scene.hair_object = bpy.context.object

        bpy.ops.gbh.delete_all_mods()

        bpy.ops.gbh.convert_hair(convert_to="CURVE")
        cf.delete_item(dummy_hair_obj.data)

        dummy_obj = bpy.context.object

        if gbh_rig.rig_use_mods and not gbh_rig.wp_fix_braids_switch:
            _use_mods(context, org_hair_object, dummy_obj)
            cf.set_active_object(context, dummy_obj)
            bpy.ops.object.convert(target="MESH")
            bpy.ops.object.convert(target="CURVE")

        objs = []
        for _ in dummy_obj.data.splines:
            bpy.ops.object.duplicate(linked=False)
            objs.append(bpy.context.object)

        objs_roots = []
        for obj_index, obj in enumerate(objs):
            scene.hair_object = obj
            splines = obj.data.splines
            for i, spline in enumerate(splines):
                if i != obj_index:
                    splines.remove(spline)

            point_co = obj.data.splines[0].points[0].co
            vector3_co = Vector((point_co.x, point_co.y, point_co.z))
            objs_roots.append(vector3_co)

            if gbh_rig.rig_use_mods and gbh_rig.wp_fix_braids_switch:
                _use_mods(context, org_hair_object, obj)
                cf.set_active_object(context, obj)
                # bpy.ops.object.convert(target="MESH")
                # bpy.ops.object.convert(target="CURVE")

            bpy.ops.gbh.hair_to_armature()

        cf.delete_item(dummy_obj.data)

        mesh_objs = []
        arm_objs = []
        for obj in objs:
            cf.copy_modifiers(context, org_hair_object, obj, False)
            scene.hair_object = obj
            bpy.ops.gbh.convert_hair(convert_to="MESH")
            mesh_objs.append(bpy.context.object)
            cf.delete_item(obj.data)

        for mesh_index, mesh in enumerate(mesh_objs):
            name = mesh.name.replace("Mesh", "Armature")
            active_object = bpy.data.objects[name]
            for bone_index, bone in enumerate(active_object.data.bones):
                bone.name = f"Hair{mesh_index + 1}_Bone{bone_index}"
            arm_objs.append(active_object)
            cf.select_objects(context, mesh, active_object)

            bpy.ops.object.parent_set(type="ARMATURE_AUTO")

            if gbh_rig.wp_clear_from_roots_switch:
                # Set the active object
                cf.set_active_object(context, mesh)
                # Make sure the object is in Weight Paint mode
                bpy.ops.object.mode_set(mode="WEIGHT_PAINT")
                for vertex in mesh.data.vertices:
                    root_co = objs_roots[mesh_index]
                    distance = (vertex.co - root_co).length
                    if distance <= (gbh_rig.wp_clear_from_roots_distance / 100):
                        # Iterate through the vertices and clear weight paint
                        for group in mesh.vertex_groups:
                            group.remove([vertex.index])

            if gbh_rig.wp_smooth_switch:
                bpy.ops.object.vertex_group_smooth(
                    group_select_mode="ALL",
                    factor=gbh_rig.wp_smooth_factor,
                    repeat=gbh_rig.wp_smooth_iterations,
                    expand=gbh_rig.wp_smooth_expand
                )

            if gbh_rig.wp_tweak_levels_switch:
                bpy.ops.object.vertex_group_levels(
                    group_select_mode="ALL",
                    offset=gbh_rig.wp_levels_offset,
                    gain=gbh_rig.wp_level_gain
                )

            # Update the view to reflect changes
            bpy.context.view_layer.update()

            # Exit weight paint mode
            bpy.ops.object.mode_set(mode="OBJECT")

        scene.hair_object = org_hair_object
        gbh_rig.rig_add_parent_bone = org_parent_bone

        armature_name = f"{org_hair_object.name}_Armature"
        mesh_name = f"{org_hair_object.name}_Mesh_WeightPainted"
        if hair_armature := bpy.data.objects.get(armature_name):
            cf.delete_item(hair_armature.data)

        if hair_mesh := bpy.data.objects.get(mesh_name):
            cf.delete_item(hair_mesh.data)

        cf.select_objects(context, arm_objs, arm_objs[0])
        bpy.ops.object.join()

        bpy.context.object.name = armature_name
        bpy.context.object.data.name = armature_name

        cf.select_objects(context, mesh_objs, mesh_objs[0])
        bpy.ops.object.join()
        bpy.context.object.name = mesh_name
        bpy.context.object.data.name = mesh_name

        if gbh_rig.rig_add_parent_bone:
            parent_size = gbh_rig.rig_parent_size / 100
            _add_parent_bone(scene, context, armature_name, parent_size)

        bpy.context.scene["hair_object"].hide_set(True)

        return {"FINISHED"}


class GBH_OT_select_similar_bones(Operator):
    bl_idname = "gbh.select_similar_bones"
    bl_label = "Select Similar Bones"
    bl_description = "Automatically select similar bones"
    bl_options = {"REGISTER", "UNDO"}

    # TODO Add select by in-chain location.
    def execute(self, context):
        wm = context.window_manager
        gbh_rig = wm.gbh_rig

        mode = bpy.context.mode

        if mode == "PAINT_WEIGHT":
            bone_name = bpy.context.object.parent.data.bones.active.name
            name_pattern = bone_name.split("_")[-1]
            armature_obj = bpy.context.object.parent
            armature_obj_data = armature_obj.data

            for bone in armature_obj_data.bones:
                bone.select = bool(bone.name.endswith(name_pattern))
        else:
            bone_name = bpy.context.object.data.bones.active.name
            name_pattern = bone_name.split("_")[-1]
            bpy.ops.pose.select_all(action="DESELECT")
            bpy.ops.object.select_pattern(pattern=f"*{name_pattern}")

        return {"FINISHED"}


class GBH_OT_select_all_bones(Operator):
    bl_idname = "gbh.select_all_bones"
    bl_label = "Select All Bones"
    bl_description = "Automatically all bones"
    bl_options = {"REGISTER", "UNDO"}

    # TODO Fix select all method.
    def execute(self, context):
        mode = bpy.context.mode

        if mode == "PAINT_WEIGHT":
            armature_obj = bpy.context.object.parent
            armature_obj_data = armature_obj.data

            for bone in armature_obj_data.bones:
                bone.select = True

        else:
            bpy.ops.pose.select_all(action="SELECT")

        return {"FINISHED"}


classes = (
    GBH_OT_hair_to_armature,
    GBH_OT_automatic_weight_paint,
    GBH_OT_select_similar_bones,
    GBH_OT_select_all_bones,
)


def register():
    from bpy.utils import register_class
    for cls in classes:
        register_class(cls)


def unregister():
    from bpy.utils import unregister_class
    for cls in reversed(classes):
        unregister_class(cls)

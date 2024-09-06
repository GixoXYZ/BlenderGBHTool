# SPDX-License-Identifier: GPL-2.0-or-later

import bpy
import os
from bpy.types import Operator
from bpy.props import StringProperty

from ..global_variables import DIR_ASSETS, PRE_MADE_NODES_FILE
from . import common_functions as cf


def _convert_uv(self, context, new_object):
    cf.set_active_object(context, new_object)

    # Check if object has UVMap attribute.
    attrib = context.object.data.attributes
    if attrib.get("UVMap"):
        attrib.active = attrib["UVMap"]
        bpy.ops.geometry.attribute_convert(
            mode="GENERIC", domain="CORNER", data_type="FLOAT2")

    else:
        err = "UVMap attribute not found."
        self.report({"ERROR"}, err)

    # Mesh vertices cleanup.
    if context.active_object:
        bpy.ops.object.mode_set(mode="EDIT")

    bpy.ops.mesh.select_all(action="SELECT")
    bpy.ops.mesh.remove_doubles()

    if context.active_object:
        bpy.ops.object.mode_set(mode="OBJECT")


"""
---------------------------------------------------------------------
Operators
---------------------------------------------------------------------
"""


class GBH_OT_convert_hair(Operator):
    bl_idname = "gbh.convert_hair"
    bl_label = "Convert Hair"
    bl_description = "Convert the modified hair into a new object"
    bl_options = {"REGISTER", "UNDO"}

    convert_to: StringProperty()

    def execute(self, context):
        scene = context.scene
        wm = context.window_manager
        gbh_convert = wm.gbh_convert
        hair_object = scene.hair_object

        curve_res = None
        res_switch = None
        object_pointer = [[scene, "object_pointer", hair_object]]

        # Set conversion type based on user input.
        if self.convert_to == "CURVE":
            convert_ng = "ConvertToCurve"
            suffix = "Curve"
            res_switch = [[gbh_convert, "convert_curve_res_switch"]]
            curve_res = [[gbh_convert, "convert_curve_res"]]

        elif self.convert_to == "CURVES":
            convert_ng = "ConvertToHairCurves"
            suffix = "Curves"
            res_switch = [[gbh_convert, "convert_curves_res_switch"]]
            curve_res = [[gbh_convert, "convert_curves_res"]]

        elif self.convert_to == "MESH":
            convert_ng = "ConvertToMesh"
            suffix = "Mesh"

        object_name = f"{scene.hair_object.name}_{suffix}"
        # Check if conversion node group already exist in current file.
        if bpy.data.node_groups.get(convert_ng):
            cf.delete_item(bpy.data.node_groups[convert_ng])

        # Append convert node group.
        path = os.path.join(DIR_ASSETS, PRE_MADE_NODES_FILE)
        cf.append_node_groups(self, context, path, convert_ng)
        # Create new mesh object.
        new_object = cf.create_mesh_object(self, context, object_name)
        location = hair_object.matrix_world.translation
        cf.set_object_location(new_object, location)
        # Set convert node group modifier and values.
        cf.set_ng_modifiers(
            new_object,
            convert_ng,
            pointer_props=object_pointer,
            int_props=curve_res,
            bool_props=res_switch,
        )
        # Convert hair.
        cf.convert_object(context, new_object, self.convert_to)
        # Convert UV attribute to UV map.
        if self.convert_to == "MESH":
            _convert_uv(self, context, new_object)

        # Check if the converted object is valid.
        if not cf.evaluate_object(self, context, new_object, self.convert_to):
            cf.delete_item(new_object.data)
            cf.delete_item(bpy.data.node_groups[convert_ng])
            return {"CANCELLED"}

        # Cleanup the conversion node group from current file.
        cf.delete_item(bpy.data.node_groups[convert_ng])
        return {"FINISHED"}


class GBH_OT_attach_curves_to_surface(Operator):
    bl_idname = "gbh.attach_curves_to_surface"
    bl_label = "Attach Selected Hair to Surface"
    bl_description = "Attach selected hair curves to surface"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        obj = context.active_object
        surface = obj.data.surface
        cf.select_objects(context, obj, surface)
        bpy.ops.curves.surface_set()
        bpy.ops.object.select_all(action="DESELECT")
        return {"FINISHED"}


class GBH_OT_strands_to_particle(Operator):
    bl_idname = "gbh.strands_to_particle"
    bl_label = "Convert Hair to Particles"
    bl_description = "Convert the modified hair into a particle system"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        bpy.ops.curves.convert_to_particle_system()

        return {"FINISHED"}


class GBH_OT_particle_to_strand(Operator):
    bl_idname = "gbh.particle_to_strand"
    bl_label = "Convert Particles to Hair Curves"
    bl_description = "Convert particle systems to hair curves"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        wm = context.window_manager
        gbh_convert = wm.gbh_convert
        parent_object = gbh_convert.particle_parent_object
        mods = parent_object.modifiers
        converted = False
        curves_count = []
        curves_count.clear()

        for mod in mods:
            name = gbh_convert.particle_to_curve_name
            if mod.type == "PARTICLE_SYSTEM":
                # Check if the particle system type is hair and its particle count is not zero.
                if mod.particle_system.settings.type == "HAIR" and mod.particle_system.settings.count > 0:
                    cf.set_active_object(context, parent_object)
                    bpy.ops.object.modifier_convert(modifier=mod.name)

                    # Set to be converted object's name.
                    obj = context.object
                    if name == "":
                        name = mod.particle_system.name

                    obj.name = name
                    cf.convert_object(context, obj, "CURVE")
                    cf.convert_object(context, obj, "CURVES")

                    # Get the strands count of the converted hair object.
                    result = cf.evaluate_object(
                        self,
                        context,
                        obj,
                        "CURVES"
                    )
                    curves = result[1]
                    curves_count.append(curves)
                    converted = True

                elif mod.particle_system.settings.count <= 0:
                    err = f"{mod.particle_system.name} has zero hair strands."
                    self.report({"ERROR"}, err)

                elif mod.particle_system.settings.type == "EMITTER":
                    err = f"{mod.particle_system.name} is an emitter particle system and cannot be converted."
                    self.report({"ERROR"}, err)

        if converted:
            info = f"Number of hair curves for each particle system: {', '.join(map(str, curves_count))}"
            self.report({"INFO"}, info)

        else:
            err = "Selected object doesn't have any hair particle system."
            self.report({"ERROR"}, err)

        return {"FINISHED"}


classes = (
    GBH_OT_convert_hair,
    GBH_OT_strands_to_particle,
    GBH_OT_particle_to_strand,
    GBH_OT_attach_curves_to_surface,
)


def register():
    from bpy.utils import register_class
    for cls in classes:
        register_class(cls)


def unregister():
    from bpy.utils import unregister_class
    for cls in reversed(classes):
        unregister_class(cls)

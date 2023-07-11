# SPDX-License-Identifier: GPL-2.0-or-later

import bpy
import os

HAIR_GEO_ERROR = "Geometry from hair source does not contain a"
HAIR_NUM = "Number of converted hair"

IMPORT_FAIL = "Failed to import, selected item is no longer available."


def _link_to_scene(item_name, data_block, scene):
    new_item = bpy.data.objects.new(item_name, data_block)
    scene.collection.objects.link(new_item)
    return new_item


def set_active_object(context, active_object):
    """Deselect every object and set the given one as active object"""
    if context.active_object:
        bpy.ops.object.mode_set(mode="OBJECT")

    if active_object:
        bpy.ops.object.select_all(action="DESELECT")
        active_object.select_set(state=True, view_layer=context.view_layer)
        context.view_layer.objects.active = active_object


def select_objects(context, objects, active_object):
    """Select multiple objects and set the given one as active object"""
    if context.active_object:
        bpy.ops.object.mode_set(mode="OBJECT")

    if objects and active_object:
        bpy.ops.object.select_all(action="DESELECT")
        if type(objects) is list:
            for obj in objects:
                obj.select_set(state=True, view_layer=context.view_layer)

        else:
            objects.select_set(state=True, view_layer=context.view_layer)

        context.view_layer.objects.active = active_object


def evaluate_object(self, context, obj, target_type):
    """Evaluate given object and get the evaluated object information"""
    depsgraph = context.evaluated_depsgraph_get()
    object_data = obj.data
    data_eval = object_data.evaluated_get(depsgraph)

    if hasattr(data_eval, "vertices"):
        if data_eval.vertices:
            info = f"{HAIR_NUM} mesh vertices: {len(data_eval.vertices)}"
            self.report({"INFO"}, info)
            return True

        else:
            if target_type == "MESH":
                err = f"{HAIR_GEO_ERROR} mesh."

            elif target_type == "CURVES":
                err = "It is not possible to convert hair objects that contain mesh into hair curves."

            if target_type == "CURVE":
                err = f"{HAIR_GEO_ERROR} curve."

            self.report({"ERROR"}, err)
            return False

    elif hasattr(data_eval, "splines"):
        if data_eval.splines:
            info = f"{HAIR_NUM} curve splines: {len(data_eval.splines)}"
            self.report({"INFO"}, info)
            return True, len(data_eval.splines)

        else:
            self.report({"ERROR"}, f"{HAIR_GEO_ERROR} curve.")
            return False

    elif hasattr(data_eval, "curves"):
        if data_eval.curves:
            info = f"{HAIR_NUM} curves: {len(data_eval.curves)}"
            self.report({"INFO"}, info)
            return True, len(data_eval.curves)

        else:
            err = f"{HAIR_GEO_ERROR} hair curve."
            self.report({"ERROR"}, err)
            return False

    else:
        err = "Geometry from hair source can't be converted."
        self.report({"ERROR"}, err)
        return False


def directory_check(path):
    return bool(os.path.isdir(path))


def delete_item(data_item):
    """Remove given data item based on its type"""
    if not data_item:
        return

    data_type = data_item.bl_rna.identifier
    item_name = data_item.name
    light_types = [
        "PointLight",
        "SunLight",
        "SpotLight",
        "AreaLight",
    ]

    if data_type == "Curve":
        data_list = bpy.data.curves

    elif data_type == "Curves":
        data_list = bpy.data.hair_curves

    elif data_type == "Mesh":
        data_list = bpy.data.meshes

    elif data_type == "Object":
        data_list = bpy.data.objects

    elif data_type == "GeometryNodeTree":
        data_list = bpy.data.node_groups

    elif data_type == "Material":
        data_list = bpy.data.materials

    elif data_type == "Scene":
        data_list = bpy.data.scenes

    elif data_type == "World":
        data_list = bpy.data.worlds

    elif data_type == "Camera":
        data_list = bpy.data.cameras

    elif data_type in light_types:
        data_list = bpy.data.lights

    if not data_list:
        return

    if data_list.get(item_name):
        data_list.remove(data_list[item_name], do_unlink=True)


def append_node_groups(self, context, path, ng_name):
    """Append and add to scene node groups from .blend file base on given path and name"""
    if context.active_object:
        bpy.ops.object.mode_set(mode="OBJECT")

    try:
        node_path = os.path.join(path, "NodeTree/")
        bpy.ops.wm.append(filename=ng_name, directory=node_path)

    except (RuntimeError,  OSError) as err:
        print(err)
        err = IMPORT_FAIL
        self.report({"ERROR"}, err)


def append_materials(self, context, path, mat_name):
    """Append and add to scene materials from .blend file base on given path and name"""
    if context.active_object:
        bpy.ops.object.mode_set(mode="OBJECT")

    try:
        mat_path = os.path.join(path, "Material/")
        bpy.ops.wm.append(filename=mat_name, directory=mat_path)

    except (RuntimeError,  OSError) as err:
        print(err)
        err = IMPORT_FAIL
        self.report({"ERROR"}, err)


def append_object(self, object_path, object_name):
    """Append and add to scene object from .blend file base on given path and name"""
    try:
        with bpy.data.libraries.load(object_path) as (data_from, data_to):
            data_to.objects = [
                name for name in data_from.objects if name.startswith(object_name)
            ]

        for obj in data_to.objects:
            bpy.context.scene.collection.objects.link(obj)
            return obj

    except (RuntimeError, OSError) as err:
        print(err)
        err = IMPORT_FAIL
        self.report({"ERROR"}, err)


def create_mesh_object(self, context, object_name):
    """Create mesh objects and link them to current scene"""
    if context.active_object:
        bpy.ops.object.mode_set(mode="OBJECT")

    if existing_object := bpy.data.objects.get(object_name):
        bpy.data.objects.remove(existing_object, do_unlink=True)

    mesh_block = bpy.data.meshes.new(object_name)
    return _link_to_scene(object_name, mesh_block, context.scene)


def convert_object(context, obj, target):
    """Convert object based on given type"""
    set_active_object(context, obj)
    bpy.ops.object.convert(target=target)


def duplicate_item(context, scene, source_item, duplicate_name, apply_transform):
    """Duplicate object using its data block"""
    duple_data = source_item.data.copy()
    duple_data.name = duplicate_name
    duple_object = _link_to_scene(duple_data.name, duple_data, scene)

    if apply_transform:
        set_active_object(context, duple_object)
        bpy.ops.object.transform_apply(
            location=True,
            rotation=True,
            scale=True
        )

    return duple_object


def copy_modifiers(context, source_object, target_object, clear_existing_modifiers):
    """Copy modifiers from given source to target object"""
    if source_object and target_object:
        if clear_existing_modifiers:
            mods = target_object.modifiers
            for mod in mods:
                target_object.modifiers.remove(mod)

        select_objects(
            context,
            objects=target_object,
            active_object=source_object
        )

        # Copy modifiers from source to target objects
        with context.temp_override(selected_objects=source_object):
            bpy.ops.object.make_links_data(type="MODIFIERS")


def set_object_location(obj, location):
    """Sets object location to given location"""
    objects = bpy.data.objects
    if objects.get(obj.name):
        objects[obj.name].location = location


def set_object_rotation(obj, rotation):
    """Sets object rotation to given rotation in degrees"""
    objects = bpy.data.objects
    if objects.get(obj.name):
        objects[obj.name].rotation_euler = rotation


def set_ng_modifiers(obj, ng_name, **kwargs):
    """Setups node groups as object modifier and changes the given node values"""
    pointer_props = kwargs.get("pointer_props")
    int_props = kwargs.get("int_props")
    float_props = kwargs.get("float_props")
    bool_props = kwargs.get("bool_props")

    # Add geometry node modifier to generated hair mesh

    if not obj.modifiers.get(ng_name):
        obj.modifiers.new(name=ng_name, type="NODES")

    ng = bpy.data.node_groups[ng_name]
    obj.modifiers[ng_name].node_group = ng

    # Set values for pointer props

    if pointer_props:
        for pointer_prop in pointer_props:
            if ng.nodes.get(pointer_prop[1]):
                ng.nodes[pointer_prop[1]].inputs[0].default_value = getattr(
                    pointer_prop[0],
                    pointer_prop[1],
                    pointer_prop[2]
                )

    # Set values for float props

    if float_props:
        for float_prop in float_props:
            if ng.nodes.get(float_prop[1]):
                ng.nodes[float_prop[1]].outputs[0].default_value = getattr(
                    float_prop[0],
                    float_prop[1]
                )

    # Set values for integer props

    if int_props:
        for int_prop in int_props:
            if ng.nodes.get(int_prop[1]):
                ng.nodes[int_prop[1]].integer = getattr(
                    int_prop[0],
                    int_prop[1]
                )

    # Set values for bool props

    if bool_props:
        for bool_prop in bool_props:
            if ng.nodes.get(bool_prop[1]):
                ng.nodes[bool_prop[1]].boolean = getattr(
                    bool_prop[0],
                    bool_prop[1]
                )


def create_new_item(context, scene, item_name, item_type):
    """Create new data block and add it to a new object and given scene"""
    if item_type == "CURVE":
        data_block = bpy.data.curves.new(item_name, "CURVE")
        return _link_to_scene(item_name, data_block, scene)

    if item_type == "CURVES":
        data_block = bpy.data.hair_curves.new(item_name)
        return _link_to_scene(item_name, data_block, scene)

    if item_type == "SCENE":
        bpy.ops.scene.new(type="NEW")
        scene = context.scene
        scene.name = item_name
        return scene

    if item_type == "SUN_LIGHT":
        data_block = bpy.data.lights.new(name=item_name, type="SUN")
        return _link_to_scene(item_name, data_block, scene)

    if item_type == "CAMERA":
        data_block = bpy.data.cameras.new(name=item_name)
        return _link_to_scene(item_name, data_block, scene)

    if item_type == "WORLD":
        world = bpy.data.worlds.new(item_name)
        scene.world = world
        return world

# SPDX-License-Identifier: GPL-2.0-or-later

import bpy
import os
import itertools
import shutil
import math
from bpy.types import Operator
from bpy.props import StringProperty

from .. import constants as const
from . import common_functions as cf


HC_TEXTURING_NAME = "Hair Card"


def _set_render_resolution(scene, resolution_x, resolution_y):
    scene.render.resolution_x = resolution_x
    scene.render.resolution_y = resolution_y


def _set_render_passes(view_layer, passes):
    for p in passes:
        setattr(view_layer, p, True)


def _create_compositor_nodes(context):
    scene = context.scene

    if not scene.use_nodes:
        scene.use_nodes = True

    tree = scene.node_tree
    render_layers_node = next(
        (node for node in tree.nodes if node.type == "R_LAYERS"),
        None
    )
    file_output_node = next(
        (node for node in tree.nodes if node.type == "OUTPUT_FILE"),
        None
    )

    if not render_layers_node:
        render_layers_node = tree.nodes.new(type="CompositorNodeRLayers")

    if not file_output_node:
        file_output_node = tree.nodes.new(type="CompositorNodeOutputFile")
        home_dir = os.path.expanduser("~")
        file_output_node.base_path = home_dir
        x = render_layers_node.location[0] + 500
        y = render_layers_node.location[1] - 110
        file_output_node.location = (x, y)

    if composite_node := next(
        (node for node in tree.nodes if node.type == "COMPOSITE"), None
    ):
        x = render_layers_node.location[0] + 500
        y = render_layers_node.location[1] + 25
        composite_node.location = (x, y)

    return render_layers_node, file_output_node


def _connect_compositor_nodes(context, render_layers_node, file_output_node):
    scene = context.scene
    tree = scene.node_tree
    wm = context.window_manager
    gbh_hair_card = wm.gbh_hair_card
    pref = context.preferences.addons[const.GBH_PACKAGE].preferences
    # Set output name
    output_name = gbh_hair_card.hc_output_name
    if output_name == "":
        output_name = "Texture"

    # Remove all existing nodes
    for i in file_output_node.inputs:
        file_output_node.inputs.remove(i)

    digits = ""
    if gbh_hair_card.hc_add_current_frame_to_names:
        i = 0
        while i < pref.hc_frame_digits:
            i += 1
            digits = f"{digits}#"

    # Get enabled render passes, create and connect sockets on file output node
    rl_node_outputs = render_layers_node.outputs
    for output in rl_node_outputs:
        if output.enabled:
            if gbh_hair_card.hc_add_current_frame_to_names:
                name = f"{output_name}_{output.name}{digits}"

            else:
                name = f"{output_name}_{output.name}"

            fo_input = file_output_node.file_slots.new(name)
            tree.links.new(fo_input, output)


def rename_renders(self):
    wm = bpy.context.window_manager
    gbh_hair_card = wm.gbh_hair_card
    if not gbh_hair_card.hc_add_current_frame_to_names:
        scene = bpy.context.scene
        tree = scene.node_tree
        node = next(
            (node for node in tree.nodes if node.type == "OUTPUT_FILE"),
            None
        )
        directory_path = node.base_path
        # Rename and replace files
        existing_files = []
        existing_files.clear()
        existing_files = list(os.listdir(directory_path))

        file_sub_path = list(node.inputs)
        for existing_name, save_name in itertools.product(existing_files, file_sub_path):
            save_name_with_ext = f"{save_name.name}.{node.format.file_format.lower()}"
            if save_name.name in existing_name and existing_name != save_name_with_ext:
                os.replace(
                    os.path.join(directory_path, existing_name),
                    os.path.join(directory_path, save_name_with_ext)
                )


def _move_frame_named_renders(self, context):
    scene = context.scene
    wm = context.window_manager
    gbh_hair_card = wm.gbh_hair_card

    output_name = gbh_hair_card.hc_output_name
    if output_name == "":
        output_name = "Texture"

    tree = scene.node_tree
    node = next(
        (node for node in tree.nodes if node.type == "OUTPUT_FILE"),
        None
    )
    directory_path = node.base_path
    # Rename and replace files
    existing_files = []
    existing_files.clear()
    existing_files = list(os.listdir(directory_path))

    file_sub_path = list(node.inputs)

    destination = os.path.join(directory_path, f"{output_name}_Frames/")

    for existing_name, save_name in itertools.product(existing_files, file_sub_path,):
        extension = node.format.file_format.lower()
        save_name_with_ext = f"{save_name.name}.{extension}"
        if save_name.name in existing_name and existing_name != save_name_with_ext:
            file_destination = destination + existing_name
            file = os.path.join(directory_path, existing_name)
            if not os.path.exists(destination):
                os.makedirs(destination)

            # Move render if already doesn't exists
            if not os.path.isfile(file_destination):
                shutil.move(file, file_destination)

            # Rename then move render if already exists
            else:
                name, ext = os.path.splitext(existing_name)
                i = 1
                dest_filename = os.path.join(
                    destination,
                    f"{name} - Copy ({i}){ext}"
                )

                while os.path.isfile(dest_filename):
                    i += 1
                    dest_filename = os.path.join(
                        destination,
                        f"{name} - Copy ({i}){ext}"
                    )

                shutil.move(file, dest_filename)


"""
---------------------------------------------------------------------
Operators
---------------------------------------------------------------------
"""


class GBH_OT_create_hc_scene(Operator):
    bl_idname = "gbh.create_hc_scene"
    bl_label = "Create Texturing Scene"
    bl_description = "Create hair card texturing scene"

    def execute(self, context):
        scene = context.scene
        wm = context.window_manager
        gbh_hair_card = wm.gbh_hair_card

        # Create hair card texturing scene
        item_name = f"{HC_TEXTURING_NAME} Texturing"
        item_type = "SCENE"
        scene = cf.create_new_item(context, scene, item_name, item_type)

        # Create new world
        item_name = f"{HC_TEXTURING_NAME} World"
        item_type = "WORLD"
        cf.create_new_item(context, scene, item_name, item_type)

        # Set render resolution for hair card texturing scene
        resolution_x = int(gbh_hair_card.hc_resolution)
        resolution_y = int(gbh_hair_card.hc_resolution)
        _set_render_resolution(scene, resolution_x, resolution_y)

        # Create new sun light
        item_name = f"{HC_TEXTURING_NAME} Sun Light"
        item_type = "SUN_LIGHT"
        sun_light = cf.create_new_item(context, scene, item_name, item_type)
        location = (0, 0, 10)
        cf.set_object_location(sun_light, location)

        # Create new camera
        item_name = f"{HC_TEXTURING_NAME} Camera"
        item_type = "CAMERA"
        camera = cf.create_new_item(context, scene, item_name, item_type)
        location = (0, 0, 2)
        cf.set_object_location(camera, location)
        x = math.radians(0)
        y = math.radians(0)
        z = math.radians(-90)
        rotation = x, y, z
        cf.set_object_rotation(camera, rotation)

        # Set scene camera and background transparency then change to camera view
        scene.camera = camera
        context.scene.render.film_transparent = True
        bpy.ops.view3d.view_camera()

        # Set recommended render passes
        passes = [
            "use_pass_diffuse_color",
            "use_pass_glossy_color",
            "use_pass_ambient_occlusion",
        ]
        view_layer = context.view_layer
        _set_render_passes(view_layer, passes)

        # Set up compositor nodes
        rl_node, fo_node = _create_compositor_nodes(context)
        _connect_compositor_nodes(context, rl_node, fo_node)

        gbh_hair_card.hc_add_current_frame_to_names = False

        return {"FINISHED"}


class GBH_OT_delete_hc_scene(Operator):
    bl_idname = "gbh.delete_hc_scene"
    bl_label = "Delete Texturing Scene"
    bl_description = "Delete hair card texturing scene"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        wm = context.window_manager
        gbh_hair_card = wm.gbh_hair_card

        scene = bpy.data.scenes.get(f"{HC_TEXTURING_NAME} Texturing")
        camera = bpy.data.cameras.get(f"{HC_TEXTURING_NAME} Camera")
        light = bpy.data.lights.get(f"{HC_TEXTURING_NAME} Sun Light")
        world = bpy.data.worlds.get(f"{HC_TEXTURING_NAME} World")

        items_to_delete = [
            scene,
            camera,
            light,
            world,
        ]
        for item in items_to_delete:
            cf.delete_item(item)

        gbh_hair_card.hc_add_current_frame_to_names = True

        return {"FINISHED"}


class GBH_OT_add_hc_object(Operator):
    bl_idname = "gbh.add_hc_object"
    bl_label = "Add Empty Curve"
    bl_description = "Add empty curve object to scene"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        scene = context.scene
        wm = context.window_manager
        gbh_hair_card = wm.gbh_hair_card
        hc_object_name = gbh_hair_card.hc_object_name

        item_name = hc_object_name if hc_object_name != "" else "Hair Object"
        # Create new empty curve
        item_type = "CURVE"
        cf.create_new_item(context, scene, item_name, item_type)

        return {"FINISHED"}


class GBH_OT_mod_hc_object(Operator):
    bl_idname = "gbh.mod_hc_object"
    bl_label = "Modify Hair Object"
    bl_description = "Sets the add-on's hair object to selected object"
    bl_options = {"REGISTER", "UNDO"}

    hair_object: StringProperty(
        name="Hair Object",
    )

    def execute(self, context):
        obj = context.scene.objects[self.hair_object]
        scene = context.scene
        scene.hair_object = obj

        return {"FINISHED"}


class GBH_OT_remove_hc_object(Operator):
    bl_idname = "gbh.remove_hc_object"
    bl_label = "Remove Hair Object"
    bl_description = "Remove selected hair object from file"
    bl_options = {"REGISTER", "UNDO"}

    hair_object: StringProperty(
        name="Hair Object",
    )

    def execute(self, context):
        obj = context.scene.objects[self.hair_object]
        cf.delete_item(obj.data)

        return {"FINISHED"}


class GBH_OT_select_hc_object(Operator):
    bl_idname = "gbh.select_hc_object"
    bl_label = "Select Hair Object"
    bl_description = "Select hair object in the viewport"
    bl_options = {"REGISTER", "UNDO"}

    hair_object: StringProperty(
        name="Hair Object",
    )

    def execute(self, context):
        obj = context.scene.objects[self.hair_object]
        cf.set_active_object(context, obj)

        return {"FINISHED"}


class GBH_OT_set_passes(Operator):
    bl_idname = "gbh.set_passes"
    bl_label = "Add and Rename Render Passes"
    bl_description = "Add and rename all selected passes to render"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        # Set up compositor nodes
        rl_node, fo_node = _create_compositor_nodes(context)
        _connect_compositor_nodes(context, rl_node, fo_node)

        return {"FINISHED"}


class GBH_OT_render(Operator):
    bl_idname = "gbh.render"
    bl_label = "Render Hair to Textures"

    def execute(self, context):
        wm = context.window_manager
        gbh_hair_card = wm.gbh_hair_card
        pref = context.preferences.addons[const.GBH_PACKAGE].preferences
        scene = context.scene
        tree = scene.node_tree
        node = next(
            (node for node in tree.nodes if node.type == "OUTPUT_FILE"),
            None
        )
        directory_path = node.base_path
        if not cf.directory_check(directory_path):
            err = const.INVALID_PATH
            self.report({"ERROR"}, err)
            return {"CANCELLED"}

        if pref.hc_auto_add_pass:
            # Set up compositor nodes
            rl_node, fo_node = _create_compositor_nodes(context)
            _connect_compositor_nodes(context, rl_node, fo_node)

        if not gbh_hair_card.hc_add_current_frame_to_names:
            _move_frame_named_renders(self, context)

        bpy.ops.render.render("INVOKE_DEFAULT")

        return {"FINISHED"}


class GBH_OT_reload_textures(Operator):
    bl_idname = "gbh.reload_textures"
    bl_label = "Reload Texture Files in Materials"

    def execute(self, context):
        for image in bpy.data.images:
            image.reload()

        area = next(
            area for area in context.screen.areas if area.type == "VIEW_3D"
        )

        space = next(
            space for space in area.spaces if space.type == "VIEW_3D"
        )

        if space.shading.type == "RENDERED":
            space.shading.type = "SOLID"
            space.shading.type = "RENDERED"

        return {"FINISHED"}


classes = (
    GBH_OT_create_hc_scene,
    GBH_OT_delete_hc_scene,
    GBH_OT_add_hc_object,
    GBH_OT_mod_hc_object,
    GBH_OT_remove_hc_object,
    GBH_OT_select_hc_object,
    GBH_OT_set_passes,
    GBH_OT_render,
    GBH_OT_reload_textures,
)


def register():
    from bpy.utils import register_class
    for cls in classes:
        register_class(cls)


def unregister():
    from bpy.utils import unregister_class
    for cls in reversed(classes):
        unregister_class(cls)

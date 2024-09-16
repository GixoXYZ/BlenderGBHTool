# SPDX-License-Identifier: GPL-2.0-or-later

import bpy
from bpy.types import Panel

from ..global_variables import GBH_PACKAGE
from . common_ui import GBHBasePanel, box_sub_panel


class VIEW3D_PT_hair_card_ui_main(Panel, GBHBasePanel):
    bl_label = "Hair Card Texture Creation"
    bl_idname = "VIEW3D_PT_hair_card_ui_main"
    bl_options = {"DEFAULT_CLOSED"}

    @classmethod
    def poll(cls, context):
        wm = context.window_manager
        gbh_panels = wm.gbh_panels
        pref = context.preferences.addons[GBH_PACKAGE].preferences
        return pref.panel_hair_cards_switch and gbh_panels.panel_hair_cards_switch

    def draw_header(self, context):
        self.layout.label(text="", icon="TEXTURE")

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        wm = context.window_manager

        body = layout.box()

        if not bpy.data.scenes.get("Hair Card Texturing"):
            gbh_hair_card = wm.gbh_hair_card
            row = body.row()
            row.operator("gbh.create_hc_scene")
            row.scale_x = 0.5
            row.prop(gbh_hair_card, "hc_resolution", text="")

        elif bpy.data.scenes.get("Hair Card Texturing"):
            self._scene_selection(context, body)
            delete = body.column()
            delete.alert = True
            delete.operator("gbh.delete_hc_scene", icon="PANEL_CLOSE")
            body.operator("gbh.reload_textures", icon="FILE_REFRESH")

            if scene.name == "Hair Card Texturing":
                self._hair_object(context, layout)
                self._camera_settings(context, layout)
                self._output_settings(context, layout)

    def _scene_selection(self, context, layout):
        window = context.window
        # Active workspace view layer is retrieved through window, not through workspace.
        layout.template_ID(
            window,
            "scene",
            new="scene.new",
            unlink="scene.delete"
        )

    def _hair_object(self, context, layout):
        scene = context.scene
        scene_objects = scene.objects
        wm = context.window_manager
        gbh_hair_card = wm.gbh_hair_card

        title = "Hair Objects"
        sub_panel = box_sub_panel(
            layout,
            "OBJECT_DATA",
            title,
            gbh_hair_card,
            "hc_objects_toggle",
            False
        )
        if sub_panel[0]:
            body = sub_panel[2]
            new_object = body.box()
            name = new_object.row()
            name.label(text="New Curve Name")
            name.prop(gbh_hair_card, "hc_object_name", text="")
            new_object.operator("gbh.add_hc_object", icon="ADD")

            hair_objects_list = []

            hair_types = ["CURVE", "CURVES"]
            for obj in scene_objects:
                if obj.type in hair_types:
                    hair_objects_list.append(obj)

            if len(hair_objects_list) <= 0:
                return

            list_box = body.box()
            for obj in hair_objects_list:
                if obj.type == "CURVE":
                    icon = "OUTLINER_OB_CURVE"
                elif obj.type == "CURVES":
                    icon = "OUTLINER_OB_CURVES"

                text = obj.name

                row = list_box.row(align=True)
                row.label(text=text, icon=icon)

                buttons = row.row(align=True)
                buttons.scale_x = 0.6

                buttons.operator(
                    "gbh.mod_hc_object",
                    text="Modify"
                ).hair_object = obj.name
                row.operator(
                    "gbh.select_hc_object",
                    text="",
                    icon="RESTRICT_SELECT_OFF"
                ).hair_object = obj.name
                row.prop(obj, "hide_render", text="")
                row.prop(obj, "hide_viewport", text="")

                delete = row.row()
                delete.separator()
                delete.operator(
                    "gbh.remove_hc_object",
                    text="",
                    icon="PANEL_CLOSE"
                ).hair_object = obj.name

    def _camera_settings(self, context, layout):
        scene_camera = context.scene.camera
        wm = context.window_manager
        gbh_hair_card = wm.gbh_hair_card
        title = "Camera"
        sub_panel = box_sub_panel(
            layout,
            "VIEW_CAMERA",
            title,
            gbh_hair_card,
            "hc_camera_toggle",
            False
        )
        if sub_panel[0]:
            body = sub_panel[2]
            if not scene_camera:
                col = body.column()
                col.label(text="No camera is found.")
                return

            col = body.column(align=True)
            scene_camera = context.scene.camera
            camera = bpy.data.cameras[scene_camera.data.name]
            col.prop(scene_camera, "location", text="Location")
            body.prop(camera, "type")

            col = body.column()
            col.separator()
            if camera.type == "PERSP":
                if camera.lens_unit == "MILLIMETERS":
                    col.prop(camera, "lens")
                elif camera.lens_unit == "FOV":
                    col.prop(camera, "angle")
                col.prop(camera, "lens_unit")

            elif camera.type == "ORTHO":
                col.prop(camera, "ortho_scale")

            elif camera.type == "PANO":
                engine = context.engine
                if engine == "CYCLES":
                    ccam = camera.cycles
                    col.prop(ccam, "panorama_type")
                    if ccam.panorama_type == "FISHEYE_EQUIDISTANT":
                        col.prop(ccam, "fisheye_fov")
                    elif ccam.panorama_type == "FISHEYE_EQUISOLID":
                        col.prop(ccam, "fisheye_lens", text="Lens")
                        col.prop(ccam, "fisheye_fov")
                    elif ccam.panorama_type == "EQUIRECTANGULAR":
                        sub = col.column(align=True)
                        sub.prop(ccam, "latitude_min", text="Latitude Min")
                        sub.prop(ccam, "latitude_max", text="Max")
                        sub = col.column(align=True)
                        sub.prop(ccam, "longitude_min", text="Longitude Min")
                        sub.prop(ccam, "longitude_max", text="Max")
                    elif ccam.panorama_type == "FISHEYE_LENS_POLYNOMIAL":
                        col.prop(ccam, "fisheye_fov")
                        col.prop(ccam, "fisheye_polynomial_k0", text="K0")
                        col.prop(ccam, "fisheye_polynomial_k1", text="K1")
                        col.prop(ccam, "fisheye_polynomial_k2", text="K2")
                        col.prop(ccam, "fisheye_polynomial_k3", text="K3")
                        col.prop(ccam, "fisheye_polynomial_k4", text="K4")

                elif engine in {"BLENDER_RENDER", "BLENDER_EEVEE", "BLENDER_EEVEE_NEXT", "BLENDER_WORKBENCH", "BLENDER_WORKBENCH_NEXT"}:
                    if camera.lens_unit == "MILLIMETERS":
                        col.prop(camera, "lens")
                    elif camera.lens_unit == "FOV":
                        col.prop(camera, "angle")
                    col.prop(camera, "lens_unit")

    def _output_settings(self, context, layout):
        rd = context.scene.render
        wm = context.window_manager
        gbh_hair_card = wm.gbh_hair_card
        pref = context.preferences.addons[GBH_PACKAGE].preferences
        scene = context.scene
        tree = scene.node_tree
        node = next(
            (node for node in tree.nodes if node.type == "OUTPUT_FILE"),
            None
        )
        title = "Output"
        sub_panel = box_sub_panel(
            layout,
            "OUTPUT",
            title,
            gbh_hair_card,
            "hc_output_toggle",
            False
        )
        if sub_panel[0]:
            body = sub_panel[2]
            box = body.box()
            col = box.column()
            row = col.row()
            row.label(text="Textures Output Name")
            row.prop(gbh_hair_card, "hc_output_name", text="")
            col.prop(gbh_hair_card, "hc_add_current_frame_to_names")
            if gbh_hair_card.hc_add_current_frame_to_names:
                col.prop(pref, "hc_frame_digits")

            col = box.column()
            col.enabled = bool(node.base_path != "")
            col.operator("gbh.render", icon="RENDER_STILL")
            col.scale_y = 1.5
            if node.base_path == "":
                col = box.column()
                col.label(text="Render output base path is not valid", icon="INFO")

            col = box.column()
            col.operator(
                "gbh.open_folder",
                text="Open Textures Folder",
                icon="TEXTURE"
            ).path = node.base_path

            view_layer = context.view_layer

            box = body.box()
            box.label(text="Texture Output Passes")
            split = box.split()

            if scene.render.engine == "CYCLES":
                cycles_view_layer = view_layer.cycles

                col = split.column(heading="Include", align=True)
                col.prop(view_layer, "use_pass_combined")
                col.prop(view_layer, "use_pass_z")
                col.prop(view_layer, "use_pass_mist")
                col.prop(view_layer, "use_pass_position")
                col.prop(view_layer, "use_pass_normal")
                sub = col.column()
                sub.active = not rd.use_motion_blur
                sub.prop(view_layer, "use_pass_vector")
                col.prop(view_layer, "use_pass_uv")

                col.prop(
                    cycles_view_layer,
                    "denoising_store_passes",
                    text="Denoising Data"
                )

                col = split.column(heading="Diffuse", align=True)
                col.prop(view_layer, "use_pass_diffuse_direct", text="Direct")
                col.prop(view_layer, "use_pass_diffuse_indirect", text="Indirect")
                col.prop(view_layer, "use_pass_diffuse_color", text="Color")

                col = col.column(heading="Glossy", align=True)
                col.prop(view_layer, "use_pass_glossy_direct", text="Direct")
                col.prop(view_layer, "use_pass_glossy_indirect", text="Indirect")
                col.prop(view_layer, "use_pass_glossy_color", text="Color")

                col = split.column(heading="Transmission", align=True)
                col.prop(view_layer, "use_pass_transmission_direct", text="Direct")
                col.prop(view_layer, "use_pass_transmission_indirect",
                         text="Indirect")
                col.prop(view_layer, "use_pass_transmission_color", text="Color")

                col = col.column(heading="Other", align=True)
                col.prop(view_layer, "use_pass_emit", text="Emission")
                col.prop(view_layer, "use_pass_environment", text="Environment")
                col.prop(
                    view_layer,
                    "use_pass_ambient_occlusion",
                    text="AO"
                )
                col.prop(cycles_view_layer, "use_pass_shadow_catcher")

            elif scene.render.engine == "BLENDER_EEVEE":
                col = split.column(heading="Data", align=True)
                col.prop(view_layer, "use_pass_combined")
                col.prop(view_layer, "use_pass_z")
                col.prop(view_layer, "use_pass_mist")
                col.prop(view_layer, "use_pass_normal")

                col = split.column(heading="Diffuse", align=True)
                col.prop(view_layer, "use_pass_diffuse_direct", text="Light")
                col.prop(view_layer, "use_pass_diffuse_color", text="Color")

                col = col.column(heading="Specular", align=True)
                col.prop(view_layer, "use_pass_glossy_direct", text="Light")
                col.prop(view_layer, "use_pass_glossy_color", text="Color")

                col = split.column(heading="Other", align=True)
                col.prop(view_layer, "use_pass_emit", text="Emission")
                col.prop(view_layer, "use_pass_environment", text="Environment")
                col.prop(view_layer, "use_pass_shadow", text="Shadow")
                col.prop(view_layer, "use_pass_ambient_occlusion", text="AO")

            col = box.column()
            col.prop(pref, "hc_auto_add_pass", toggle=True)
            if not pref.hc_auto_add_pass:
                col.operator("gbh.set_passes", icon="CHECKMARK")

            box = body.box()
            col = box.column(align=True)
            col.label(text="Render Resolution")
            col.prop(rd, "resolution_x", text="Resolution Width")
            col.prop(rd, "resolution_y", text="Resolution Height")
            col = box.column()
            col.prop(rd, "resolution_percentage", text="Resolution Scale (%)")
            col.prop(rd, "film_transparent", text="Transparent Background")

            world = context.scene.world
            if not world.use_nodes:
                col.prop(world, "color", text="World Color")

            # Set "node" context pointer for the panel layout.
            box.context_pointer_set("node", node)

            if hasattr(node, "draw_buttons_ext"):
                node.draw_buttons_ext(context, box)

    def _lighting_settings(self, context):
        pass

    def _hdri_settings(self, context):
        pass


classes = (
    VIEW3D_PT_hair_card_ui_main,
)


def register():
    from bpy.utils import register_class
    for cls in classes:
        register_class(cls)


def unregister():
    from bpy.utils import unregister_class
    for cls in reversed(classes):
        unregister_class(cls)

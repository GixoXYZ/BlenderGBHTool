# SPDX-License-Identifier: GPL-2.0-or-later

from bpy.types import Panel

from ..global_variables import GBH_PACKAGE
from . common_ui import GBHBasePanel, box_sub_panel, clear_pointer_if_object_deleted


class VIEW3D_PT_convert_ui_main(Panel, GBHBasePanel):
    bl_label = "Convert Hair"
    bl_idname = "VIEW3D_PT_convert_ui_main"
    bl_options = {"DEFAULT_CLOSED"}

    @classmethod
    def poll(cls, context):
        wm = context.window_manager
        gbh_panels = wm.gbh_panels
        pref = context.preferences.addons[GBH_PACKAGE].preferences
        return pref.panel_convert_switch and gbh_panels.panel_convert_switch

    def draw_header(self, context):
        self.layout.label(text="", icon="UV_SYNC_SELECT")

    def draw(self, context):
        scene = context.scene
        layout = self.layout

        if scene.hair_object:
            self._convert_to_mesh(layout, context)
            self._convert_to_curve(layout, context)
            self._convert_to_curves(layout, context)

        self._attach_curves_to_surface(layout, context)
        self._convert_particle_to_curves(layout, context)
        self._convert_to_particle_system(layout, context)

    def _convert_to_mesh(self, layout, context):
        wm = context.window_manager
        gbh_convert = wm.gbh_convert

        title = "Convert to Mesh"
        sub_panel = box_sub_panel(
            layout,
            "MESH_DATA",
            title,
            gbh_convert,
            "convert_mesh",
            False
        )
        if sub_panel[0]:
            body = sub_panel[2]
            row = body.row()
            row.operator(
                "gbh.convert_hair",
                icon="EXPORT",
                text="Convert Modified Hair to Mesh"
            ).convert_to = "MESH"

    def _convert_to_curve(self, layout, context):
        wm = context.window_manager
        gbh_convert = wm.gbh_convert

        title = "Convert to Curve"
        sub_panel = box_sub_panel(
            layout,
            "CURVE_DATA",
            title,
            gbh_convert,
            "convert_curve",
            False
        )
        if sub_panel[0]:
            body = sub_panel[2]
            row = body.row()
            row.operator(
                "gbh.convert_hair",
                icon="EXPORT",
                text="Convert Modified Hair to Curve"
            ).convert_to = "CURVE"
            row = body.row()
            row.prop(gbh_convert, "convert_curve_res_switch",)
            row = body.row()
            row.enabled = gbh_convert.convert_curve_res_switch
            row.prop(gbh_convert, "convert_curve_res", )

    def _convert_to_curves(self, layout, context):
        wm = context.window_manager
        gbh_convert = wm.gbh_convert

        title = "Convert to Hair Curves"
        sub_panel = box_sub_panel(
            layout,
            "CURVES_DATA",
            title,
            gbh_convert,
            "convert_curves",
            False
        )
        if sub_panel[0]:
            body = sub_panel[2]
            row = body.row()
            row.operator(
                "gbh.convert_hair",
                icon="EXPORT",
                text="Convert Modified Hair to Curves"
            ).convert_to = "CURVES"
            row = body.row()
            row.prop(gbh_convert, "convert_curves_res_switch")
            row = body.row()
            row.enabled = gbh_convert.convert_curves_res_switch
            row.prop(gbh_convert, "convert_curves_res")

    def _attach_curves_to_surface(self, layout, context):
        wm = context.window_manager
        gbh_convert = wm.gbh_convert
        obj = context.object

        title = "Attach Hair Curves to Surface"
        sub_panel = box_sub_panel(
            layout,
            "CURVES_DATA",
            title, gbh_convert,
            "attach_curves_to_surface",
            False,
        )
        if sub_panel[0]:
            body = sub_panel[2]
            if not obj:
                self._select_hair_curves(body)
                return
            if obj.type != "CURVES":
                self._select_hair_curves(body)
                return

            # Select parent object.
            body.prop(obj.data, "surface", text="Parent Object")
            # Select parent's UV map.
            has_surface = obj.data.surface is not None
            if has_surface:
                body.prop_search(
                    obj.data,
                    "surface_uv_map",
                    obj.data.surface.data,
                    "uv_layers",
                    text="Parent's UV Map"
                )
            else:
                row = body.row()
                row.prop(obj.data, "surface_uv_map", text="Parent's UV Map")
                row.enabled = has_surface

            row = body.row()
            row.enabled = obj.data.surface is not None and obj.data.surface_uv_map != ""
            row.operator("gbh.attach_curves_to_surface", icon="EXPORT")

    def _convert_particle_to_curves(self, layout, context):
        wm = context.window_manager
        gbh_convert = wm.gbh_convert

        title = "Convert Particle System to Hair Curves"
        sub_panel = box_sub_panel(
            layout,
            "PARTICLES",
            title, gbh_convert,
            "convert_particle_to_curves",
            False
        )
        if sub_panel[0]:
            body = sub_panel[2]
            col = body.column()
            col.label(text="Object to Convert Particles from")
            clear_pointer_if_object_deleted(
                context,
                gbh_convert,
                "particle_parent_object"
            )
            col.prop(gbh_convert, "particle_parent_object", text="")
            if gbh_convert.particle_parent_object:
                row = col.row()
                row.label(text="Converted Hair Name")
                row.prop(gbh_convert, "particle_to_curve_name", text="")
                col.operator("gbh.particle_to_strand", icon="EXPORT")

    def _convert_to_particle_system(self, layout, context):
        wm = context.window_manager
        gbh_convert = wm.gbh_convert
        obj = context.object

        title = "Convert to Particle System (Deprecated)"
        sub_panel = box_sub_panel(
            layout,
            "PARTICLES",
            title,
            gbh_convert,
            "convert_particle",
            False
        )
        if sub_panel[0]:
            body = sub_panel[2]
            if not obj:
                self._select_hair_curves(body)
                return

            if obj.type != "CURVES":
                self._select_hair_curves(body)
                return

            # Select parent object.
            body.prop(obj.data, "surface", text="Parent Object")
            # Select parent's UV map.
            has_surface = obj.data.surface is not None
            if has_surface:
                body.prop_search(
                    obj.data,
                    "surface_uv_map",
                    obj.data.surface.data,
                    "uv_layers",
                    text="Parent's UV Map"
                )
            else:
                row = body.row()
                row.prop(obj.data, "surface_uv_map", text="Parent's UV Map")
                row.enabled = has_surface
            row = body.row()
            row.enabled = obj.data.surface is not None
            row.operator("gbh.strands_to_particle", icon="EXPORT")

            # Warnings.
            row = body.row()
            row.label(
                text="Selected hair in the viewport gets converted.",
                icon="INFO"
            )
            row = body.row()
            row.label(
                text="Modifiers are not applied in this method.",
                icon="INFO"
            )
            row = body.row()
            row.label(
                text="Using dense and hi-res curves could result in unexpected behavior.",
                icon="INFO"
            )
            row = body.row(align=True)
            row.label(
                text="Hair dynamics for particles might work unexpectedly.",
                icon="INFO"
            )

    def _select_hair_curves(self, body):
        row = body.row(align=True)
        row.label(
            text="Please select a hair curves object in the viewport.",
            icon="INFO"
        )


classes = (
    VIEW3D_PT_convert_ui_main,
)


def register():
    from bpy.utils import register_class
    for cls in classes:
        register_class(cls)


def unregister():
    from bpy.utils import unregister_class
    for cls in reversed(classes):
        unregister_class(cls)

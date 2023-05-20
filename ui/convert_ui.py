# SPDX-License-Identifier: GPL-2.0-or-later

from bpy.types import Panel

from .. constants import GBH_PACKAGE
from . common_ui import GBHBasePanel
from . import convert_ui_modules as modules


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
            modules.convert_to_mesh(layout, context)
            modules.convert_to_curve(layout, context)
            modules.convert_to_curves(layout, context)

        modules.attach_curves_to_surface(layout, context)
        modules.convert_particle_to_curves(layout, context)
        modules.convert_to_particle_system(layout, context)


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

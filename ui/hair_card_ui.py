# SPDX-License-Identifier: GPL-2.0-or-later

import bpy
from bpy.types import Panel

from ..global_variables import GBH_PACKAGE
from . common_ui import GBHBasePanel
from . import hair_card_modules as modules


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
        gbh_hair_card = wm.gbh_hair_card

        body = layout.box()

        if not bpy.data.scenes.get("Hair Card Texturing"):
            row = body.row()
            row.operator("gbh.create_hc_scene")
            row.scale_x = 0.5
            row.prop(gbh_hair_card, "hc_resolution", text="")

        elif bpy.data.scenes.get("Hair Card Texturing"):
            modules.scene_selection(context, body)
            delete = body.column()
            delete.alert = True
            delete.operator("gbh.delete_hc_scene", icon="PANEL_CLOSE")
            body.operator("gbh.reload_textures", icon="FILE_REFRESH")

            if scene.name == "Hair Card Texturing":
                modules.hair_object(context, layout)
                modules.camera_settings(context, layout)
                modules.output_settings(context, layout)


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

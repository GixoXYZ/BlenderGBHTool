# SPDX-License-Identifier: GPL-2.0-or-later

from bpy.types import Panel

from . import landing_ui_modules as modules
from . common_ui import GBHBasePanel, box_sub_panel


class VIEW3D_PT_landing_ui_main(Panel, GBHBasePanel):
    bl_label = "Hair"

    def draw_header(self, context):
        self.layout.label(text="", icon="OUTLINER_OB_CURVES")

    def draw(self, context):
        layout = self.layout
        wm = context.window_manager
        gbh_presets = wm.gbh_presets
        gbh_mods = wm.gbh_mods
        box = layout.box()
        modules.ui_hair_object(context, box)

        title = "Presets"
        sub_panel = box_sub_panel(
            layout,
            "PRESET",
            title,
            gbh_presets,
            "presets_header_toggle",
            False
        )
        if sub_panel[0]:
            body = sub_panel[2]
            modules.ui_hair_presets(context, body)

        title = "Copy Modifiers and Node Groups"
        sub_panel = box_sub_panel(
            layout,
            "COPY_ID",
            title,
            gbh_mods,
            "mod_copy_toggle",
            False
        )
        if sub_panel[0]:
            body = sub_panel[2]
            modules.ui_mod_copy(context, body)


classes = (
    VIEW3D_PT_landing_ui_main,
)


def register():
    from bpy.utils import register_class
    for cls in classes:
        register_class(cls)


def unregister():
    from bpy.utils import unregister_class
    for cls in reversed(classes):
        unregister_class(cls)

# SPDX-License-Identifier: GPL-2.0-or-later

import contextlib
from bpy.types import Panel

from . import node_groups_ui_modules as modules
from . common_ui import GBHBasePanel
from .. constants import LIST_ROWS


class VIEW3D_PT_ng_ui_main(Panel, GBHBasePanel):
    bl_label = "Hair Modifications"

    @classmethod
    def poll(cls, context):
        scene = context.scene
        return scene.hair_object

    def draw_header(self, context):
        self.layout.label(text="", icon="MODIFIER")

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        obj = scene.hair_object

        box = layout.box()
        row = box.row()
        row.template_list(
            "OBJECT_UL_ng_list",
            "",
            obj,
            "modifiers",
            obj,
            "selected_mod_index",
            rows=LIST_ROWS
        )

        modules.ng_manage(context, box)

        if mod_list := list(obj.modifiers):
            with contextlib.suppress(IndexError, AttributeError):
                mod = mod_list[obj.selected_mod_index]
                modules.ng_stack(context, layout,  mod)


classes = (
    VIEW3D_PT_ng_ui_main,
)


def register():
    from bpy.utils import register_class
    for cls in classes:
        register_class(cls)


def unregister():
    from bpy.utils import unregister_class
    for cls in reversed(classes):
        unregister_class(cls)

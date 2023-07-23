# SPDX-License-Identifier: GPL-2.0-or-later

import bpy
from bpy.types import Operator
from bpy.props import StringProperty, BoolProperty

from .. import global_variables as gv

addon_keymaps = []


def add_hotkey():
    pref = bpy.context.preferences.addons[gv.GBH_PACKAGE].preferences
    wm = bpy.context.window_manager
    kc = wm.keyconfigs.addon

    if not kc:
        print("Keymap Error")
        return

    km = kc.keymaps.new(name="Object Mode", space_type="EMPTY")
    # Adding "Alt" + "Space" as pie menu hotkey
    kmi = km.keymap_items.new(
        GBH_OT_PIE_panel_toggle_call.bl_idname, pref.shortcut_key, "PRESS", alt=pref.shortcut_alt, shift=pref.shortcut_shift, ctrl=pref.shortcut_ctrl)
    addon_keymaps.append((km, kmi))


def remove_hotkey():
    for km, kmi in addon_keymaps:
        km.keymap_items.remove(kmi)

    addon_keymaps.clear()


class GBH_OT_panel_focus(Operator):
    bl_idname = "gbh.panel_focus"
    bl_label = "Toggle Panel"
    bl_description = "Toggle selected panel"

    panel_id: StringProperty(name="Panel ID")

    def execute(self, context):
        wm = context.window_manager
        gbh_panels = wm.gbh_panels

        toggles = [
            "panel_update_switch",
            "panel_rig_switch",
            "panel_convert_switch",
            "panel_lib_switch",
            "panel_hair_cards_switch",
            "panel_info_switch",
        ]

        for toggle in toggles:
            if toggle != self.panel_id:
                setattr(gbh_panels, toggle, False)

            else:
                setattr(gbh_panels, toggle, True)

        context.area.tag_redraw()
        return {"FINISHED"}


class GBH_OT_panel_unfocus(Operator):
    bl_idname = "gbh.panel_unfocus"
    bl_label = "Toggle Panel"
    bl_description = "Show all panels"

    def execute(self, context):
        wm = context.window_manager
        gbh_panels = wm.gbh_panels

        toggles = [
            "panel_update_switch",
            "panel_rig_switch",
            "panel_convert_switch",
            "panel_lib_switch",
            "panel_hair_cards_switch",
            "panel_info_switch",
        ]

        for toggle in toggles:
            setattr(gbh_panels, toggle, True)

        context.area.tag_redraw()
        return {"FINISHED"}


class GBH_OT_PIE_panel_toggle_call(Operator):
    bl_idname = "gbh.panel_toggle_call"
    bl_label = "GBH Pie Menu Caller"
    bl_description = "Call panel toggle pie menu"

    def execute(self, context):
        bpy.ops.wm.call_menu_pie(name="VIEW3D_MT_PIE_gbh_panel_toggle")
        return {"FINISHED"}


classes = (
    GBH_OT_panel_focus,
    GBH_OT_panel_unfocus,
    GBH_OT_PIE_panel_toggle_call,
)


def register():
    from bpy.utils import register_class
    for cls in classes:
        register_class(cls)

    add_hotkey()


def unregister():
    from bpy.utils import unregister_class
    for cls in reversed(classes):
        unregister_class(cls)

    remove_hotkey()

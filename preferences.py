# SPDX-License-Identifier: GPL-2.0-or-later

import bpy
import os
from bpy.types import AddonPreferences
from bpy.props import (
    StringProperty,
    BoolProperty,
    IntProperty,
    EnumProperty,
)

from . icons import load_icons
from . import global_variables as gv
from . operators.ui_ops import add_hotkey, remove_hotkey


def _update_icons(self, context):
    load_icons()


def _update_channel(self, context):
    self.update_available = False


def _lib_item_per_page_update(self, context):
    wm = context.window_manager
    gbh_lib = wm.gbh_lib
    gbh_lib.lib_page_index = 0


def update_shortcut(self, context):
    remove_hotkey()
    add_hotkey()


class GBHPreferences(AddonPreferences):
    bl_idname = __package__
    scriptdir = bpy.path.abspath(os.path.dirname(__file__))

    automatic_update_check: BoolProperty(
        name="Automatic Update Check",
        default=True,
    )
    update_latest_version: StringProperty()
    last_update_check: StringProperty(default="Never")
    update_available: BoolProperty(
        default=False,
    )
    preview_update: BoolProperty(
        name="Include Preview Updates",
        default=True,
    )
    update_check_interval: EnumProperty(
        name="Update Check Interval",
        items=[
            ("24", "Daily", ""),
            ("168", "Weekly", ""),
            ("336", "Biweekly", ""),
            ("720", "Monthly", ""),
        ],
        default="168"
    )
    panel_update_switch: BoolProperty(
        name="Update Panel Toggle",
        default=True,
    )
    panel_rig_switch: BoolProperty(
        name="Rigging Panel Toggle",
        default=True,
    )
    panel_convert_switch: BoolProperty(
        name="Convert Panel Toggle",
        default=True,
    )
    panel_lib_switch: BoolProperty(
        name="Library Panel Toggle",
        default=True,
    )
    panel_hair_cards_switch: BoolProperty(
        name="Hair Cards Panel Toggle",
        default=True,
    )
    panel_info_switch: BoolProperty(
        name="Info Panel Toggle",
        default=True,
    )
    lib_user_folder: StringProperty(
        name="User's Assets Folder",
        subtype="DIR_PATH",
        description="Select personal files directory",
    )
    lib_item_per_page: IntProperty(
        name="Library Items Per Page",
        default=4,
        min=3,
        max=20,
        update=_lib_item_per_page_update,
    )
    lib_scale: EnumProperty(
        name="Library Icons Scale",
        items=[
            ("3", "Small", ""),
            ("5", "Medium", ""),
            ("8", "Large", ""),
        ],
        default="3"
    )
    lib_list_view: BoolProperty(
        name="Library View Mode",
        default=True,
    )
    lib_add_to_active_object: BoolProperty(
        name="Add Node Groups to Active Object",
        description="Add node groups to active objects in viewport instead of adding them only to hair object",
        default=True,
    )
    icon_color: EnumProperty(
        items=[
            ("white", "White", "", 2),
            ("black", "Black", "", 1),
        ],
        name="Icons Color",
        default="white",
        update=_update_icons,
    )
    hc_auto_add_pass: BoolProperty(
        name="Add and Rename Render Passes on Render",
        default=True,
    )
    hc_frame_digits: IntProperty(
        name="Number of Frame Digits in Suffix",
        description="Number of frame digits added to rendered file name",
        default=2,
        min=1,
        max=10,
    )
    shortcut_key: EnumProperty(
        items=(
            ("NONE", "Select key", ""),
            ("LEFTMOUSE", "LEFTMOUSE", ""),
            ("MIDDLEMOUSE", "MIDDLEMOUSE", ""),
            ("RIGHTMOUSE", "RIGHTMOUSE", ""),
            ("BUTTON4MOUSE", "BUTTON4MOUSE", ""),
            ("BUTTON5MOUSE", "BUTTON5MOUSE", ""),
            ("BUTTON6MOUSE", "BUTTON6MOUSE", ""),
            ("BUTTON7MOUSE", "BUTTON7MOUSE", ""),
            ("MOUSEMOVE", "MOUSEMOVE", ""),
            ("INBETWEEN_MOUSEMOVE", "INBETWEEN_MOUSEMOVE", ""),
            ("TRACKPADPAN", "TRACKPADPAN", ""),
            ("TRACKPADZOOM", "TRACKPADZOOM", ""),
            ("MOUSEROTATE", "MOUSEROTATE", ""),
            ("WHEELUPMOUSE", "WHEELUPMOUSE", ""),
            ("WHEELDOWNMOUSE", "WHEELDOWNMOUSE", ""),
            ("WHEELINMOUSE", "WHEELINMOUSE", ""),
            ("WHEELOUTMOUSE", "WHEELOUTMOUSE", ""),
            ("A", "A", ""),
            ("B", "B", ""),
            ("C", "C", ""),
            ("D", "D", ""),
            ("E", "E", ""),
            ("F", "F", ""),
            ("G", "G", ""),
            ("H", "H", ""),
            ("I", "I", ""),
            ("J", "J", ""),
            ("K", "K", ""),
            ("L", "L", ""),
            ("M", "M", ""),
            ("N", "N", ""),
            ("O", "O", ""),
            ("P", "P", ""),
            ("Q", "Q", ""),
            ("R", "R", ""),
            ("S", "S", ""),
            ("T", "T", ""),
            ("U", "U", ""),
            ("V", "V", ""),
            ("W", "W", ""),
            ("X", "X", ""),
            ("Y", "Y", ""),
            ("Z", "Z", ""),
            ("ZERO", "ZERO", ""),
            ("ONE", "ONE", ""),
            ("TWO", "TWO", ""),
            ("THREE", "THREE", ""),
            ("FOUR", "FOUR", ""),
            ("FIVE", "FIVE", ""),
            ("SIX", "SIX", ""),
            ("SEVEN", "SEVEN", ""),
            ("EIGHT", "EIGHT", ""),
            ("NINE", "NINE", ""),
            ("LEFT_CTRL", "LEFT_CTRL", ""),
            ("LEFT_ALT", "LEFT_ALT", ""),
            ("LEFT_SHIFT", "LEFT_SHIFT", ""),
            ("RIGHT_ALT", "RIGHT_ALT", ""),
            ("RIGHT_CTRL", "RIGHT_CTRL", ""),
            ("RIGHT_SHIFT", "RIGHT_SHIFT", ""),
            ("OSKEY", "OSKEY", ""),
            ("GRLESS", "GRLESS", ""),
            ("ESC", "ESC", ""),
            ("TAB", "TAB", ""),
            ("RET", "RET", ""),
            ("SPACE", "SPACE", ""),
            ("LINE_FEED", "LINE_FEED", ""),
            ("BACK_SPACE", "BACK_SPACE", ""),
            ("DEL", "DEL", ""),
            ("SEMI_COLON", "SEMI_COLON", ""),
            ("PERIOD", "PERIOD", ""),
            ("COMMA", "COMMA", ""),
            ("QUOTE", "QUOTE", ""),
            ("ACCENT_GRAVE", "ACCENT_GRAVE", ""),
            ("MINUS", "MINUS", ""),
            ("SLASH", "SLASH", ""),
            ("BACK_SLASH", "BACK_SLASH", ""),
            ("EQUAL", "EQUAL", ""),
            ("LEFT_BRACKET", "LEFT_BRACKET", ""),
            ("RIGHT_BRACKET", "RIGHT_BRACKET", ""),
            ("LEFT_ARROW", "LEFT_ARROW", ""),
            ("DOWN_ARROW", "DOWN_ARROW", ""),
            ("RIGHT_ARROW", "RIGHT_ARROW", ""),
            ("UP_ARROW", "UP_ARROW", ""),
            ("NUMPAD_1", "NUMPAD_1", ""),
            ("NUMPAD_2", "NUMPAD_2", ""),
            ("NUMPAD_3", "NUMPAD_3", ""),
            ("NUMPAD_4", "NUMPAD_4", ""),
            ("NUMPAD_5", "NUMPAD_5", ""),
            ("NUMPAD_6", "NUMPAD_6", ""),
            ("NUMPAD_7", "NUMPAD_7", ""),
            ("NUMPAD_8", "NUMPAD_8", ""),
            ("NUMPAD_9", "NUMPAD_9", ""),
            ("NUMPAD_0", "NUMPAD_0", ""),
            ("NUMPAD_PERIOD", "NUMPAD_PERIOD", ""),
            ("NUMPAD_SLASH", "NUMPAD_SLASH", ""),
            ("NUMPAD_ASTERIX", "NUMPAD_ASTERIX", ""),
            ("NUMPAD_MINUS", "NUMPAD_MINUS", ""),
            ("NUMPAD_ENTER", "NUMPAD_ENTER", ""),
            ("NUMPAD_PLUS", "NUMPAD_PLUS", ""),
            ("F1", "F1", ""),
            ("F2", "F2", ""),
            ("F3", "F3", ""),
            ("F4", "F4", ""),
            ("F5", "F5", ""),
            ("F6", "F6", ""),
            ("F7", "F7", ""),
            ("F8", "F8", ""),
            ("F9", "F9", ""),
            ("F10", "F10", ""),
            ("F11", "F11", ""),
            ("F12", "F12", ""),
            ("F13", "F13", ""),
            ("F14", "F14", ""),
            ("F15", "F15", ""),
            ("F16", "F16", ""),
            ("F17", "F17", ""),
            ("F18", "F18", ""),
            ("F19", "F19", ""),
            ("PAUSE", "PAUSE", ""),
            ("INSERT", "INSERT", ""),
            ("HOME", "HOME", ""),
            ("PAGE_UP", "PAGE_UP", ""),
            ("PAGE_DOWN", "PAGE_DOWN", ""),
            ("END", "END", ""),
            ("MEDIA_PLAY", "MEDIA_PLAY", ""),
            ("MEDIA_STOP", "MEDIA_STOP", ""),
            ("MEDIA_FIRST", "MEDIA_FIRST", ""),
            ("MEDIA_LAST", "MEDIA_LAST", ""),
            ("TEXTINPUT", "TEXTINPUT", ""),
            ("WINDOW_DEACTIVATE", "WINDOW_DEACTIVATE", ""),
            ("TIMER", "TIMER", ""),
            ("TIMER0", "TIMER0", ""),
            ("TIMER1", "TIMER1", ""),
            ("TIMER2", "TIMER2", ""),
            ("TIMER_JOBS", "TIMER_JOBS", ""),
            ("TIMER_AUTOSAVE", "TIMER_AUTOSAVE", ""),
            ("TIMER_REPORT", "TIMER_REPORT", ""),
            ("TIMERREGION", "TIMERREGION", ""),
            ("NDOF_MOTION", "NDOF_MOTION", ""),
            ("NDOF_BUTTON_MENU", "NDOF_BUTTON_MENU", ""),
            ("NDOF_BUTTON_FIT", "NDOF_BUTTON_FIT", ""),
            ("NDOF_BUTTON_TOP", "NDOF_BUTTON_TOP", ""),
            ("NDOF_BUTTON_BOTTOM", "NDOF_BUTTON_BOTTOM", ""),
            ("NDOF_BUTTON_LEFT", "NDOF_BUTTON_LEFT", ""),
            ("NDOF_BUTTON_RIGHT", "NDOF_BUTTON_RIGHT", ""),
            ("NDOF_BUTTON_FRONT", "NDOF_BUTTON_FRONT", ""),
            ("NDOF_BUTTON_BACK", "NDOF_BUTTON_BACK", ""),
            ("NDOF_BUTTON_ISO1", "NDOF_BUTTON_ISO1", ""),
            ("NDOF_BUTTON_ISO2", "NDOF_BUTTON_ISO2", ""),
            ("NDOF_BUTTON_ROLL_CW", "NDOF_BUTTON_ROLL_CW", ""),
            ("NDOF_BUTTON_ROLL_CCW", "NDOF_BUTTON_ROLL_CCW", ""),
            ("NDOF_BUTTON_SPIN_CW", "NDOF_BUTTON_SPIN_CW", ""),
            ("NDOF_BUTTON_SPIN_CCW", "NDOF_BUTTON_SPIN_CCW", ""),
            ("NDOF_BUTTON_TILT_CW", "NDOF_BUTTON_TILT_CW", ""),
            ("NDOF_BUTTON_TILT_CCW", "NDOF_BUTTON_TILT_CCW", ""),
            ("NDOF_BUTTON_ROTATE", "NDOF_BUTTON_ROTATE", ""),
            ("NDOF_BUTTON_PANZOOM", "NDOF_BUTTON_PANZOOM", ""),
            ("NDOF_BUTTON_DOMINANT", "NDOF_BUTTON_DOMINANT", ""),
            ("NDOF_BUTTON_PLUS", "NDOF_BUTTON_PLUS", ""),
            ("NDOF_BUTTON_MINUS", "NDOF_BUTTON_MINUS", ""),
            ("NDOF_BUTTON_ESC", "NDOF_BUTTON_ESC", ""),
            ("NDOF_BUTTON_ALT", "NDOF_BUTTON_ALT", ""),
            ("NDOF_BUTTON_SHIFT", "NDOF_BUTTON_SHIFT", ""),
            ("NDOF_BUTTON_CTRL", "NDOF_BUTTON_CTRL", ""),
            ("NDOF_BUTTON_1", "NDOF_BUTTON_1", ""),
            ("NDOF_BUTTON_2", "NDOF_BUTTON_2", ""),
            ("NDOF_BUTTON_3", "NDOF_BUTTON_3", ""),
            ("NDOF_BUTTON_4", "NDOF_BUTTON_4", ""),
            ("NDOF_BUTTON_5", "NDOF_BUTTON_5", ""),
            ("NDOF_BUTTON_6", "NDOF_BUTTON_6", ""),
            ("NDOF_BUTTON_7", "NDOF_BUTTON_7", ""),
            ("NDOF_BUTTON_8", "NDOF_BUTTON_8", ""),
            ("NDOF_BUTTON_9", "NDOF_BUTTON_9", ""),
            ("NDOF_BUTTON_10", "NDOF_BUTTON_10", ""),
            ("NDOF_BUTTON_A", "NDOF_BUTTON_A", ""),
            ("NDOF_BUTTON_B", "NDOF_BUTTON_B", ""),
            ("NDOF_BUTTON_C", "NDOF_BUTTON_C", "")
        ),
        name="Key",
        description="Key",
        default="H",
        update=update_shortcut,
    )
    shortcut_alt: BoolProperty(
        name="Alt",
        default=False,
        update=update_shortcut,
    )
    shortcut_shift: BoolProperty(
        name="Shift",
        default=True,
        update=update_shortcut,
    )
    shortcut_ctrl: BoolProperty(
        name="Ctrl",
        default=True,
        update=update_shortcut,
    )

    def draw(self, context):
        layout = self.layout
        wm = bpy.context.window_manager
        gbh_update = wm.gbh_update

        box = layout.box()
        col = box.column()
        col.label(text="Add-on Updates:")
        row = col.row()
        row.scale_y = 1.3
        if gv.update_checking:
            row.enabled = False
            row.operator("gbh.update_check", icon="FILE_REFRESH", text="Checking for Updates...")

        elif self.update_available:
            row.operator(
                "gbh.update_check",
                text="",
                icon="FILE_REFRESH"
            )
            row.operator(
                "wm.url_open",
                icon="IMPORT",
                text=f"Download GBH Tool {self.update_latest_version}"
            ).url = gv.update_url

            sub_row = row.row()
            sub_row.scale_x = 0.6
            sub_row.operator(
                "wm.url_open",
                icon="INFO",
                text="Changelog"
            ).url = gv.update_info_url

        else:
            row.operator("gbh.update_check", icon="FILE_REFRESH")

        row.prop(self, "preview_update")
        row = col.row()
        row.prop(self, "automatic_update_check")
        row = row.row()
        row.enabled = self.automatic_update_check
        row.prop(self, "update_check_interval", text="")

        row = col.row()
        row.label(text=f"Lase Update Check: {self.last_update_check}")
        col = col.column()
        col.label(text=f"Last Update Check Report: {gbh_update.update_report}")

        box = layout.box()
        col = box.column()
        col.label(text="Toggle Panels:")
        panels = [
            "panel_update_switch",
            "panel_rig_switch",
            "panel_convert_switch",
            "panel_lib_switch",
            "panel_hair_cards_switch",
            "panel_info_switch"
        ]
        for panel in panels:
            col.prop(self, panel)

        col = box.column()
        col.label(text="Panel Toggle Pie Menu Shortcut:")
        row = col.row()
        row.prop(self, "shortcut_key")
        row = row.row()
        row.scale_x = 0.6
        row.prop(self, "shortcut_ctrl", toggle=True)
        row.prop(self, "shortcut_shift", toggle=True)
        row.prop(self, "shortcut_alt", toggle=True)

        box = layout.box()
        row = box.row()
        row.label(text="Library Settings:")
        row = box.row()
        row.label(text="Icons Color:")
        row.prop(self, "icon_color", text="")
        row = box.row()
        row.label(text="Library Items Per Page:")
        row.prop(self, "lib_item_per_page", text="")

        box = layout.box()
        split = box.split()
        split.label(text="Add-on's Installation Folder:")
        col = split.column()
        col.operator(
            "gbh.open_folder",
            text="Open Presets Folder",
            icon="PRESET"
        ).path = gv.DIR_PRESETS
        col.operator(
            "gbh.open_folder",
            text="Open Library Folder",
            icon="ASSET_MANAGER"
        ).path = gv.DIR_LIBRARY
        col.operator(
            "gbh.open_folder",
            text="Open Textures Folder",
            icon="TEXTURE"
        ).path = gv.DIR_TEXTURES


classes = (
    GBHPreferences,
)


def register():
    from bpy.utils import register_class
    for cls in classes:
        register_class(cls)


def unregister():
    from bpy.utils import unregister_class
    for cls in reversed(classes):
        unregister_class(cls)

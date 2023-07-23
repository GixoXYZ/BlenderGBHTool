# SPDX-License-Identifier: GPL-2.0-or-later

import bpy


def redraw_area_ui(area_type):
    for window in bpy.context.window_manager.windows:
        for area in window.screen.areas:
            if (area.type == area_type):
                area.tag_redraw()

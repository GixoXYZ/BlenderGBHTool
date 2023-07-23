# SPDX-License-Identifier: GPL-2.0-or-later

import os
import bpy
from bpy.utils import previews

from .global_variables import GBH_PACKAGE

_preview_collections = {}


def get_icons():
    return _preview_collections["library"]


def load_icons():
    # Remove the current icons and clear preview_collections
    for pcoll in _preview_collections.values():
        previews.remove(pcoll)

    _preview_collections.clear()
    # Load new icons
    pcoll = previews.new()
    pref = bpy.context.preferences.addons[GBH_PACKAGE].preferences
    color = pref.icon_color
    icons_dir = os.path.join(os.path.dirname(__file__), "icons", color)
    icons_dir_files = os.listdir(icons_dir)

    all_icon_files = [
        icon for icon in icons_dir_files if icon.endswith(".png")
    ]

    all_icon_names = [icon[:-4] for icon in all_icon_files]
    all_icon_files_and_names = zip(all_icon_names, all_icon_files)

    for icon_name, icon_file in all_icon_files_and_names:
        pcoll.load(icon_name, os.path.join(icons_dir, icon_file), "IMAGE")

    _preview_collections["library"] = pcoll


def register():
    load_icons()


def unregister():
    for pcoll in _preview_collections.values():
        previews.remove(pcoll)

    _preview_collections.clear()

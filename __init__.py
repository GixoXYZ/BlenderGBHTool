# SPDX-License-Identifier: GPL-2.0-or-later

# A portion of this program includes code from Antti Tikka's Modifier List Blender add-on released in April 1, 2022.
# Modifier List's code is used under the terms of the GNU General Public License v3.

import toml
import os

from . import global_variables as gv

if "bpy" in locals():
    import importlib
    importlib.reload(preferences)
    importlib.reload(properties)
    importlib.reload(icons)
    importlib.reload(library_ops)
    importlib.reload(rig_ops)
    importlib.reload(convert_ops)
    importlib.reload(common_ops)
    importlib.reload(node_groups_ops)
    importlib.reload(presets_ops)
    importlib.reload(hair_card_ops)
    importlib.reload(ui_ops)
    importlib.reload(info_ops)
    importlib.reload(update_ui)
    importlib.reload(landing_ui)
    importlib.reload(node_groups_ui)
    importlib.reload(library_ui)
    importlib.reload(hair_card_ui)
    importlib.reload(convert_ui)
    importlib.reload(rig_ui)
    importlib.reload(info_ui)
    importlib.reload(update_ops)
    importlib.reload(pie_ui)

else:
    from .ui import (
        hair_card_ui,
        info_ui,
        landing_ui,
        library_ui,
        convert_ui,
        node_groups_ui,
        rig_ui,
        update_ui,
        pie_ui,
    )
    from . operators import (
        hair_card_ops,
        library_ops,
        node_groups_ops,
        common_ops,
        presets_ops,
        rig_ops,
        convert_ops,
        update_ops,
        ui_ops,
        info_ops,
    )
    from . import (
        icons,
        preferences,
        properties,
    )


modules = [
    preferences,
    properties,
    icons,
    library_ops,
    rig_ops,
    convert_ops,
    common_ops,
    node_groups_ops,
    presets_ops,
    hair_card_ops,
    ui_ops,
    info_ops,
    update_ui,
    landing_ui,
    node_groups_ui,
    library_ui,
    hair_card_ui,
    convert_ui,
    rig_ui,
    info_ui,
    update_ops,
    pie_ui,
]


def register():
    script_dir = os.path.dirname(__file__)
    file_path = os.path.join(script_dir, "blender_manifest.toml")
    with open(file_path, "r") as file:
        manifest_data = toml.load(file)
        version = manifest_data["version"]
        gv.GBH_VERSION = [int(part) for part in version.split('.')]
    for module in modules:
        module.register()


def unregister():
    for module in reversed(modules):
        module.unregister()

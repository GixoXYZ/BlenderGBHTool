# SPDX-License-Identifier: GPL-2.0-or-later
# A minor portion of this program includes code from Antti Tikka's Modifier List Blender add-on released in April 1, 2022.
# Modifier List's code is used under the terms of the GNU General Public License v3.


# fmt: off
bl_info = {
    "name": "GBH Tool",
    "author": "Gixo <notgixo@proton.me>",
    "description": "Gixo's Blender Hair Tool generates different hair styles using Blender's new hair system.",
    "blender": (3, 5, 0),
    "version": (2, 1, 2, 1, "stable"),
    "location": "View3D > Toolshelf > GBH Tool",
    "warning": "",
    "support": "COMMUNITY",
    "category": "Object",
    "doc_url": "https://thegixo.github.io/GBHToolDocs/",
}

from . operators.update_ops import addon_info
# fmt: on

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
    importlib.reload(update_ui)
    importlib.reload(landing_ui_modules)
    importlib.reload(landing_ui)
    importlib.reload(node_groups_ui_modules)
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
        landing_ui_modules,
        landing_ui,
        library_ui,
        convert_ui,
        node_groups_ui_modules,
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
    update_ui,
    landing_ui_modules,
    landing_ui,
    node_groups_ui_modules,
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
    version = tuple(
        item for item in bl_info["version"] if not isinstance(item, str)
    )
    gbh_version = ".".join([str(x) for x in version])
    addon_info(gbh_version)
    for module in modules:
        module.register()


def unregister():
    for module in reversed(modules):
        module.unregister()

# SPDX-License-Identifier: GPL-2.0-or-later

from . common_ui import multi_line_text
from .. import constants as const


def update_version_info(context, layout):
    pref = context.preferences.addons[const.GBH_PACKAGE].preferences
    lv = pref.update_latest_version
    rt = pref.update_release_type
    bv = pref.update_blender_version

    box = layout.box()
    box.label(text="Update Info", icon="INFO")
    col = box.column()
    update_version = F"GBH Tool v{lv} {rt} is Available for Blender {bv} and later."
    multi_line_text(
        context=context,
        text=update_version,
        parent=col
    )


def update_message(context, layout):
    pref = context.preferences.addons[const.GBH_PACKAGE].preferences
    um = pref.update_message

    if um != "":
        box = layout.box()
        box.label(text="Update Message", icon="INFO")
        col = box.column()
        multi_line_text(
            context=context,
            text=um,
            parent=col)


def update_changelog(context, layout):
    pref = context.preferences.addons[const.GBH_PACKAGE].preferences

    if pref.update_changelog != "":
        box = layout.box()
        box.label(text="What's new", icon="SORTBYEXT")
        for change in eval(pref.update_changelog):
            row = box.row()
            row.label(text="", icon="DOT")
            col = row.column()
            multi_line_text(
                context=context,
                text=change,
                parent=col
            )


def update_download(context, layout):
    row = layout.row()
    row.operator(
        "wm.url_open",
        icon="IMPORT",
        text="Download"
    ).url = const.URL_GUMROAD

# SPDX-License-Identifier: GPL-2.0-or-later

from . common_ui import multi_line_text
from .. import global_variables as gv


def update_download(context, layout):
    pref = context.preferences.addons[gv.GBH_PACKAGE].preferences
    col = layout.column()
    col.operator(
        "wm.url_open",
        icon="IMPORT",
        text=f"Download GBH Tool {pref.update_latest_version}"
    ).url = gv.update_url
    col.operator(
        "wm.url_open",
        icon="INFO",
        text="Changelog"
    ).url = gv.update_info_url

# SPDX-License-Identifier: GPL-2.0-or-later

import bpy
import json
import requests
import datetime
import re
import threading
from bpy.types import Operator

from .. import global_variables as gv
from . import common_functions as cf

UPDATE_TIMEOUT = 20
DATE_TIME_FORMAT = "%Y-%m-%d %H:%M:%S"
UPDATE_INTERNET_FAIL = "Failed to connect to update server."
UPDATE_GET_FAIL = "Failed to retrieve updates."
UPDATE_NEW = "New update available."
UPDATE_NO_NEW = "No new updates available."
RELEASE_URL_LATEST = "https://api.github.com/repos/GixoXYZ/BlenderGBHTool/releases/latest"
RELEASE_URL_ALL = "https://api.github.com/repos/GixoXYZ/BlenderGBHTool/releases"


def check_for_updates():
    pref = bpy.context.preferences.addons[gv.GBH_PACKAGE].preferences
    wm = bpy.context.window_manager
    gbh_update = wm.gbh_update

    gv.update_checking = True
    if release_info := get_latest_release_info():
        if compare_versions(release_info["tag"], gv.GBH_VERSION):
            gv.update_url = release_info["url"]
            gv.update_info_url = release_info["info_url"]
            pref.update_available = True
            gbh_update.update_report = UPDATE_NEW
            pref.update_latest_version = release_info["tag"]

        else:
            pref.update_available = False
            gbh_update.update_report = UPDATE_NO_NEW

        pref.last_update_check = datetime.datetime.now().strftime(DATE_TIME_FORMAT)

    gv.update_checking = False
    cf.redraw_area_ui("PREFERENCES")
    cf.redraw_area_ui("VIEW_3D")


def compare_versions(latest_tag, gbh_version):
    # Convert latest tag to a list.
    online_version = re.findall(r"\d+|[A-Za-z]+", latest_tag)[1:]
    parsed_online_version = [int(match) if match.isdigit() else match for match in online_version]
    return parsed_online_version > gbh_version


def get_latest_release_info():
    pref = bpy.context.preferences.addons[gv.GBH_PACKAGE].preferences
    wm = bpy.context.window_manager
    gbh_update = wm.gbh_update

    try:
        url = RELEASE_URL_ALL if pref.preview_update else RELEASE_URL_LATEST
        response = requests.get(url, timeout=UPDATE_TIMEOUT)
        if response.status_code == 200:
            if releases := response.json():
                if pref.preview_update:
                    latest_release = releases[0]
                else:
                    latest_release = releases
                print(f"GBH Tool: Latest downloadable version is {latest_release['tag_name']}.")
                assets = latest_release["assets"]
                download_url = assets[0]["browser_download_url"]
                release_tag = latest_release["tag_name"]
                update_info_url = latest_release["html_url"]
                return {"tag": release_tag, "url": download_url, "info_url": update_info_url}
        else:
            gbh_update.update_report = f"{UPDATE_GET_FAIL} Status code: {response.status_code}"
            return None

    except (requests.exceptions.ConnectionError, requests.exceptions.RequestException) as err:
        print(f"GBH Tool: {err}")
        gbh_update.update_report = UPDATE_INTERNET_FAIL
        return None


def _has_time_elapsed():
    pref = bpy.context.preferences.addons[gv.GBH_PACKAGE].preferences
    if pref.last_update_check == "Never":
        return True

    now = datetime.datetime.now()
    last_check = datetime.datetime.strptime(
        pref.last_update_check,
        DATE_TIME_FORMAT
    )
    time_diff = now - last_check
    return time_diff.total_seconds() / 3600.0 > int(pref.update_check_interval)


class GBH_OT_update_check(Operator):
    bl_idname = "gbh.update_check"
    bl_label = "Check for Updates"
    bl_description = "Check for GBH Tool updates"

    def execute(self, context):
        gv.update_checking = True
        # Run update checker on a new thread.
        threading.Thread(target=check_for_updates).start()
        return {"FINISHED"}


classes = (
    GBH_OT_update_check,
)


def register():
    from bpy.utils import register_class
    for cls in classes:
        register_class(cls)

    pref = bpy.context.preferences.addons[gv.GBH_PACKAGE].preferences
    if compare_versions(pref.update_latest_version, gv.GBH_VERSION):
        pref.update_available = False

    has_time_elapsed = _has_time_elapsed()

    if pref.automatic_update_check and has_time_elapsed:
        # Run update checker on a new thread.
        threading.Thread(target=check_for_updates).start()


def unregister():
    from bpy.utils import unregister_class
    for cls in reversed(classes):
        unregister_class(cls)

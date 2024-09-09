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


def check_for_updates():
    pref = bpy.context.preferences.addons[gv.GBH_PACKAGE].preferences
    wm = bpy.context.window_manager
    gbh_update = wm.gbh_update

    gv.update_checking = True
    if release_info := get_latest_release_info():
        if compare_versions(release_info["tag"], gv.GBH_VERSION):
            gv.ULR_UPDATE = release_info["url"]
            gv.ULR_UPDATE_INFO = release_info["info_url"]
            pref.update_available = True
            gbh_update.update_report = UPDATE_NEW
            pref.update_latest_version = release_info["tag"]

        else:
            pref.update_available = False
            gbh_update.update_report = UPDATE_NO_NEW

        pref.last_update_check = datetime.datetime.now().strftime(DATE_TIME_FORMAT)

    cache_gh_branches()

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
        response = requests.get(gv.URL_RELEASE_LATEST, timeout=UPDATE_TIMEOUT)
        if response.status_code == 200:
            if releases := response.json():
                print(f"GBH Tool: Latest downloadable version is {releases['tag_name']}.")
                assets = releases["assets"]
                download_url = assets[0]["browser_download_url"]
                release_tag = releases["tag_name"]
                update_info_url = releases["html_url"]
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


def cache_gh_branches():
    wm = bpy.context.window_manager
    gbh_update = wm.gbh_update

    response = requests.get(gv.URL_BRANCHES)
    # Check if the request was successful
    if response.status_code == 200:
        branches = response.json()
        gv.branches_cache = [(branch["name"], branch["name"], "") for branch in branches]

        gv.branches_latest_commits.clear()
        for branch in branches:
            branch_name = branch["name"]
            commit_url = branch["commit"]["url"]

            # Fetch the latest commit info to get the date
            commit_response = requests.get(commit_url)

            if commit_response.status_code == 200:
                commit_data = commit_response.json()
                commit_date_str = commit_data["commit"]["committer"]["date"]
                commit_date = str(datetime.datetime.strptime(commit_date_str, "%Y-%m-%dT%H:%M:%SZ"))

                gv.branches_latest_commits[branch_name] = commit_date

    if hasattr(gbh_update, "update_branches"):
        gbh_update.update_latest_commit = gv.branches_latest_commits.get(gbh_update.update_branches, "Not Available")


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
    if not compare_versions(pref.update_latest_version, gv.GBH_VERSION):
        pref.update_available = False

    if pref.automatic_update_check:
        # Run update checker on a new thread.
        if _has_time_elapsed():
            threading.Thread(target=check_for_updates).start()
        else:
            threading.Thread(target=cache_gh_branches).start()


def unregister():
    from bpy.utils import unregister_class
    for cls in reversed(classes):
        unregister_class(cls)

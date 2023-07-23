# SPDX-License-Identifier: GPL-2.0-or-later

import bpy
import json
import requests
import datetime
import concurrent.futures
from bpy.types import Operator

from .. import global_variables as gv

UPDATE_INTERVAL = 24
UPDATE_TIMEOUT = 5
DATE_TIME_FORMAT = "%Y-%m-%d %H:%M:%S"
UPDATE_INTERNET_FAIL = "Failed to connect to update server."
UPDATE_CHECK_FAIL = "Failed to check for updates."
UPDATE_NEW = "New update available."
UPDATE_NO_NEW = "No new updates available."
UPDATE_CHANNEL_ERROR = "Selected update channel is not available."


def addon_info(gbh_version):
    global GBH_VERSION
    GBH_VERSION = gbh_version


def _version_compare(installed_v, update_v):
    return installed_v < update_v


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
    return time_diff.total_seconds() / 3600.0 > UPDATE_INTERVAL


def update_checker():
    pref = bpy.context.preferences.addons[gv.GBH_PACKAGE].preferences
    wm = bpy.context.window_manager
    gbh_update = wm.gbh_update

    try:
        res = requests.get(gv.URL_UPDATE, timeout=UPDATE_TIMEOUT)
        if not res.ok:
            gbh_update.update_report = UPDATE_INTERNET_FAIL
            return
        else:
            response = requests.get(gv.URL_UPDATE)

    except requests.exceptions.RequestException as err:
        print(err)
        gbh_update.update_report = UPDATE_INTERNET_FAIL
        return

    try:
        data = json.loads(response.text)

    except json.decoder.JSONDecodeError as err:
        print(err)
        gbh_update.update_report = UPDATE_CHECK_FAIL
        return

    if data.get(pref.update_channel):
        try:
            pref.update_latest_version = data[pref.update_channel]["version"]
            pref.update_release_type = data[pref.update_channel]["release_type"]
            pref.update_blender_version = data[pref.update_channel]["blender_version"]
            pref.update_message = data[pref.update_channel]["message"]
            pref.update_changelog = str(data[pref.update_channel]["changelog"])
            pref.last_update_check = datetime.datetime.now().strftime(DATE_TIME_FORMAT)

        except KeyError as err:
            print(err)
            gbh_update.update_report = UPDATE_CHECK_FAIL
            return

        installed_version = GBH_VERSION.split(".")
        latest_version = data[pref.update_channel]["version"].split(".")

        if _version_compare(installed_version, latest_version):
            pref.update_available = True
            gbh_update.update_report = UPDATE_NEW

        else:
            pref.update_available = False
            gbh_update.update_report = UPDATE_NO_NEW
            return

    elif not data.get(pref.update_channel):
        gbh_update.update_report = UPDATE_CHANNEL_ERROR
        return


class GBH_OT_update_check(Operator):
    bl_idname = "gbh.update_check"
    bl_label = "Check for Updates"
    bl_description = "Check for GBH Tool updates"

    def execute(self, context):
        # Run update checker on a new thread
        executor = concurrent.futures.ThreadPoolExecutor(max_workers=5)
        executor.submit(update_checker)
        return {"FINISHED"}


classes = (
    GBH_OT_update_check,
)


def register():
    from bpy.utils import register_class
    for cls in classes:
        register_class(cls)

    pref = bpy.context.preferences.addons[gv.GBH_PACKAGE].preferences
    if not _version_compare(GBH_VERSION.split("."), pref.update_latest_version.split(".")):
        pref.update_available = False

    has_time_elapsed = _has_time_elapsed()

    if pref.startup_update_check and has_time_elapsed:
        # Run update checker on a new thread
        executor = concurrent.futures.ThreadPoolExecutor(max_workers=5)
        executor.submit(update_checker)


def unregister():
    from bpy.utils import unregister_class
    for cls in reversed(classes):
        unregister_class(cls)

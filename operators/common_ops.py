# SPDX-License-Identifier: GPL-2.0-or-later

import bpy
import os
import platform
from bpy.types import Operator
from bpy.props import StringProperty

from ..global_variables import INVALID_PATH


class GBH_OT_open_folder(Operator):
    bl_idname = "gbh.open_folder"
    bl_label = "Open Folder"
    bl_description = "Open selected folder"

    path: StringProperty()

    def execute(self, context):
        path = self.path
        if not os.path.isdir(path):
            err = INVALID_PATH
            self.report({"ERROR"}, err)
            return

        if platform.system() == "Windows":
            try:
                os.startfile(path)

            except (FileNotFoundError, RuntimeError) as err:
                return self._show_error(self, err)

        else:
            try:
                os.system(f'xdg-open "{path}"')

            except (FileNotFoundError, RuntimeError) as err:
                return self._show_error(self, err)

        return {"FINISHED"}

    def _show_error(self, err):
        print(err)
        err = "An error occurred, please try opening the directory manually."
        self.report({"ERROR"}, err)

        return {"CANCELLED"}


class GBH_OT_testing(Operator):
    bl_idname = "gbh.testing"
    bl_label = "Test"
    bl_description = "Operator meant for testing purposes"

    def execute(self, context):

        return {"FINISHED"}


classes = (
    GBH_OT_open_folder,
    GBH_OT_testing,
)


def register():
    from bpy.utils import register_class
    for cls in classes:
        register_class(cls)


def unregister():
    from bpy.utils import unregister_class
    for cls in reversed(classes):
        unregister_class(cls)

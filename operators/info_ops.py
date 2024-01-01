# SPDX-License-Identifier: GPL-2.0-or-later

import bpy
import requests
import re
import threading
import time

from bpy.types import Operator
from bpy.props import StringProperty

from .. import global_variables as gv
from . import common_functions as cf

FETCH_TIMEOUT = 20


class GBH_OT_gh_issues(Operator):
    bl_idname = "gbh.gh_issues"
    bl_label = "Open a Github Issue"

    issue_type: StringProperty(
        default="",
    )

    def execute(self, context):
        if self.issue_type == "01--bug-report":
            gv.bug_template_fetching = True
        elif self.issue_type == "02--feature-request":
            gv.feat_template_fetching = True

        # Open github issue on a new thread.
        threading.Thread(target=self.open_github_issue, args=(self.issue_type,)).start()
        return {"FINISHED"}

    def open_github_issue(self, issue_type):
        def get_github_issues_template(template):
            template_url = f"https://raw.githubusercontent.com/GixoXYZ/BlenderGBHTool/main/.github/ISSUE_TEMPLATE/{template}"
            try:
                response = requests.get(template_url, timeout=FETCH_TIMEOUT)
                return response.text if response.status_code == 200 else None
            except (requests.exceptions.ConnectionError, requests.exceptions.RequestException) as err:
                print(f"GBH Tool: {err}")
                return None

        def extract_title_and_labels(template_content):
            title_match = re.search(r"title:\s*'(.+)'", template_content)
            labels_match = re.search(r"labels:\s*(.+)", template_content)
            assignees_match = re.search(r"assignees:\s*(.+)", template_content)

            title = title_match[1] if title_match else ""
            labels = labels_match[1] if labels_match else ""
            assignees = assignees_match[1] if assignees_match else ""

            return title, labels, assignees

        if issue_template := get_github_issues_template(
            f"{issue_type}.md"
        ):
            # Use the title, labels and assignees from selected GitHub issue template.
            title, labels, assignees = extract_title_and_labels(issue_template)

            body = ""
            if issue_type == "01--bug-report":
                os_type = bpy.app.build_platform.decode("utf-8")
                blender_version = bpy.app.version_string
                blender_branch = bpy.app.build_branch.decode("utf-8")
                blender_build_date = bpy.app.build_commit_date.decode("utf-8")
                blender_build_hash = bpy.app.build_hash.decode("utf-8")
                gbh_version = ".".join(map(str, gv.GBH_VERSION))

                front_matter_pattern = r"^---\n[\s\S]*?\n---\n"
                if match := re.search(front_matter_pattern, issue_template):
                    issue_template = issue_template[match.end():]

                strings_to_check = [
                    "[Please put your operating system info here.]",
                    "[Please put the version of Blender that the bug exists in, here.]",
                    "[Please put the version of GBH Tool that the bug exists in, here.]"
                ]

                if all(string in issue_template for string in strings_to_check):
                    # Add gathered system info to bug report body.
                    body = (
                        issue_template
                        .replace("[Please put your operating system info here.]", os_type)
                        .replace("[Please put the version of Blender that the bug exists in, here.]", f"version: {blender_version}, branch: {blender_branch}, commit date: {blender_build_date}, hash: {blender_build_hash}")
                        .replace("[Please put the version of GBH Tool that the bug exists in, here.]", f"version: {gbh_version}")
                    )

                    # Remove possible trailing new lines, and use double spaces for new lines.
                    body = body.rstrip("\n").replace("\n", "%0A")

                else:
                    body = (
                        f"**System Information**%0AOperating system: {os_type}%0A"
                        f"%0A**Blender Version**%0ABroken: version: {blender_version}, branch: {blender_branch}, commit date: {blender_build_date}, hash: {blender_build_hash}%0AWorked: [Please put the newest version of Blender that worked as expected here.]%0A"
                        f"%0A**GBH Tool Version**%0ABroken: version: {gbh_version}%0AWorked: [Please put the newest version of GBH Tool that worked as expected here.]%0A"
                        "%0A**Short description of error**%0A[Please fill out a short description of the error here.]%0A"
                        "%0A**Exact steps for others to reproduce the error**%0A[Please describe the exact steps needed to reproduce the issue.]%0A[Based on the default startup or an attached .blend file (as simple as possible).]%0A"
                        "%0A**Screenshots**%0A[If applicable, add screenshots to help explain your problem.]%0A"
                        "%0A**Additional context**%0A[Add any other context about the problem here.]"
                    )

            github_url = f"https://github.com/GixoXYZ/BlenderGBHTool/issues/new?template={issue_type}.md&assignees={assignees}&title={title}&labels={labels}&body={body}"
            bpy.ops.wm.url_open(url=github_url)
            gv.fetch_template_message = ""

        else:
            issue_name = (re.sub(r"\d+--", "", issue_type)).replace("-", " ")
            err = f"Failed to fetch {issue_name} template. Please check your internet connection."
            print(f"GBH Tool: {err}")
            gv.fetch_template_message = err
            cf.redraw_area_ui("VIEW_3D")
            time.sleep(10)
            gv.fetch_template_message = ""

        if issue_type == "01--bug-report":
            gv.bug_template_fetching = False
        elif issue_type == "02--feature-request":
            gv.feat_template_fetching = False
        cf.redraw_area_ui("VIEW_3D")


classes = (
    GBH_OT_gh_issues,
)


def register():
    from bpy.utils import register_class
    for cls in classes:
        register_class(cls)


def unregister():
    from bpy.utils import unregister_class
    for cls in reversed(classes):
        unregister_class(cls)

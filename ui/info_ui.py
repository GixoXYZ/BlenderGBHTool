# SPDX-License-Identifier: GPL-2.0-or-later

from bpy.types import Panel

from . common_ui import GBHBasePanel, box_sub_panel, multi_line_text
from .. icons import get_icons
from .. import global_variables as gv


class VIEW3D_PT_info_ui_main(Panel, GBHBasePanel):
    bl_label = "Info"
    bl_idname = "VIEW3D_PT_info_ui_main"
    bl_options = {"DEFAULT_CLOSED"}

    @classmethod
    def poll(cls, context):
        wm = context.window_manager
        gbh_panels = wm.gbh_panels
        pref = context.preferences.addons[gv.GBH_PACKAGE].preferences
        return pref.panel_info_switch and gbh_panels.panel_info_switch

    def draw_header(self, context):
        self.layout.label(text="", icon="INFO")

    def draw(self, context):
        layout = self.layout

        box = layout.box()
        col = box.column()
        col.label(text="Links")

        links = {
            "Docs": {"url": gv.URL_DOCS, "icon": "Docs"},
            "Contact": {"url": gv.URL_CONTACT, "icon": "Contact"},
            "Gumroad": {"url": gv.URL_GUMROAD, "icon": "Gumroad"},
            "Github": {"url": gv.URL_GITHUB, "icon": "Github"},
            "Questions and Discussions": {"url": gv.URL_DISCUSS, "icon": "Discuss"},
        }

        for key, button_data in links.items():
            self._info_button(
                context,
                col,
                key,
                button_data["icon"],
                button_data["url"]
            )

        pcoll = get_icons()
        icon = pcoll["Issue"].icon_id
        feat = col.column()
        if gv.feat_template_fetching:
            feat.enabled = False
            feat.operator("gbh.gh_issues", icon_value=icon, text="Fetching Feature Request Template...")
        else:
            feat.operator("gbh.gh_issues", icon_value=icon, text="Feature Request").issue_type = "02--feature-request"

        bug = col.column()
        if gv.bug_template_fetching:
            bug.enabled = False
            bug.operator("gbh.gh_issues", icon_value=icon, text="Fetching Bug Report Template...")
        else:
            bug.operator("gbh.gh_issues", icon_value=icon, text="Report a Bug").issue_type = "01--bug-report"

        if gv.fetch_template_message != "":
            col = box.column()
            col.label(text="An Error Occurred!", icon="ERROR")
            multi_line_text(
                context=context,
                text=gv.fetch_template_message,
                parent=box
            )

    def _info_button(self, context, layout, text, icon, url):
        pcoll = get_icons()
        icon = pcoll[icon].icon_id
        layout.operator("wm.url_open", icon_value=icon, text=text).url = url


classes = (
    VIEW3D_PT_info_ui_main,
)


def register():
    from bpy.utils import register_class
    for cls in classes:
        register_class(cls)


def unregister():
    from bpy.utils import unregister_class
    for cls in reversed(classes):
        unregister_class(cls)

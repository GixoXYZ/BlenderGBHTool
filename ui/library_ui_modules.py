# SPDX-License-Identifier: GPL-2.0-or-later

import bpy
import math

from .. icons import get_icons
from ..global_variables import GBH_PACKAGE
from .. operators import library_ops as lib_ops


def lib_settings_header(context, layout):
    pref = context.preferences.addons[GBH_PACKAGE].preferences
    row = layout.row()
    view = row.row()
    wm = context.window_manager
    gbh_lib = wm.gbh_lib

    view.alignment = "LEFT"
    if pref.lib_list_view:
        icon = "COLLAPSEMENU"

    if not pref.lib_list_view:
        icon = "SNAP_VERTEX"

    view.prop(pref, "lib_list_view", text="", icon=icon, emboss=False)
    view.prop(pref, "lib_scale", text="View Size")

    row = row.row()
    row.alignment = "RIGHT"

    row.operator("gbh.reload_library", text="", icon="FILE_REFRESH")
    row.prop(
        gbh_lib,
        "lib_settings_switch",
        text="",
        icon="PREFERENCES"
    )


def lib_settings_menu(context, layout):
    pref = context.preferences.addons[GBH_PACKAGE].preferences
    col = layout.column()
    col.prop(
        pref,
        "lib_add_to_active_object",
        text="Add Node Groups to Active Objects in Viewport",
        icon="OBJECT_DATA"
    )
    if bpy.data.use_autopack:
        col.active_default = True
    col.operator(
        "file.autopack_toggle",
        text="Automatically Pack Resources for This File",
        icon="PACKAGE"
    )

    col.separator()

    bcoll = lib_ops.get_blend_files()
    box = layout.box()
    col = box.column()
    col.label(text="Select Personal Directory")
    row = col.row()
    row.prop(pref, "lib_user_folder", text="")

    if not bcoll:
        row.scale_x = 0.5
        row.operator("gbh.open_user_lib", text="Open Directory")

    if bcoll:
        row.scale_x = 0.5
        row.operator("gbh.close_user_lib", text="Close Directory")

        col = box.column(align=True)
        for blend in bcoll:
            col.operator("gbh.open_user_file", text=blend).filename = blend


def lib_categories_and_search(layout):
    wm = bpy.context.window_manager
    gbh_lib = wm.gbh_lib
    box = layout.box()

    row = box.row()
    row.prop(gbh_lib, "lib_category", text="Category")

    if gbh_lib.lib_category == "GBH":
        row = box.row()
        row.prop(gbh_lib, "asset_category", expand=True)

    row = box.row(align=True)
    # row.label(text="Search")
    row.prop(gbh_lib, "lib_search", text="Search")


def lib_pages(layout):
    pref = bpy.context.preferences.addons[GBH_PACKAGE].preferences
    wm = bpy.context.window_manager
    gbh_lib = wm.gbh_lib

    if gbh_lib.asset_category == "MATERIALS":
        items = lib_ops.get_materials()

    elif gbh_lib.asset_category == "NODES":
        items = lib_ops.get_node_groups()
    total_items = len(items)
    if total_items % pref.lib_item_per_page == 0:
        total_page = math.floor(total_items/pref.lib_item_per_page)
    else:
        total_page = math.floor(total_items/pref.lib_item_per_page)+1

    box = layout.box()
    row = box.row(align=True)
    if total_items != 0:
        row.label(text=f"Total Items: {total_items}")
        row.label(text="Pages")
        left_sub_row = row.row(align=True)
        left_sub_row.enabled = gbh_lib.lib_page_index > 0
        left_sub_row.operator(
            "gbh.change_lib_page",
            text="",
            icon="TRIA_LEFT"
        ).page_index = gbh_lib.lib_page_index-1

        right_sub_row = row.row(align=True)
        right_sub_row.enabled = gbh_lib.lib_page_index < total_page-1
        right_sub_row.operator(
            "gbh.change_lib_page",
            text="",
            icon="TRIA_RIGHT"
        ).page_index = gbh_lib.lib_page_index+1

        pages_sub_row = box.grid_flow(
            even_columns=True, even_rows=True, row_major=True, align=True)
        for i in range(total_page):
            button = pages_sub_row.row(align=True)
            button.scale_x = 0.8
            if i == gbh_lib.lib_page_index:
                button.active_default = True
            button.operator(
                "gbh.change_lib_page",
                text=f"{i+1}"
            ).page_index = i

    else:
        row.label(text="Total Items: 0")


def lib_materials_grid(context, layout):
    pref = context.preferences.addons[GBH_PACKAGE].preferences
    wm = context.window_manager
    gbh_lib = wm.gbh_lib

    pcoll = get_icons()
    mcoll = lib_ops.get_materials()

    total_items = len(mcoll)
    if total_items % pref.lib_item_per_page == 0:
        total_page = math.floor(total_items/pref.lib_item_per_page)
        last_page_item = pref.lib_item_per_page
    else:
        total_page = math.floor(total_items/pref.lib_item_per_page)+1
        if gbh_lib.lib_page_index + 1 == total_page:
            last_page_item = total_items % pref.lib_item_per_page
        else:
            last_page_item = pref.lib_item_per_page

    if total_items != 0:
        current_page_index = gbh_lib.lib_page_index*pref.lib_item_per_page

        # Make a box for each node group found in library file
        for i in range(last_page_item):
            mat = mcoll[i+current_page_index]
            mat_name = mat[0]
            box = layout.box()
            icon = pcoll[mat_name] if mat_name in pcoll else pcoll["Material"]
            if pref.lib_list_view and pref.lib_scale == "8":
                factor = 0.4

            elif pref.lib_list_view and pref.lib_scale == "3":
                factor = 0.2

            else:
                factor = 0.3

            if pref.lib_list_view:
                list_split = box.split(factor=factor)
                thumbnail = list_split
                body = list_split

            if not pref.lib_list_view:
                thumbnail = box
                body = box

            thumbnail.template_icon(
                icon_value=icon.icon_id, scale=int(pref.lib_scale))

            col = body.column()
            if pref.lib_list_view:
                if pref.lib_scale == "3":
                    for _ in range(3):
                        col.separator()

                elif pref.lib_scale == "5":
                    for _ in range(7):
                        col.separator()

                elif pref.lib_scale == "8":
                    for _ in range(14):
                        col.separator()

            col.label(text=mat_name, icon="MATERIAL")

            row = col.row()
            if bpy.data.materials.get(mat_name):
                row.active_default = True
                row.operator(
                    "gbh.material_delete",
                    text="Delete"
                ).matname = str(mat)

            else:
                row.operator(
                    "gbh.material_append",
                    text="Import"
                ).matname = str(mat)


def lib_nodes_grid(context, layout):
    pref = context.preferences.addons[GBH_PACKAGE].preferences
    wm = context.window_manager
    gbh_lib = wm.gbh_lib

    ncoll = lib_ops.get_node_groups()
    pcoll = get_icons()

    total_items = len(ncoll)
    if total_items % pref.lib_item_per_page == 0:
        total_page = math.floor(total_items/pref.lib_item_per_page)
        last_page_item = pref.lib_item_per_page
    else:
        total_page = math.floor(total_items/pref.lib_item_per_page)+1
        if gbh_lib.lib_page_index + 1 == total_page:
            last_page_item = total_items % pref.lib_item_per_page
        else:
            last_page_item = pref.lib_item_per_page

    if total_items != 0:
        current_page_index = gbh_lib.lib_page_index*pref.lib_item_per_page

        # Make a box for each node group found in library file
        for i in range(last_page_item):
            ng = ncoll[i+current_page_index]
            ng_name = ng[0]
            box = layout.box()
            icon = pcoll[ng_name] if ng_name in pcoll else pcoll["Node Group"]
            if pref.lib_list_view and pref.lib_scale == "8":
                factor = 0.4

            elif pref.lib_list_view and pref.lib_scale == "3":
                factor = 0.2

            else:
                factor = 0.3

            if pref.lib_list_view:
                list_split = box.split(factor=factor)
                thumbnail = list_split
                body = list_split

            if not pref.lib_list_view:
                thumbnail = box
                body = box

            thumbnail.template_icon(
                icon_value=icon.icon_id, scale=int(pref.lib_scale))

            col = body.column()

            if pref.lib_list_view:
                if pref.lib_scale == "3":
                    for _ in range(3):
                        col.separator()

                elif pref.lib_scale == "5":
                    for _ in range(7):
                        col.separator()

                elif pref.lib_scale == "8":
                    for _ in range(14):
                        col.separator()

            col.label(text=ng_name, icon="NODETREE")

            row = col.row()
            if bpy.data.node_groups.get(ng_name):
                row.active_default = True
                row.operator(
                    "gbh.node_group_add_to_object",
                    text="Add to Object"
                ).nodename = str(ng)
                row.operator(
                    "gbh.node_group_delete", text="",
                    icon="PANEL_CLOSE"
                ).nodename = str(ng)

            else:
                row.operator(
                    "gbh.node_group_append",
                    text="Import"
                ).nodename = str(ng)

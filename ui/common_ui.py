# SPDX-License-Identifier: GPL-2.0-or-later

import textwrap


class GBHBasePanel:
    """Base panel"""
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "GBH Tool"


def box_sub_panel(layout, header_icon, label, source, prop, icon_value):
    """Create closable sub-panel box"""
    state = getattr(source, prop)
    main = layout.column(align=True)
    header = main.box()
    icon = "TRIA_DOWN" if state else "TRIA_RIGHT"
    row = header.row(align=True)
    row.alignment = "LEFT"
    row.prop(
        source,
        prop,
        text="",
        icon=icon,
        toggle=True,
        emboss=False
    )

    if icon_value:
        row.prop(
            source,
            prop,
            text=label,
            icon_value=header_icon.icon_id,
            toggle=True,
            emboss=False
        )

    else:
        row.prop(
            source,
            prop,
            text=label,
            icon=header_icon,
            toggle=True,
            emboss=False
        )

    if state:
        body = main.box()
        return state, header, body, main

    else:
        return state, header


def multi_line_text(context, text, parent):
    """Make texts distribution dynamically"""
    chars = int(context.region.width / 7)
    wrapper = textwrap.TextWrapper(width=chars)
    text_lines = wrapper.wrap(text=text)
    for text_line in text_lines:
        parent.label(text=text_line)


def clear_pointer_if_object_deleted(context, prop_parent, prop_pointer):
    if attr := getattr(prop_parent, prop_pointer):
        if not context.scene.objects.get(attr.name):
            prop_parent.property_unset(prop_pointer)

# SPDX-License-Identifier: GPL-2.0-or-later

from .. icons import get_icons
from . common_ui import box_sub_panel, multi_line_text


def info_button(context, layout, text, icon, url):
    pcoll = get_icons()
    icon = pcoll[icon].icon_id
    layout.operator("wm.url_open", icon_value=icon, text=text).url = url


def info_pitfalls(layout, context):
    wm = context.window_manager
    gbh_info = wm.gbh_info
    # UV info section
    title = "UV"
    sub_panel = box_sub_panel(
        layout,
        "UV_DATA",
        title,
        gbh_info,
        "info_uv",
        False
    )
    if sub_panel[0]:
        body = sub_panel[2]

        col = body.column()
        col.label(text="UV not working?", icon="INFO")
        box = body.box()
        text1 = '- To ensure that your material is set up correctly, make sure to include an "Attribute" node and assign the name "UVMap" to its value field. Once this is done, you can connect the vector pin output to your texture UV input.'
        multi_line_text(
            context=context,
            text=text1,
            parent=box
        )
        text2 = '- The cause of this issue may be the accidental deletion of the "UVMap" attribute in the output attributes of your geometry nodes. To resolve this, you can either manually enter the attribute yourself or simply delete the hair modification and start over to restore the missing attribute.'
        multi_line_text(
            context=context,
            text=text2,
            parent=box
        )

    # Mesh info section
    title = "Mesh"
    sub_panel = box_sub_panel(
        layout,
        "MESH_DATA",
        title,
        gbh_info,
        "info_mesh",
        False)
    if sub_panel[0]:
        body = sub_panel[2]

        col = body.column()
        col.label(text="Mesh to hair not working?", icon="INFO")
        box = body.box()
        text1 = '- When using the "Mesh to Hair" feature, the software uses edge crease values to determine the roots of the hair strands. To ensure that your hair strands have proper roots, you can add edge creases by entering edit mode and selecting the edges where the roots should be. Next, press "Shift + E" on your keyboard, and drag your mouse all the way up before left-clicking to create the crease. The edge should turn pink to confirm that the crease has been added. After this step, you can switch back to object mode and the "Mesh to Hair" feature should work as intended.'
        multi_line_text(
            context=context,
            text=text1,
            parent=box
        )

        col = body.column()
        col.label(text="Profiles not looking okay?", icon="INFO")
        box = body.box()
        text1 = '- Try to apply transform of the hair and parent object using "Ctrl + A" shortcut. Object rotation and scale can alter the behavior of the addon.'
        multi_line_text(
            context=context,
            text=text1,
            parent=box
        )

    # Particle system info section
    title = "Particle System"
    sub_panel = box_sub_panel(
        layout,
        "PARTICLES",
        title,
        gbh_info,
        "info_particle",
        False
    )
    if sub_panel[0]:
        body = sub_panel[2]

        col = body.column()
        col.label(
            text="Hair stretch after conversion to particle system and enabling hair dynamics?", icon="INFO")
        box = body.box()
        text1 = '- This could be caused by hair resolution being too high. Try using a lower res hair or reduce vertex mass in the particle system settings.'
        multi_line_text(
            context=context,
            text=text1,
            parent=box
        )

        col = body.column()
        col.label(
            text="Hair styles gets messed up with hair dynamics?", icon="INFO")
        box = body.box()
        text1 = "- I haven't find a solution for this problem so far. Hair simulation is planned to be added to Blender in the future and hopefully we'll be getting better results."
        multi_line_text(
            context=context,
            text=text1,
            parent=box
        )

    # Rendering info section
    title = "Rendering"
    sub_panel = box_sub_panel(
        layout,
        "RENDERLAYERS",
        title,
        gbh_info,
        "info_rendering",
        False
    )
    if sub_panel[0]:
        body = sub_panel[2]

        col = body.column()
        col.label(text="Black artifact when rendering hair cards?", icon="INFO")
        box = body.box()
        text1 = '- This is caused by insufficient light bounces for transparent objects. To fix this issue head to "Render Properties -> Light Paths -> Max Bounces" and then increase "Transparent" value.'
        multi_line_text(
            context=context,
            text=text1,
            parent=box
        )

    # Rig info section
    title = "Rig"
    sub_panel = box_sub_panel(
        layout,
        "GROUP_BONE",
        title,
        gbh_info,
        "info_rig",
        False
    )
    if sub_panel[0]:
        body = sub_panel[2]

        col = body.column()
        col.label(text="Automatic weight paint behaves unexpectedly?", icon="INFO")
        box = body.box()
        text1 = '- This is could be caused by flipped normals. Add "GBG Flip Faces" node group from the library to the hair object and things should start to behave as expected.'
        multi_line_text(
            context=context,
            text=text1,
            parent=box
        )

# SPDX-License-Identifier: GPL-2.0-or-later

import bpy
import contextlib
from bpy.types import Panel, UIList

from .. icons import get_icons

from . common_ui import GBHBasePanel, box_sub_panel
from ..global_variables import LIST_ROWS


class OBJECT_UL_ng_list(UIList):

    def draw_item(self, context, layout, data, item, active_data, active_propname, index):
        mod = item
        if self.layout_type in {"DEFAULT", "COMPACT"}:
            row = layout.row(align=True)
            row.prop(mod, "name", text="", emboss=False,
                     icon_value=layout.icon(mod))
            row.prop(mod, "show_viewport", text="", emboss=False)
            row.prop(mod, "show_render", text="", emboss=False)

        elif self.layout_type in {"GRID"}:
            layout.alignment = "CENTER"
            layout.label(text="", icon_value=layout.icon(mod))


class VIEW3D_PT_ng_ui_main(Panel, GBHBasePanel):
    bl_label = "Hair Modifications"

    @classmethod
    def poll(cls, context):
        scene = context.scene
        return scene.hair_object

    def draw_header(self, context):
        self.layout.label(text="", icon="MODIFIER")

    def draw(self, context):
        scene = context.scene
        if obj := scene.hair_object:
            layout = self.layout
            box = layout.box()
            row = box.row()
            row.template_list(
                "OBJECT_UL_ng_list",
                "",
                obj,
                "modifiers",
                obj,
                "selected_mod_index",
                rows=LIST_ROWS
            )

            self._ng_manage(context, box)

            if mod_list := list(obj.modifiers):
                with contextlib.suppress(IndexError, AttributeError):
                    mod = mod_list[obj.selected_mod_index]
                    self._ng_stack(context, layout, mod)

    def _ng_manage(self, context, layout):
        scene = context.scene
        obj = scene.hair_object
        mod_list = list(obj.modifiers)

        row = layout.row()
        delete = row.row()
        delete.alert = True
        delete.operator(
            "gbh.delete_all_mods",
            text="Delete All Modifiers"
        )
        row = row.row(align=True)
        row.alignment = "RIGHT"
        row.operator("gbh.modifier_new", icon="ADD", text="")
        sub_row = row.row(align=True)
        sub_row.enabled = len(mod_list) > 0
        sub_row.operator("gbh.remove_item", icon="REMOVE", text="")

        sub_row.separator()

        sub_row = row.row(align=True)
        sub_row.enabled = len(mod_list) > 1

        up_button = sub_row.row(align=True)
        up_button.enabled = obj.selected_mod_index > 0
        up_button.operator(
            "gbh.modifier_move",
            text="",
            icon="TRIA_UP"
        ).direction = "UP"

        down_button = sub_row.row(align=True)
        down_button.enabled = obj.selected_mod_index < len(mod_list) - 1
        down_button.operator(
            "gbh.modifier_move",
            text="",
            icon="TRIA_DOWN"
        ).direction = "DOWN"

    def _node_inputs(self, layout, ng):
        row = layout.row()
        row.template_ID(ng, "node_group", new="gbh.ng_new")

        row = layout.row()

        input_node = next(
            (node for node in ng.node_group.nodes if node.type == "GROUP_INPUT"), None
        )
        if not input_node:
            return

        valid_node_outputs_names = []
        node_output_types = []
        node_output_socket_shapes = []
        linked_inputs = []

        for node_output in input_node.outputs[:-1]:
            if node_output.type != "GEOMETRY":
                valid_node_outputs_names.append(node_output.name)
                node_output_types.append(node_output.type)
                node_output_socket_shapes.append(node_output.display_shape)

        input_nodes_list = [
            node for node in ng.node_group.nodes if node.type == "GROUP_INPUT"
        ]
        for input_node in input_nodes_list:
            linked_inputs.extend(
                socket.name
                for socket in input_node.outputs[:-1]
                if socket.is_linked == True
            )
        # input_prop_ids = [prop_id for prop_id in ng.keys() if (prop_id.startswith("Input_") and prop_id[-1].isdigit())]

        input_prop_ids = [prop_id for prop_id in ng.keys() if (prop_id[-1].isdigit())]

        input_identifiers_names_types_shapes = zip(
            input_prop_ids,
            valid_node_outputs_names,
            node_output_types,
            node_output_socket_shapes
        )

        datablock_input_info_per_type = {
            "COLLECTION": {"data_collection": "collections", "icon": "OUTLINER_COLLECTION"},
            "IMAGE": {"data_collection": "images", "icon": "IMAGE"},
            "MATERIAL": {"data_collection": "materials", "icon": "MATERIAL"},
            "OBJECT": {"data_collection": "objects", "icon": "OBJECT_DATA"},
            "TEXTURE": {"data_collection": "textures", "icon": "TEXTURE"},
        }

        for prop_id, name, input_type, socket_shape in input_identifiers_names_types_shapes:
            row = layout.row(align=True)
            if name not in linked_inputs and ng.node_group.nodes.get(name):
                row.label(text=name)
                col = layout.column()
                with contextlib.suppress(TypeError, IndexError, AttributeError):
                    col.template_curve_mapping(
                        ng.node_group.nodes.get(name),
                        "mapping"
                    )

                    col.template_color_ramp(
                        ng.node_group.nodes.get(name),
                        "color_ramp"
                    )
                    layout.separator()

            elif input_type in datablock_input_info_per_type:
                input_info = datablock_input_info_per_type[input_type]
                row.label(text=name)
                row.prop_search(
                    ng, f'["{prop_id}"]',
                    bpy.data, input_info["data_collection"],
                    text="",
                    icon=input_info["icon"]
                )

            elif input_type == "STRING":
                row.label(text=name)
                row.prop(ng, f'["{prop_id}"]', text="")

            else:
                with contextlib.suppress(IndexError, AttributeError):
                    if ng.get(f"{prop_id}_use_attribute"):
                        if ng[f"{prop_id}_use_attribute"] == 1:
                            row.label(text=name)
                            attr_prop_name = f'["{prop_id}_attribute_name"]'
                            row.prop(ng, attr_prop_name, text="")
                            op = row.operator(
                                "gbh.geometry_nodes_attr_search",
                                text="",
                                icon="VIEWZOOM"
                            )
                            op.property_name = attr_prop_name

                    else:
                        col = row.column()
                        col.prop(ng, f'["{prop_id}"]', text=name)

                    if socket_shape in {"DIAMOND", "DIAMOND_DOT"}:
                        sub_row = row.row()
                        op = sub_row.operator(
                            "gbh.input_attr_toggle",
                            text="",
                            icon="SPREADSHEET"
                        )
                        op.i = f"{prop_id}_use_attribute"

    def _node_outputs(self, layout, sub_panel, ng):
        valid_node_outputs_names = [
            output.name for output in ng.node_group.interface.items_tree
            if output.item_type == "SOCKET"
            if output.in_out == "OUTPUT" and output.socket_type != "NodeSocketGeometry"
        ]

        output_prop_ids = [prop_id for prop_id in ng.keys()if prop_id.endswith("attribute_name")]

        if not valid_node_outputs_names:
            return

        footer = sub_panel[3].box()
        footer.label(text="Outputs")
        for prop_id, name in zip(output_prop_ids, valid_node_outputs_names):
            with contextlib.suppress(IndexError, AttributeError):
                row = footer.row(align=True)
                row.label(text=name)
                row.prop(ng, f'["{prop_id}"]', text="")
                op = row.operator(
                    "gbh.geometry_nodes_attr_search",
                    text="",
                    icon="VIEWZOOM"
                )
                op.property_name = f'["{prop_id}"]'

    def _ng_stack(self, context, layout, mod):
        wm = context.window_manager
        gbh_mods = wm.gbh_mods
        pcoll = get_icons()
        if mod.name in pcoll:
            icon = pcoll[mod.name]
            use_icon_value = True

        else:
            icon = "MODIFIER"
            use_icon_value = False

        title = f"{mod.name} Controls"
        sub_panel = box_sub_panel(
            layout,
            icon,
            title,
            gbh_mods,
            "controls_header_toggle",
            use_icon_value
        )
        if sub_panel[0]:
            header = sub_panel[1]
            row = header.row(align=True)
            name = row.row(align=True)
            name.prop(mod, "name", text="", icon_value=header.icon(mod))
            apply = row.row(align=True)
            apply.scale_x = 0.5
            apply.operator("gbh.apply_item", text="Apply", icon="CHECKMARK")
            header.separator(factor=-1)
            body = sub_panel[2]

            if mod.type == "NODES":
                self._node_inputs(body, mod)
                self._node_outputs(body, sub_panel, mod)

            else:
                row = body.row(align=True)
                row.label(text='Select a "Geometry Nodes" modifier.')
                return


classes = (
    VIEW3D_PT_ng_ui_main,
    OBJECT_UL_ng_list,
)


def register():
    from bpy.utils import register_class
    for cls in classes:
        register_class(cls)


def unregister():
    from bpy.utils import unregister_class
    for cls in reversed(classes):
        unregister_class(cls)

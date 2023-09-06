# SPDX-License-Identifier: GPL-2.0-or-later

import bpy
from bpy.types import PropertyGroup
from bpy.props import (
    BoolProperty,
    IntProperty,
    FloatProperty,
    EnumProperty,
    PointerProperty,
    StringProperty,
    CollectionProperty,
)

from . operators.hair_card_ops import rename_renders
from . operators.presets_ops import refresh_presets_list
from . operators import library_ops as lib_ops


"""Hair object poll functions"""


def _hair_object_poll(self, obj):
    valid_obj_type = ["CURVE", "CURVES"]
    if obj.type in valid_obj_type and obj in list(bpy.context.scene.objects):
        return obj.type


"""Presets update functions"""


def _presets_hair_type_update(self, context):
    wm = context.window_manager
    gbh_presets = wm.gbh_presets
    gbh_presets.presets_list_index = 0
    refresh_presets_list(self, context)


"""Library update functions"""


def _lib_cat_update(self, context):
    wm = context.window_manager
    gbh_lib = wm.gbh_lib
    gbh_lib.property_unset("asset_category")

    lib_ops.load_library(self, context)


def _lib_asset_cat_update(self, context):
    lib_ops.load_library(self, context)


def _lib_search_update(self, context):
    lib_ops.lib_search()


"""Rig update functions"""


def _arm_update(self, context):
    wm = context.window_manager
    gbh_rig = wm.gbh_rig
    if gbh_rig.rig_live_preview:
        bpy.ops.gbh.hair_to_armature()


"""Hair Card update functions"""


def _render_complete_handler(self, context):
    if self.hc_add_current_frame_to_names:
        try:
            bpy.app.handlers.render_complete.remove(rename_renders)
            print("GBH Tool: Render rename handler removed.")

        except ValueError as err:
            print(f"GBH Tool: {err}")

    else:
        bpy.app.handlers.render_complete.append(rename_renders)
        print("GBH Tool: Render rename handler added.")


"""Mods functions"""


def _copy_from_object_poll(self, obj):
    hair_object = bpy.context.scene.hair_object
    valid_obj_type = ["CURVE", "CURVES"]
    if obj.type in valid_obj_type and obj in list(bpy.context.scene.objects) and obj != hair_object:
        return obj.type


"""Convert functions"""


def _particle_parent_object_poll(self, obj):
    valid_obj_type = ["MESH"]
    if obj.type in valid_obj_type and obj in list(bpy.context.scene.objects):
        return obj.type


"""
---------------------------------------------------------------------
Property Groups
---------------------------------------------------------------------
"""


class GBH_PresetsListProperties(PropertyGroup):
    """Dummy class to store presets lists"""

    pass


class GBH_PresetsProperties(PropertyGroup):
    """Presets property group"""

    presets_hair_type: EnumProperty(
        name="Hair Type",
        description="Hair type selection",
        items=[
            ("NONE", "None", ""),
            ("STRANDS", "Hair Strands", ""),
            ("CARDS", "Hair Cards", ""),
            ("STYLIZED", "Stylized Hair", ""),
            ("OBJECT", "Hair Objects", ""),
        ],
        update=_presets_hair_type_update,
    )
    presets_header_toggle: BoolProperty(
        name="Minimize/Maximize Presets",
        default=True,
    )
    presets_list_index: IntProperty(
        name="Presets List Index",
    )
    new_preset_name: StringProperty(
        name="New Preset's Name",
    )


class GBH_ModsProperties(PropertyGroup):
    """Modifiers property group"""

    controls_header_toggle: BoolProperty(
        name="Minimize/Maximize Controls",
        default=True,
    )
    mod_copy_toggle: BoolProperty(
        name="Minimize/Maximize Copy Modifiers",
        default=False,
    )
    mod_copy_object: PointerProperty(
        name="Object to Copy from",
        description="Hair object to copy modifiers from",
        type=bpy.types.Object,
        poll=_copy_from_object_poll,
    )


class GBH_LibraryProperties(PropertyGroup):
    """Library property group"""

    lib_category: EnumProperty(
        name="Category",
        description="Select library's category",
        items=[
            ("GBH", "GBH Assets", ""),
            ("BLENDER", "Blender Assets", ""),
            ("USER", "User Assets", ""),
        ],
        update=_lib_cat_update,
    )
    asset_category: EnumProperty(
        name="Assets Type",
        description="Select the asset type shown in library",
        items=[
            ("NODES", "Node Groups", "", 1),
            ("MATERIALS", "Materials", "", 2),
        ],
        update=_lib_asset_cat_update,
    )
    lib_page_index: IntProperty(
        name="Library Page Index",
        description="Select library page index",
        default=0,
    )
    lib_search: StringProperty(
        name="Library Search",
        description="Search for keywords in library",
        options={"TEXTEDIT_UPDATE"},
        default="",
        update=_lib_search_update
    )
    lib_settings_switch: BoolProperty(
        name="Library Settings",
        default=False,
    )
    lib_path: StringProperty(
        name="Library Path",
        default="",
    )


class GBH_RigProperties(PropertyGroup):
    """Rigging property group"""

    rig_armature_creation: BoolProperty(
        name="Minimize/Maximize Armature Creation",
        default=True,
    )
    rig_live_preview: BoolProperty(
        name="Live Preview",
        description="Show live preview of bones",
        default=True,
    )
    arm_res: IntProperty(
        name="Rig Resolution",
        description="Number of bones in each chain",
        min=2,
        soft_max=10,
        default=5,
        update=_arm_update,
    )
    arm_density: FloatProperty(
        name="Rig Density",
        description="Density of bones chains per hair curves",
        min=0,
        max=100,
        default=100,
        update=_arm_update,
    )
    arm_start: FloatProperty(
        name="Rig Start",
        description="Start of bone chains in relation to hair curves",
        min=0,
        max=100,
        default=0,
        update=_arm_update,
    )
    arm_end: FloatProperty(
        name="Rig End",
        description="End of bone chains in relation to hair curves",
        min=0,
        max=100,
        default=100,
        update=_arm_update,
    )
    arm_parent_size: FloatProperty(
        name="Armature Parent Bone Size (cm)",
        description="Size of added parent bone to the armature",
        min=5,
        max=100,
        default=25,
        update=_arm_update,
    )
    arm_reverse: BoolProperty(
        name="Reverse Chains Direction",
        description="Reverse bone chains direction",
        update=_arm_update,
    )
    arm_add_parent_bone: BoolProperty(
        name="Add Parent Bone",
        description="Add parent bone to armature",
        default=True,
        update=_arm_update,
    )
    arm_use_mods: BoolProperty(
        name="Use Object's Modifiers",
        description="Use object's modifiers to create armature from",
        default=False,
        update=_arm_update,
    )
    arm_not_used_mods: StringProperty()

    rig_weight_paint: BoolProperty(
        name="Minimize/Maximize Weight Paint",
        default=True,
    )
    wp_clear_from_roots_switch: BoolProperty(
        name="Clear Weight Paint from Root",
        default=False,
    )
    wp_clear_from_roots_distance: FloatProperty(
        name="Distance from Root (cm)",
        default=5,
        soft_max=100,
        min=0,
    )
    wp_fix_braids_switch: BoolProperty(
        name="Fix Braids Mesh",
    )
    wp_tweak_levels_switch: BoolProperty(
        name="Tweak Levels",
    )
    wp_levels_offset: FloatProperty(
        name="Offset",
        default=0.1,
        max=1,
        min=-1,
    )
    wp_level_gain: FloatProperty(
        name="Gain",
        default=1,
        soft_max=10,
        min=0,
    )
    wp_smooth_switch: BoolProperty(
        name="Smooth Weights",
    )
    wp_smooth_factor: FloatProperty(
        name="Factor",
        default=0.5,
        max=1,
        min=0,
    )
    wp_smooth_iterations: IntProperty(
        name="Iterations",
        default=5,
        soft_max=200,
        min=1,
    )
    wp_smooth_expand: FloatProperty(
        name="Expand/Contract",
        default=1,
        max=1,
        min=-1,
    )


class GBH_ConvertProperties(PropertyGroup):
    """Convert property group"""

    convert_particle: BoolProperty(
        name="Minimize/Maximize Particle System Conversion",
        default=False,
    )
    convert_particle_to_curves: BoolProperty(
        name="Minimize/Maximize Particle System to Hair Curves Conversion",
        default=False,
    )
    convert_mesh: BoolProperty(
        name="Minimize/Maximize Mesh Conversion",
        default=False,
    )
    convert_curve: BoolProperty(
        name="Minimize/Maximize Curve Conversion",
        default=False,
    )
    convert_curves: BoolProperty(
        name="Minimize/Maximize Hair Curves Conversion",
        default=False,
    )
    attach_curves_to_surface: BoolProperty(
        name="Minimize/Maximize Attach Hair Curves to Surface",
        default=False,
    )
    convert_curve_res_switch: BoolProperty(
        name="Resample curve",
        default=False,
    )
    convert_curve_res: IntProperty(
        name="Curve Resolution (points)",
        description="Number of points curve would have",
        min=2,
        soft_max=10,
        default=5,
    )
    convert_curves_res_switch: BoolProperty(
        name="Resample hair curves",
        default=False,
    )
    convert_curves_res: IntProperty(
        name="Hair Curves Resolution (points)",
        description="Number of points hair curves would have",
        min=2,
        soft_max=10,
        default=5,
    )
    particle_parent_object: PointerProperty(
        name="Object to Convert Particles from",
        description="Mesh object to convert particle systems from",
        type=bpy.types.Object,
        poll=_particle_parent_object_poll,
    )
    particle_to_curve_name: StringProperty(
        name="Converted Hair Name",
        default="",
    )


class GBH_InfoProperties(PropertyGroup):
    """Info property group"""

    info_uv: BoolProperty(
        name="Minimize/Maximize UV Info Section",
        default=False,
    )
    info_mesh: BoolProperty(
        name="Minimize/Maximize Mesh Info Section",
        default=False,
    )
    info_convert: BoolProperty(
        name="Minimize/Maximize Conversion Info Section",
        default=False,
    )
    info_particle: BoolProperty(
        name="Minimize/Maximize Particle System Info Section",
        default=False,
    )
    info_rendering: BoolProperty(
        name="Minimize/Maximize Rendering Info Section",
        default=False,
    )
    info_rig: BoolProperty(
        name="Minimize/Maximize Rig Info Section",
        default=False,
    )


class GBH_HairCardProperties(PropertyGroup):
    """Hair card texturing property group"""

    hc_output_name: StringProperty(
        name="Texture Output Name",
    )
    hc_resolution: EnumProperty(
        name="Texture Resolution",
        items=[
            ("1024", "1K", ""),
            ("2048", "2K", ""),
            ("4096", "4K", ""),
            ("8192", "8K", ""),
        ],
        default="4096"
    )
    hc_camera_toggle: BoolProperty(
        name="Minimize/Maximize Camera Settings",
        default=False,
    )
    hc_output_toggle: BoolProperty(
        name="Minimize/Maximize Output Settings",
        default=False,
    )
    hc_objects_toggle: BoolProperty(
        name="Minimize/Maximize Hair Objects",
        default=False,
    )
    hc_object_name: StringProperty(
        name="New Curve Name",
    )
    hc_add_current_frame_to_names: BoolProperty(
        name="Add Current Frame to Render Names",
        default=True,
        update=_render_complete_handler,
    )


class GBH_UpdateProperties(PropertyGroup):
    """Update property group"""
    update_report: StringProperty(
        default="No update check has been done yet in this session"
    )


class GBH_PanelProperties(PropertyGroup):
    """Panel property group"""
    panels_state: BoolProperty(
        default=False
    )
    panel_update_switch: BoolProperty(
        name="Update Panel Toggle",
        default=True,
    )
    panel_rig_switch: BoolProperty(
        name="Rigging Panel Toggle",
        default=True,
    )
    panel_convert_switch: BoolProperty(
        name="Convert Panel Toggle",
        default=True,
    )
    panel_lib_switch: BoolProperty(
        name="Library Panel Toggle",
        default=True,
    )
    panel_hair_cards_switch: BoolProperty(
        name="Hair Cards Panel Toggle",
        default=True,
    )
    panel_info_switch: BoolProperty(
        name="Info Panel Toggle",
        default=True,
    )


classes = (
    GBH_PanelProperties,
    GBH_PresetsProperties,
    GBH_PresetsListProperties,
    GBH_ModsProperties,
    GBH_LibraryProperties,
    GBH_RigProperties,
    GBH_ConvertProperties,
    GBH_InfoProperties,
    GBH_HairCardProperties,
    GBH_UpdateProperties,
)


def register():
    from bpy.utils import register_class
    for cls in classes:
        register_class(cls)

    bpy.types.Scene.hair_object = PointerProperty(
        name="Hair Object",
        description="Hair object selection",
        type=bpy.types.Object,
        poll=_hair_object_poll,
    )
    bpy.types.Object.selected_mod_index = IntProperty(
        name="Selected Modifier Index"
    )
    bpy.types.WindowManager.gbh_panels = PointerProperty(
        type=GBH_PanelProperties
    )
    bpy.types.WindowManager.gbh_presets = PointerProperty(
        type=GBH_PresetsProperties
    )
    bpy.types.WindowManager.gbh_presets_list = CollectionProperty(
        type=GBH_PresetsListProperties, name=""
    )
    bpy.types.WindowManager.gbh_mods = PointerProperty(
        type=GBH_ModsProperties
    )
    bpy.types.WindowManager.gbh_lib = PointerProperty(
        type=GBH_LibraryProperties
    )
    bpy.types.WindowManager.gbh_rig = PointerProperty(
        type=GBH_RigProperties
    )
    bpy.types.WindowManager.gbh_convert = PointerProperty(
        type=GBH_ConvertProperties
    )
    bpy.types.WindowManager.gbh_info = PointerProperty(
        type=GBH_InfoProperties
    )
    bpy.types.WindowManager.gbh_hair_card = PointerProperty(
        type=GBH_HairCardProperties
    )
    bpy.types.WindowManager.gbh_update = PointerProperty(
        type=GBH_UpdateProperties
    )


def unregister():
    del bpy.types.Scene.hair_object
    del bpy.types.Object.selected_mod_index
    del bpy.types.WindowManager.gbh_presets
    del bpy.types.WindowManager.gbh_presets_list
    del bpy.types.WindowManager.gbh_mods
    del bpy.types.WindowManager.gbh_lib
    del bpy.types.WindowManager.gbh_rig
    del bpy.types.WindowManager.gbh_convert
    del bpy.types.WindowManager.gbh_info
    del bpy.types.WindowManager.gbh_hair_card
    del bpy.types.WindowManager.gbh_update

    from bpy.utils import unregister_class
    for cls in reversed(classes):
        unregister_class(cls)

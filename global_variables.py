# SPDX-License-Identifier: GPL-2.0-or-later

import bpy
import os

# Add-on info.
GBH_PACKAGE = __package__
GBH_VERSION = None

# URLs.
URL_DOCS = "https://GixoXYZ.github.io/GBHToolDocs/"
URL_CONTACT = "https://GixoXYZ.github.io"
URL_GITHUB = "https://github.com/GixoXYZ/BlenderGBHTool"
URL_GUMROAD = "https://gixo.gumroad.com/l/GBHTool"
URL_ISSUE = "https://github.com/GixoXYZ/BlenderGBHTool/issues/new"
URL_DISCUSS = "https://github.com/GixoXYZ/BlenderGBHTool/discussions/8"


URL_YOUTUBE = "https://www.youtube.com/playlist?list=PLFexHVb3hTS5wZYhBsFuzS574-5uv1RZ5"
URL_TWITTER = "https://twitter.com/GixoXYZ"
URL_DISCORD = "https://discord.com/invite/TxTpJ8FQaz"


# Directories.
current_file_path = os.path.dirname(__file__)
blender_path = bpy.utils.resource_path("LOCAL")
DIR_LIBRARY = os.path.join(current_file_path, "gbh_library/")
DIR_ASSETS = os.path.join(current_file_path, "assets/")
DIR_PRESETS = os.path.join(current_file_path, "presets/")
DIR_TEXTURES = os.path.join(current_file_path, "textures/")
DIR_ICONS = os.path.join(current_file_path, "icons/")
DIR_BLENDER_ASSETS = os.path.join(
    blender_path,
    "datafiles/assets/geometry_nodes/"
)

# Files.
PRE_MADE_NODES_FILE = "pre_made_ng.blend"

# UI.
LIST_ROWS = 4

# Directory and file.
INVALID_PATH = "Selected path is not valid."

# Updating.
update_checking = False
update_url = "https://github.com/GixoXYZ/BlenderGBHTool/releases"
update_info_url = "https://github.com/GixoXYZ/BlenderGBHTool/releases/latest"

# Github.
bug_template_fetching = False
feat_template_fetching = False
fetch_template_message = ""

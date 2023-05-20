# SPDX-License-Identifier: GPL-2.0-or-later

import bpy
import os

# Add-on info
GBH_PACKAGE = __package__

# URLs
URL_DOCS = "https://thegixo.github.io/GBHToolDocs/"
URL_YOUTUBE = "https://www.youtube.com/playlist?list=PLFexHVb3hTS5wZYhBsFuzS574-5uv1RZ5"
URL_TWITTER = "https://twitter.com/notGixo"
URL_DISCORD = "https://discord.com/invite/TxTpJ8FQaz"
URL_GUMROAD = "https://gixo.gumroad.com/l/GBHTool"
URL_UPDATE = "https://raw.githubusercontent.com/thegixo/GBHToolDocs/main/version.json"


# Directories
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

# Files
PRE_MADE_NODES_FILE = "pre_made_ng.blend"

# UI
LIST_ROWS = 4

# Directory and file
INVALID_PATH = "Selected path is not valid."

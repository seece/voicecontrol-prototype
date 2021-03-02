#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software Foundation,
#  Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.

bl_info = \
    {
        "name" : "Voice Control",
        "author" : "Pekka Väänänen",
        "version" : (0, 0, 1),
        "blender" : (2, 80, 0),
        "description" : "Control Blender with speech recognition.",
        "wiki_url" : "",
        "tracker_url" : "",
        #"category" : "",
    }

"""
This addon connects to Windows' speech recognition service and sends key commands
to the main Blender window.

It's rough around the edges and may crash, cause freezes and detect wrong phrases,
so it should be considered a prototype.
"""

import os
import bpy
import math
import sys
import site
import threading

from bpy.props import *

scriptdir, _  = os.path.split(__file__)
modulesdir = os.path.join(scriptdir, "deps/Lib/site-packages")

if modulesdir not in sys.path:
    print(f"Adding {modulesdir} as a site")

    # We need to add the modules dir as a "site" so that "pth files" get read by the interpreter.
    # See https://stackoverflow.com/a/15209116
    site.addsitedir(modulesdir)

    print("sys.path")
    for p in sys.path:
        print(f"  {p}")

# Force submodule reloads
if "bpy" in locals():
    import importlib
    if "speech" in locals():
        importlib.reload(speech)
    if "winkeys" in locals():
        importlib.reload(winkeys)
    if "vcodes" in locals():
        importlib.reload(vcodes)

from . import speech
from . import winkeys
from . import vcodes

phrase_to_codes = {}

def get_hardcoded_phrases():
    cmds = {
            'rotate' : ('R',),
            'rotate x' : ('R', 'X'),
            'rotate y' : ('R', 'Y'),
            'rotate z' : ('R', 'Z'),
            'grab' : ('G',),
            'grab x' : ('G', 'X'),
            'grab y' : ('G', 'Y'),
            'grab z' : ('G', 'Z'),
            'scale' : ('S',),
            'scale x' : ('S', 'X'),
            'scale y' : ('S', 'Y'),
            'scale z' : ('S', 'Z'),
            'no' : ('ESC',),
            'OK' : ('RETURN',),
            'mistake' : ('LEFT_CTRL', 'Z'), # TODO "undo" is overriden by windows
            'mode' : ('TAB',),
            'select all' : ('A',),
            'select none' : ('ALT', 'A'),
            'select invert' : ('CTRL', 'I'),
            'render' : ('F12',),
            'show camera' : ('NUMPAD_0',),
            'show top' : ('NUMPAD_7',),
            'show front' : ('NUMPAD_1',),
            'show right' : ('NUMPAD_3',),
            'show perspective' : ('NUMPAD_5',),
            'add' : ('LEFT_SHIFT', 'A',),
            'remove' : ('X',), # TODO "delete" is used by windows
            }


    codemap = {} # phrase -> (VK_..., )

    for phrase, keys in cmds.items():
        codes = list([vcodes.type_to_vcode(type) for type in keys])
        if None in codes:
            print(f"Binding for {codes} has unmapped keys!")
            continue
        codemap[phrase] = codes
    return codemap

def vcodes_to_string(codes):
    return " ".join([vcodes.vcode_to_type(c) for c in codes])

def callback(phrase, listener):
    area_type = bpy.context.area.type if bpy.context.area else 'NONE'
    print(f": {phrase} in area '{area_type}'")

    codes = None

    if phrase in phrase_to_codes:
        print(phrase)

        codes = phrase_to_codes[phrase]
        print("codes", codes, vcodes_to_string(codes))

    if codes is not None:
        for c in codes:
            winkeys.press_key(c)
        for c in codes:
            winkeys.release_key(c)

        speech.say(phrase)
    else:
        print(f"Couldn't find key mapping for phrase \"{phrase}\"")
        return


    # if phrase == "turn off":
    #     speech.say("Goodbye.")
    #     listener.stoplistening()

class VoiceControlPanel(bpy.types.Panel):
    bl_idname = 'SOME_PT_voice_panel'
    bl_label = 'Voice Control'
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "render"

    def draw(self, context):
        l = self.layout
        l.column().label(text = 'this is text')


class VoiceControlPrefs(bpy.types.AddonPreferences):
    bl_idname = __package__

    def draw(self, context):
        l = self.layout
        l.column().label(text = 'VOICE CONTROL!')

classes = (VoiceControlPanel, VoiceControlPrefs)

def initialize():
    global phrase_to_codes
    global listener

    wm = bpy.context.window_manager
    kc = wm.keyconfigs.user

    keymap_names = [
            '3D View',
            # '3D View Generic',
            # '3D View Tool: Cursor',
            # '3D View Tool: Edit Armature, Bone Envelope',
            # '3D View Tool: Edit Armature, Bone Size',
            # '3D View Tool: Edit Armature, Extrude',
            # '3D View Tool: Edit Armature, Extrude to Cursor',
            # '3D View Tool: Edit Armature, Roll',
            # '3D View Tool: Edit Curve, Draw',
            # '3D View Tool: Edit Curve, Extrude',
            # '3D View Tool: Edit Curve, Extrude to Cursor',
            # '3D View Tool: Edit Curve, Radius',
            # '3D View Tool: Edit Curve, Randomize',
            # '3D View Tool: Edit Curve, Tilt',
            # '3D View Tool: Edit Gpencil, Bend',
            # '3D View Tool: Edit Gpencil, Extrude',
            # '3D View Tool: Edit Gpencil, Radius',
            # '3D View Tool: Edit Gpencil, Select Box',
            # '3D View Tool: Edit Gpencil, Select Circle',
            # '3D View Tool: Edit Gpencil, Select Lasso',
            # '3D View Tool: Edit Gpencil, Shear',
            # '3D View Tool: Edit Gpencil, To Sphere',
            # '3D View Tool: Edit Gpencil, Transform Fill',
            # '3D View Tool: Edit Gpencil, Tweak',
            # '3D View Tool: Edit Mesh, Bevel',
            # '3D View Tool: Edit Mesh, Bisect',
            # '3D View Tool: Edit Mesh, Edge Slide',
            # '3D View Tool: Edit Mesh, Extrude Along Normals',
            # '3D View Tool: Edit Mesh, Extrude Individual',
            # '3D View Tool: Edit Mesh, Extrude Manifold',
            # '3D View Tool: Edit Mesh, Extrude Region',
            # '3D View Tool: Edit Mesh, Extrude to Cursor',
            # '3D View Tool: Edit Mesh, Inset Faces',
            # '3D View Tool: Edit Mesh, Knife',
            # '3D View Tool: Edit Mesh, Loop Cut',
            # '3D View Tool: Edit Mesh, Offset Edge Loop Cut',
            # '3D View Tool: Edit Mesh, Poly Build',
            # '3D View Tool: Edit Mesh, Push/Pull',
            # '3D View Tool: Edit Mesh, Randomize',
            # '3D View Tool: Edit Mesh, Rip Edge',
            # '3D View Tool: Edit Mesh, Rip Region',
            # '3D View Tool: Edit Mesh, Shrink/Fatten',
            # '3D View Tool: Edit Mesh, Smooth',
            # '3D View Tool: Edit Mesh, Spin',
            # '3D View Tool: Edit Mesh, Spin Duplicates',
            # '3D View Tool: Edit Mesh, To Sphere',
            # '3D View Tool: Edit Mesh, Vertex Slide',
            # '3D View Tool: Measure',
            # '3D View Tool: Move',
            # '3D View Tool: Object, Add Primitive',
            # '3D View Tool: Paint Gpencil, Arc',
            # '3D View Tool: Paint Gpencil, Box',
            # '3D View Tool: Paint Gpencil, Circle',
            # '3D View Tool: Paint Gpencil, Curve',
            # '3D View Tool: Paint Gpencil, Cutter',
            # '3D View Tool: Paint Gpencil, Eyedropper',
            # '3D View Tool: Paint Gpencil, Line',
            # '3D View Tool: Paint Gpencil, Polyline',
            # '3D View Tool: Paint Weight, Gradient',
            # '3D View Tool: Paint Weight, Sample Vertex Group',
            # '3D View Tool: Paint Weight, Sample Weight',
            # '3D View Tool: Pose, Breakdowner',
            # '3D View Tool: Pose, Push',
            # '3D View Tool: Pose, Relax',
            # '3D View Tool: Rotate',
            # '3D View Tool: Scale',
            # '3D View Tool: Sculpt Gpencil, Select Box',
            # '3D View Tool: Sculpt Gpencil, Select Circle',
            # '3D View Tool: Sculpt Gpencil, Select Lasso',
            # '3D View Tool: Sculpt Gpencil, Tweak',
            # '3D View Tool: Sculpt, Box Face Set',
            # '3D View Tool: Sculpt, Box Hide',
            # '3D View Tool: Sculpt, Box Mask',
            # '3D View Tool: Sculpt, Box Trim',
            # '3D View Tool: Sculpt, Cloth Filter',
            # '3D View Tool: Sculpt, Color Filter',
            # '3D View Tool: Sculpt, Face Set Edit',
            # '3D View Tool: Sculpt, Lasso Face Set',
            # '3D View Tool: Sculpt, Lasso Mask',
            # '3D View Tool: Sculpt, Lasso Trim',
            # '3D View Tool: Sculpt, Line Mask',
            # '3D View Tool: Sculpt, Line Project',
            # '3D View Tool: Sculpt, Mask By Color',
            # '3D View Tool: Sculpt, Mesh Filter',
            # '3D View Tool: Select Box',
            # '3D View Tool: Select Circle',
            # '3D View Tool: Select Lasso',
            # '3D View Tool: Shear',
            # '3D View Tool: Transform',
            # '3D View Tool: Tweak',
            # 'Animation',
            # 'Animation Channels',
            # 'Armature',
            # 'Bevel Modal Map',
            'Clip',
            # 'Clip Dopesheet Editor',
            # 'Clip Editor',
            # 'Clip Graph Editor',
            # 'Clip Time Scrub',
            # 'Console',
            # 'Curve',
            # 'Custom Normals Modal Map',
            # 'Dopesheet',
            # 'Dopesheet Generic',
            # 'Eyedropper ColorRamp PointSampling Map',
            # 'Eyedropper Modal Map',
            # 'File Browser',
            # 'File Browser Buttons',
            # 'File Browser Main',
            # 'Font',
            # 'Frames',
            # 'Generic Gizmo',
            # 'Generic Gizmo Click Drag',
            # 'Generic Gizmo Drag',
            # 'Generic Gizmo Maybe Drag',
            # 'Generic Gizmo Select',
            # 'Generic Gizmo Tweak Modal Map',
            # 'Generic Tool: Annotate',
            # 'Generic Tool: Annotate Eraser',
            # 'Generic Tool: Annotate Line',
            # 'Generic Tool: Annotate Polygon',
            # 'Gesture Box',
            # 'Gesture Lasso',
            # 'Gesture Straight Line',
            # 'Gesture Zoom Border',
            # 'Gizmos',
            # 'Graph Editor',
            # 'Graph Editor Generic',
            # 'Grease Pencil',
            # 'Grease Pencil Stroke Edit Mode',
            # 'Grease Pencil Stroke Paint (Draw brush)',
            # 'Grease Pencil Stroke Paint (Erase)',
            # 'Grease Pencil Stroke Paint (Fill)',
            # 'Grease Pencil Stroke Paint (Tint)',
            # 'Grease Pencil Stroke Paint Mode',
            # 'Grease Pencil Stroke Sculpt (Clone)',
            # 'Grease Pencil Stroke Sculpt (Grab)',
            # 'Grease Pencil Stroke Sculpt (Pinch)',
            # 'Grease Pencil Stroke Sculpt (Push)',
            # 'Grease Pencil Stroke Sculpt (Randomize)',
            # 'Grease Pencil Stroke Sculpt (Smooth)',
            # 'Grease Pencil Stroke Sculpt (Strength)',
            # 'Grease Pencil Stroke Sculpt (Thickness)',
            # 'Grease Pencil Stroke Sculpt (Twist)',
            # 'Grease Pencil Stroke Sculpt Mode',
            # 'Grease Pencil Stroke Vertex (Average)',
            # 'Grease Pencil Stroke Vertex (Blur)',
            # 'Grease Pencil Stroke Vertex (Draw)',
            # 'Grease Pencil Stroke Vertex (Replace)',
            # 'Grease Pencil Stroke Vertex (Smear)',
            # 'Grease Pencil Stroke Vertex Mode',
            # 'Grease Pencil Stroke Weight (Draw)',
            # 'Grease Pencil Stroke Weight Mode',
            # 'Header',
            # 'Image',
            # 'Image Editor Tool: Sample',
            # 'Image Editor Tool: Uv, Cursor',
            # 'Image Editor Tool: Uv, Move',
            # 'Image Editor Tool: Uv, Rip Region',
            # 'Image Editor Tool: Uv, Rotate',
            # 'Image Editor Tool: Uv, Scale',
            # 'Image Editor Tool: Uv, Sculpt Stroke',
            # 'Image Editor Tool: Uv, Select Box',
            # 'Image Editor Tool: Uv, Select Circle',
            # 'Image Editor Tool: Uv, Select Lasso',
            # 'Image Editor Tool: Uv, Tweak',
            # 'Image Generic',
            # 'Image Paint',
            # 'Info',
            # 'Knife Tool Modal Map',
            # 'Lattice',
            # 'Markers',
            # 'Mask Editing',
            'Mesh',
            # 'Metaball',
            # 'NLA Channels',
            # 'NLA Editor',
            # 'NLA Generic',
            # 'Node Editor',
            # 'Node Generic',
            # 'Node Tool: Links Cut',
            # 'Node Tool: Select Box',
            # 'Node Tool: Select Circle',
            # 'Node Tool: Select Lasso',
            # 'Node Tool: Tweak',
            'Object Mode',
            # 'Object Non-modal',
            # 'Outliner',
            # 'Paint Curve',
            # 'Paint Face Mask (Weight, Vertex, Texture)',
            # 'Paint Stroke Modal',
            # 'Paint Vertex Selection (Weight, Vertex)',
            # 'Particle',
            # 'Pose',
            # 'Property Editor',
            # 'Region Context Menu',
            'Screen',
            # 'Screen Editing',
            # 'Sculpt',
            # 'Sequencer',
            # 'Sequencer Tool: Blade',
            # 'Sequencer Tool: Sample']
            # 'Sequencer Tool: Select',
            # 'Sequencer Tool: Select Box',
            # 'SequencerCommon',
            # 'SequencerPreview',
            # 'Standard Modal Map',
            # 'Text',
            # 'Text Generic',
            # 'Time Scrub',
            # 'Toolbar Popup',
            # 'Transform Modal Map',
            # 'User Interface',
            # 'UV Editor',
            # 'Vertex Paint',
            # 'View2D',
            # 'View2D Buttons List',
            # 'View3D Dolly Modal',
            # 'View3D Fly Modal',
            # 'View3D Gesture Circle',
            # 'View3D Move Modal',
            # 'View3D Placement Modal Map',
            # 'View3D Rotate Modal',
            # 'View3D Walk Modal',
            # 'View3D Zoom Modal',
            # 'Weight Paint',
        ]

    # Keymaps are loaded after addons so we postpone initialization with a short timer.
    if 'Clip' not in kc.keymaps:
        bpy.app.timers.register(initialize, first_interval=0.01)
        return

    def get_map_items(map_names):
        """
        Fetches all keymaps given in "map_names" and returns a {phrase: [KeyMapItem]} dict.
        """

        wm = bpy.context.window_manager
        kc = wm.keyconfigs.user

        items = {}

        for name in map_names:
            km = kc.keymaps[name]
            for ki in km.keymap_items:
                items[ki.name] = ki

        return items

    # First set up detection phrases from built-in keymaps.

    map_items = get_map_items(keymap_names)

    for phrase, ki in map_items.items():
        codes = vcodes.keyitem_to_vcodes(ki)

        if codes:
            phrase_to_codes[phrase] = codes
        else:
            print(f"Couldn't create key mapping for phrase \"{phrase}\"")


    # Then add hard coded custom phrases at the top.

    phrase_to_codes.update(get_hardcoded_phrases())

    print("Registered phrases:")
    for phrase, codes in phrase_to_codes.items():
        print(f"   {vcodes_to_string(codes):<20} {phrase}")

    listener = speech.listenfor(phrase_to_codes.keys(), callback)

def register():
    initialize()

    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    listener.stoplistening()
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)


if __name__ == "__main__":
    register()

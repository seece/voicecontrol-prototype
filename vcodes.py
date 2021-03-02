# For key constants, see the following links.
# https://docs.blender.org/api/2.92/bpy.types.KeyMapItem.html
# https://docs.microsoft.com/en-us/windows/win32/inputdev/virtual-key-codes

VK_LBUTTON = 0x01
VK_RBUTTON = 0x02
VK_MBUTTON = 0x04
VK_TAB  = 0x09
VK_RETURN = 0x0D
VK_SHIFT = 0x10
VK_CONTROL = 0x11
VK_MENU = 0x12 # alt
VK_LSHIFT = 0xA0
VK_RSHIFT = 0xA1
VK_LCONTROL = 0xA2
VK_RCONTROL = 0xA3
VK_LMENU = 0xA4
VK_RMENU = 0xA5

VK_LEFT = 0x25
VK_UP = 0x26
VK_RIGHT = 0x27
VK_DOWN = 0x28
VK_ESCAPE = 0x1B

VK_NUMPAD0 = 0x60
VK_NUMPAD1 = 0x61
VK_NUMPAD2 = 0x62
VK_NUMPAD3 = 0x63
VK_NUMPAD4 = 0x64
VK_NUMPAD5 = 0x65
VK_NUMPAD6 = 0x66
VK_NUMPAD7 = 0x67
VK_NUMPAD8 = 0x68
VK_NUMPAD9 = 0x69

VK_F1 = 0x70
VK_F2 = 0x71
VK_F3 = 0x72
VK_F4 = 0x73
VK_F5 = 0x74
VK_F6 = 0x75
VK_F7 = 0x76
VK_F8 = 0x77
VK_F9 = 0x78
VK_F10 = 0x79
VK_F11 = 0x7A
VK_F12 = 0x7B

mapping = {
    # not part of blender, here for introspection use only
    'ALT' : VK_MENU,
    'CTRL' : VK_CONTROL,
    'SHIFT' : VK_SHIFT,

    # blender keys
    'LEFTMOUSE': VK_LBUTTON,
    'MIDDLEMOUSE': VK_MBUTTON,
    'RIGHTMOUSE': VK_RBUTTON,
    'ZERO':     0x30,
    'ONE':      0x31,
    'TWO':      0x32,
    'THREE':    0x33,
    'FOUR':     0x34,
    'FIVE':     0x35,
    'SIX':      0x36,
    'SEVEN':    0x37,
    'EIGHT':    0x38,
    'NINE':     0x39,
    'A': 0x41,
    'B': 0x42,
    'C': 0x43,
    'D': 0x44,
    'E': 0x45,
    'F': 0x46,
    'G': 0x47,
    'H': 0x48,
    'I': 0x49,
    'J': 0x4A,
    'K': 0x4B,
    'L': 0x4C,
    'M': 0x4D,
    'N': 0x4E,
    'O': 0x4F,
    'P': 0x50,
    'Q': 0x51,
    'R': 0x52,
    'S': 0x53,
    'T': 0x54,
    'U': 0x55,
    'V': 0x56,
    'W': 0x57,
    'X': 0x58,
    'Y': 0x59,
    'Z': 0x5A,
    'LEFT_CTRL': VK_LCONTROL,
    'LEFT_ALT': VK_LMENU,
    'LEFT_SHIFT': VK_LSHIFT,
    'RIGHT_CTRL': VK_RCONTROL,
    'RIGHT_ALT': VK_RMENU,
    'RIGHT_SHIFT': VK_RSHIFT,
    'LEFT_ARROW': VK_LEFT,
    'RIGHT_ARROW': VK_RIGHT,
    'UP_ARROW': VK_UP,
    'DOWN_ARROW': VK_DOWN,
    'RETURN': VK_RETURN,
    'ESC': VK_ESCAPE,
    'TAB': VK_TAB,
    'F1': VK_F1,
    'F2': VK_F2,
    'F3': VK_F3,
    'F4': VK_F4,
    'F5': VK_F5,
    'F6': VK_F6,
    'F7': VK_F7,
    'F8': VK_F8,
    'F9': VK_F9,
    'F10': VK_F10,
    'F11': VK_F11,
    'F12': VK_F12,
    'NUMPAD_0' : VK_NUMPAD0,
    'NUMPAD_1' : VK_NUMPAD1,
    'NUMPAD_2' : VK_NUMPAD2,
    'NUMPAD_3' : VK_NUMPAD3,
    'NUMPAD_4' : VK_NUMPAD4,
    'NUMPAD_5' : VK_NUMPAD5,
    'NUMPAD_6' : VK_NUMPAD6,
    'NUMPAD_7' : VK_NUMPAD7,
    'NUMPAD_8' : VK_NUMPAD8,
    'NUMPAD_9' : VK_NUMPAD9,
}

mapping_inverse = {v: k for (k, v) in mapping.items()}

def type_to_vcode(type):
    return mapping.get(type, None)

def vcode_to_type(vcode):
    return mapping_inverse.get(vcode, str(vcode))

def keyitem_to_vcodes(ki):
    if ki.map_type != 'KEYBOARD':
        print(f"Warning: '{ki.name}' had map_type '{ki.map_type}'!")
        return None

    codes = []
    if ki.shift:
        codes.append(VK_SHIFT)
    if ki.ctrl:
        codes.append(VK_CONTROL)
    if ki.alt:
        codes.append(VK_MENU)

    modifier = type_to_vcode(ki.key_modifier)

    if modifier:
        codes.append(modifier)

    key = type_to_vcode(ki.type)

    if key:
        codes.append(key)

    return codes


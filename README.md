# Blender Voice Control Prototype

*Control Blender with Windows Speech Recognition.*

This addon sends simulated key presses to the Blender window when a voice control phrase is heard. Phrases are automatically read from user keybindings.

This is **a prototype quality addon** and meant as a base for further research. It is **not supported** and issues will be closed.

## Installation

1. Install the `voicecontrol-prototype` addon.
2. Install its `pywin32` dependency.

### 1. The addon

Use the preferences dialog to install like with any addon.

### 2. pywin32

You need to install the `pywin32` package to run this addon.

### Installing pywin32 into addon dir

A Python "wheel" package is bundled in `external/` for convenience. Install it to `voicecontrol-prototype/deps/` so that the addon finds it.

    cd voicecontrol-prototype
    python -m pip install external/pywin32-300-cp37-cp37m-win_amd64.whl --prefix deps

This makes it easy to remove the addon and it's dependencies.

For example for Blender 2.91:

    cd %APPDATA%\Blender Foundation\Blender\2.91\scripts\addons\voicecontrol-prototype
    "C:\Program Files\Blender Foundation\Blender 2.91\2.91\python\bin\python.exe" -m pip install external/pywin32-300-cp37-cp37m-win_amd64.whl --prefix deps

Then restart Blender.

## How it works


This addon reads Blender's keymaps and listens to their names. For example, saying "New File" will be mapped to `CTRL+N`. There are also custom commands added for convenience. See `get_hardcoded_phrases()` in `__init__.py`.

You should see the Speech Recognition window pop up when the addon loads. You must **activate speech recognition by clicking the round button**.

![Speech recognition's "listening" panel](img/listening.PNG)

*Speech Recognition is active.*

No external software is needed since Windows Speech Recognition COM objects can be used via Python (see `speech.py`).

### Limitations

- Not all keys are mapped into Windows virtual `VK_*` codes so many commands simply won't work.
- Speech recognition only works on the system language. This can't be changed.
- Speech recognition is a bit slow.
- No context is taken into account when sending the key presses.
- Many mappings have the same name but they overlap.
- Windows only.

## Blender speech recognition related links

- rootaman's [Voice Command for Blender with Vocola](https://www.reddit.com/r/blender/comments/axx1i0/my_voice_command_in_blender_which_maybe_useful/)
- [Blender Voice Command (archived)](https://web.archive.org/web/20160408160551/http://www.blendervoicecommand.com/)
- http://auralbits.blogspot.com/2010/04/windows-speech-registry-hacking-for-fun.html

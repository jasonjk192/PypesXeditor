About
-----

This is an example project in Python to showcase the usage of pesXeditor (which is based on [4ccEditor](https://github.com/the4chancup/4ccEditor))

NumPy and Pandas (wip) are optional.

Currently only PES 17 load/save functions are implemented. pesXeditor.dll is also included.

Usage
-----

Brief overview of the included scripts:
pes_data.py -> holds the ctype conversions between python and the dll as well as other data
pes_masterkey.py -> helper script to load masterkey if required
pes_schema.py -> helper to convert between ctype and numpy format
pes_loader.py -> contains most of the load/save code as well as some extra functions present in the dll (like descriptors)
pes_editor.py -> main file which you'll want to import for use. Contains a base editor class and then game specific classes

In case savefile or .dll path is incorrect, check pes_data.py and modify the paths there.

Example code:

```
import pes_editor
editor = pes_editor.PES17Editor() # main object (game specific) to handle load/save

# manipulate stuff -> see pes_editor.py for availble functions
# also see pes_data.py for a full list of accessible fields
print(editor.players[100].id)  # from pes_data.editor_player_entry
print(editor.players[100].data.name_string) # from pes_data.editor_player_export. Note: data.name isn't in a proper format so you need to use name_string
editor.players[100].data.name_string = 'New Name' # edit the data

editor.save() # optional if you wish to save the changes
editor.close() # required to properly unload the data
```
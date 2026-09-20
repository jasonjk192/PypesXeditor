import ctypes
import sys
from enum import IntEnum
from dataclasses import dataclass

VERSION_TYPE = {
    15: "15",
    16: "Old",
    17: "Old",
    18: "New",
    19: "New",
    20: "New",
    21: "New"
}

class OpResult(IntEnum):
    UNKNOWN = -1
    OK = 0
    READ_FILE_STAT_FAILED = 1
    INVALID_ARGUMENT = 2
    OPEN_FAILED = 3
    ALLOC_FAILED = 4

class FileHeaderOld(ctypes.Structure):
    _fields_ = [
        ("mysteryData", ctypes.c_uint8 * 64),
        ("dataSize", ctypes.c_uint32),
        ("logoSize", ctypes.c_uint32),
        ("descSize", ctypes.c_uint32),
        ("serialLength", ctypes.c_uint32),
        ("hash", ctypes.c_uint8 * 64),
        ("fileTypeString", ctypes.c_uint8 * 32),
    ]

class FileDescriptorOld(ctypes.Structure):
    _fields_ = [
        ("encryptionHeader", ctypes.POINTER(ctypes.c_uint8)),
        ("fileHeader", ctypes.POINTER(FileHeaderOld)),
        ("description", ctypes.POINTER(ctypes.c_uint8)),
        ("logo", ctypes.POINTER(ctypes.c_uint8)),
        ("data", ctypes.POINTER(ctypes.c_uint8)),
        ("serial", ctypes.POINTER(ctypes.c_uint8)),
    ]

class FileHeaderNew(ctypes.Structure):
    _fields_ = [
        ("mysteryData", ctypes.c_uint8 * 64),
        ("dataSize", ctypes.c_uint32),
        ("logoSize", ctypes.c_uint32),
        ("descSize", ctypes.c_uint32),
        ("serialLength", ctypes.c_uint32),
        ("hash", ctypes.c_uint8 * 64),
        ("fileTypeString", ctypes.c_uint8 * 32),
        ("gameVersionString", ctypes.c_uint8 * 32),
    ]

class FileDescriptorNew(ctypes.Structure):
    _fields_ = [
        ("encryptionHeader", ctypes.POINTER(ctypes.c_uint8)),
        ("fileHeader", ctypes.POINTER(FileHeaderNew)),
        ("description", ctypes.POINTER(ctypes.c_uint8)),
        ("logo", ctypes.POINTER(ctypes.c_uint8)),
        ("data", ctypes.POINTER(ctypes.c_uint8)),
        ("serial", ctypes.POINTER(ctypes.c_uint8)),
    ]

class FileDescriptor15(ctypes.Structure):
    _fields_ = [
        ("dataSize", ctypes.c_uint32),
        ("startByte", ctypes.c_ubyte),
        ("chunk0Size", ctypes.c_uint32),
        ("chunk1Size", ctypes.c_uint32),
        ("chunk2Size", ctypes.c_uint32),

        ("chunk0", ctypes.POINTER(ctypes.c_uint8)),
        ("chunk1lenBytes", ctypes.POINTER(ctypes.c_uint8)),
        ("chunk1", ctypes.POINTER(ctypes.c_uint8)),
        ("chunk2lenBytes", ctypes.POINTER(ctypes.c_uint8)),
        ("data", ctypes.POINTER(ctypes.c_uint8)),
    ]
    
class editor_player_export(ctypes.Structure):
    _fields_ = [
        ("nation", ctypes.c_uint32),
        ("height", ctypes.c_uint8),
        ("weight", ctypes.c_uint8),
        ("gc1", ctypes.c_uint8),
        ("gc2", ctypes.c_uint8),
        ("atk", ctypes.c_uint8),
        ("def", ctypes.c_uint8),
        ("gk", ctypes.c_uint8),
        ("drib", ctypes.c_uint8),
        ("mo_fk", ctypes.c_uint8),
        ("finish", ctypes.c_uint8),
        ("lowpass", ctypes.c_uint8),
        ("loftpass", ctypes.c_uint8),
        ("header", ctypes.c_uint8),
        ("form", ctypes.c_uint8),
        ("b_edit_player", ctypes.c_uint8),
        ("swerve", ctypes.c_uint8),
        ("catching", ctypes.c_uint8),
        ("clearing", ctypes.c_uint8),
        ("reflex", ctypes.c_uint8),
        ("injury", ctypes.c_uint8),
        ("b_edit_basicset", ctypes.c_uint8),
        ("body_ctrl", ctypes.c_uint8),
        ("phys_cont", ctypes.c_uint8),
        ("kick_pwr", ctypes.c_uint8),
        ("exp_pwr", ctypes.c_uint8),
        ("mo_armd", ctypes.c_uint8),
        ("b_edit_regpos", ctypes.c_uint8),
        ("age", ctypes.c_uint8),
        ("reg_pos", ctypes.c_uint8),
        ("play_style", ctypes.c_uint8),
        ("ball_ctrl", ctypes.c_uint8),
        ("ball_win", ctypes.c_uint8),
        ("weak_acc", ctypes.c_uint8),
        ("jump", ctypes.c_uint8),
        ("mo_armr", ctypes.c_uint8),
        ("mo_ck", ctypes.c_uint8),
        ("cover", ctypes.c_uint8),
        ("weak_use", ctypes.c_uint8),

        ("play_pos", ctypes.c_uint8 * 13),

        ("mo_hunchd", ctypes.c_uint8),
        ("mo_hunchr", ctypes.c_uint8),
        ("mo_pk", ctypes.c_uint8),
        ("place_kick", ctypes.c_uint8),
        ("star", ctypes.c_uint8),
        ("mo_drib", ctypes.c_uint8),
        ("tight_pos", ctypes.c_uint8),
        ("aggres", ctypes.c_uint8),
        ("play_attit", ctypes.c_uint8),
        ("b_edit_playpos", ctypes.c_uint8),
        ("b_edit_ability", ctypes.c_uint8),
        ("b_edit_skill", ctypes.c_uint8),
        ("stamina", ctypes.c_uint8),
        ("speed", ctypes.c_uint8),
        ("b_edit_style", ctypes.c_uint8),
        ("b_edit_com", ctypes.c_uint8),
        ("b_edit_motion", ctypes.c_uint8),
        ("b_base_copy", ctypes.c_uint8),
        ("strong_foot", ctypes.c_uint8),
        ("strong_hand", ctypes.c_uint8),

        ("com_style", ctypes.c_uint8 * 7),
        ("play_skill", ctypes.c_uint8 * 41),

        ("name", ctypes.c_uint16 * 61),
        ("shirt_name", ctypes.c_char * 21),

        ("b_edit_face", ctypes.c_uint8),
        ("b_edit_hair", ctypes.c_uint8),
        ("b_edit_phys", ctypes.c_uint8),
        ("b_edit_strip", ctypes.c_uint8),

        ("boot_id", ctypes.c_uint32),
        ("glove_id", ctypes.c_uint32),
        ("copy_id", ctypes.c_uint32),

        ("neck_len", ctypes.c_int32),
        ("neck_size", ctypes.c_int32),
        ("shldr_hi", ctypes.c_int32),
        ("shldr_wid", ctypes.c_int32),
        ("chest", ctypes.c_int32),
        ("waist", ctypes.c_int32),
        ("arm_size", ctypes.c_int32),
        ("arm_len", ctypes.c_int32),
        ("thigh", ctypes.c_int32),
        ("calf", ctypes.c_int32),
        ("leg_len", ctypes.c_int32),
        ("head_len", ctypes.c_int32),
        ("head_wid", ctypes.c_int32),
        ("head_dep", ctypes.c_int32),

        ("wrist_col_l", ctypes.c_uint8),
        ("wrist_col_r", ctypes.c_uint8),
        ("wrist_tape", ctypes.c_uint8),
        ("spec_col", ctypes.c_uint8),
        ("spec_style", ctypes.c_uint8),
        ("sleeve", ctypes.c_uint8),
        ("inners", ctypes.c_uint8),
        ("socks", ctypes.c_uint8),
        ("undershorts", ctypes.c_uint8),
        ("untucked", ctypes.c_uint8),
        ("ankle_tape", ctypes.c_uint8),
        ("gloves", ctypes.c_uint8),
        ("gloves_col", ctypes.c_uint8),
        ("skin_col", ctypes.c_uint8),
        ("iris_col", ctypes.c_uint8),
    ]
    
    @property
    def name_string(self):
        return _decode_c_uint16_string(self.name)
        
    @name_string.setter
    def name_string(self, value):
        self.name = _encode_c_uint16_string(value, 61)

    #@property
    #def shirt_name_string(self):
    #    return  _decode_c_uint16_string(self.shirt_name)
        
    #@shirt_name_string.setter
    #def shirt_name_string(self, value):
    #    self.shirt_name = _encode_c_uint16_string(value, 21)

class editor_player_entry(ctypes.Structure):
    _fields_ = [
        ("data", editor_player_export),
        ("id", ctypes.c_uint32),
        ("app_id", ctypes.c_uint32),
        ("b_changed", ctypes.c_uint8),
        ("b_show", ctypes.c_uint8),
        ("team_ind", ctypes.c_int32),
        ("team_lineup_ind", ctypes.c_int32),
    ]

class editor_strip_set(ctypes.Structure):
    _fields_ = [
        ("stripNumber", ctypes.c_uint8),
        ("stripTeamId", ctypes.c_uint32),
    ]

class editor_team_entry(ctypes.Structure):
    _fields_ = [
        ("id", ctypes.c_uint32),
        ("manager_id", ctypes.c_uint32),
        ("stadium_id", ctypes.c_int32),

        ("name", ctypes.c_uint16 * 0x46),
        ("short_name", ctypes.c_char * 0x4),

        ("players", ctypes.c_uint32 * 40),
        ("numbers", ctypes.c_uint16 * 40),

        ("b_edit_name", ctypes.c_uint8),
        ("b_edit_shortname", ctypes.c_uint8),
        ("b_edit_stadium", ctypes.c_uint8),
        ("b_edit_strip", ctypes.c_uint8),

        ("num_on_team", ctypes.c_int32),

        ("starting11", ctypes.c_int32 * 11),

        ("captain_ind", ctypes.c_int8),

        ("color1_red", ctypes.c_int8),
        ("color1_blue", ctypes.c_int8),
        ("color1_green", ctypes.c_int8),

        ("color2_red", ctypes.c_int8),
        ("color2_blue", ctypes.c_int8),
        ("color2_green", ctypes.c_int8),

        ("stripBlock", editor_strip_set * 10),

        ("b_changed", ctypes.c_uint8),
        ("b_show", ctypes.c_uint8),
    ]
    
    @property
    def name_string(self):
        return _decode_c_uint16_string(self.name)
        
    @name_string.setter
    def name_string(self, value):
        self.name = _encode_c_uint16_string(value, 0x46)
        self.b_changed = True
        
    @property
    def short_name_string(self):
        return _decode_c_uint16_string(self.short_name)
        
    @short_name_string.setter
    def short_name_string(self, value):
        self.short_name = _encode_c_uint16_string(value, 0x4)
        self.b_changed = True

@dataclass
class SaveData15:
    descriptor: ctypes.POINTER(FileDescriptor15)
    players: ctypes.POINTER(editor_player_entry)
    num_players: ctypes.c_uint32
    teams: ctypes.POINTER(editor_team_entry)
    num_teams: ctypes.c_uint32
    
@dataclass
class SaveDataOld:
    descriptor: ctypes.POINTER(FileDescriptorOld)
    players: ctypes.POINTER(editor_player_entry)
    num_players: ctypes.c_uint32
    teams: ctypes.POINTER(editor_team_entry)
    num_teams: ctypes.c_uint32
    
@dataclass
class SaveDataNew:
    descriptor: ctypes.POINTER(FileDescriptorNew)
    players: ctypes.POINTER(editor_player_entry)
    num_players: ctypes.c_uint32
    teams: ctypes.POINTER(editor_team_entry)
    num_teams: ctypes.c_uint32

def _decode_c_uint16_string(s):
    if not s or len(s) == 0:
        return ""
    try:
        decoded = bytes(s).decode('utf-16-le', errors='strict')
        return decoded.split('\x00', 1)[0]
    except (UnicodeDecodeError, TypeError):
        return ""

def _encode_c_uint16_string(s, max_length):
    encoded = s.encode("utf-16-le")
    outS = (ctypes.c_uint16*max_length)()
    if len(s) > max_length-1:
        raise ValueError("string is too long (maximum "+str(max_length-1)+" UTF-16 characters)")
    for i in range(max_length):
        outS[i] = 0
    for i in range(len(encoded) // 2):
        outS[i] = int.from_bytes(encoded[i * 2:i * 2 + 2], byteorder="little")
    return outS

def _get_document_dir():
    if sys.version_info >= (3, 4):
        from pathlib import Path
        return str(Path.home() / "Documents")
    else:
        import os
        return str(os.path.join(os.path.expanduser("~"), "Documents"))

dll_lib_path = ".\\pesXeditor.dll"
savefile_path = _get_document_dir()+"\\KONAMI\\Pro Evolution Soccer 2017\\save\\EDIT00000000"

EditorCache = ctypes.c_void_p

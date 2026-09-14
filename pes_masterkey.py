import ctypes

def _get_masterkey(version):
    if version == 15:
        return "MasterKeyPes15"
    elif version == 16:
        return "MasterKeyPes16"
    elif version == 17:
        return "MasterKeyPes17"
    elif version == 18:
        return "MasterKeyPes18"
    elif version == 19:
        return "MasterKeyPes19"
    elif version == 20:
        return "MasterKeyPes20"
    elif version == 21:
        return "MasterKeyPes21"
    return "MasterKeyZero"

def load_masterkey(dll_lib, version):
    ArrayType64 = ctypes.c_uint8 * 64
    masterkey_array = ArrayType64.in_dll(dll_lib, _get_masterkey(version))
    return masterkey_array
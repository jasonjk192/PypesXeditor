import ctypes

import pes_data
import pes_masterkey

def load_dll():
	return ctypes.WinDLL(pes_data.dll_lib_path)

def _load_savefile_as_buffer():
	with open(pes_data.savefile_path, "rb") as f:
		savefile = f.read()
	savefile_buffer = (ctypes.c_uint8 * len(savefile)).from_buffer_copy(savefile)
	return savefile_buffer
    
def _create_descriptorOld(dll_lib):
	dll_lib.createFileDescriptorOld.argtypes = []
	dll_lib.createFileDescriptorOld.restype = ctypes.POINTER(pes_data.FileDescriptorOld)
	dll_lib.decryptWithKeyOld.argtypes = [
	    ctypes.POINTER(pes_data.FileDescriptorOld),
	    ctypes.POINTER(ctypes.c_uint8),
	    ctypes.POINTER(ctypes.c_uint8),
	]
	dll_lib.decryptWithKeyOld.restype = None
	descriptorOld = dll_lib.createFileDescriptorOld()
	return descriptorOld

def _create_descriptorNew(dll_lib):
    dll_lib.createFileDescriptorNew.argtypes = []
    dll_lib.createFileDescriptorNew.restype = ctypes.POINTER(pes_data.FileDescriptorNew)
    dll_lib.decryptWithKeyNew.argtypes = [
        ctypes.POINTER(pes_data.FileDescriptorNew),
        ctypes.POINTER(ctypes.c_uint8),
        ctypes.POINTER(ctypes.c_uint8),
    ]
    dll_lib.decryptWithKeyNew.restype = None
    descriptorNew = dll_lib.createFileDescriptorNew()
    return descriptorNew

def _create_descriptor15(dll_lib):
    dll_lib.createFileDescriptor15.argtypes = []
    dll_lib.createFileDescriptor15.restype = ctypes.POINTER(pes_data.FileDescriptor15)
    dll_lib.decryptWithKey15.argtypes = [
        ctypes.POINTER(pes_data.FileDescriptor15),
        ctypes.POINTER(ctypes.c_uint8),
        ctypes.POINTER(ctypes.c_uint8),
    ]
    dll_lib.decryptWithKey15.restype = None
    descriptor15 = dll_lib.createFileDescriptor15()
    return descriptor15

def _get_descriptorOld(dll_lib, version):
    version_type = pes_data.VERSION_TYPE[version]
    if version_type != "Old":
        return None
        
    savefile_buffer = _load_savefile_as_buffer()
    masterkey_array = pes_masterkey.load_masterkey(dll_lib, version)
    descriptor = _create_descriptorOld(dll_lib)
    dll_lib.decryptWithKeyOld(descriptor, savefile_buffer, masterkey_array)
    return descriptor
    
def _get_descriptorNew(dll_lib, version):
    version_type = pes_data.VERSION_TYPE[version]
    if version_type != "New":
        return None
        
    savefile_buffer = _load_savefile_as_buffer()
    masterkey_array = pes_masterkey.load_masterkey(dll_lib, version)
    descriptor = _create_descriptorNew(dll_lib)
    dll_lib.decryptWithKeyNew(descriptor, savefile_buffer, masterkey_array)
    return descriptor
    
def _get_descriptor15(dll_lib):
    version_type = pes_data.VERSION_TYPE[version]
    if version_type != "15":
        return None
        
    savefile_buffer = _load_savefile_as_buffer()
    masterkey_array = pes_masterkey.load_masterkey(dll_lib, 15)
    descriptor = _create_descriptor15(dll_lib)
    dll_lib.decryptWithKey15(descriptor, savefile_buffer, masterkey_array)
    return descriptor
    
def _unload_descriptor15(dll_lib, descriptor):
    dll_lib.editor_freeData.argtypes = [
        ctypes.POINTER(pes_data.FileDescriptor15)
    ]
    dll_lib.editor_freeData.restype = None
    dll_lib.editor_freeDescriptor15(descriptor)
    
def _unload_descriptorOld(dll_lib, descriptor):
    dll_lib.editor_freeData.argtypes = [
        ctypes.POINTER(pes_data.FileDescriptorOld)
    ]
    dll_lib.editor_freeData.restype = None
    dll_lib.editor_freeDescriptorOld(descriptor)
    
def _unload_descriptorNew(dll_lib, descriptor):
    dll_lib.editor_freeData.argtypes = [
        ctypes.POINTER(pes_data.FileDescriptorNew)
    ]
    dll_lib.editor_freeData.restype = None
    dll_lib.editor_freeDescriptorNew(descriptor)

def get_descriptor(dll_lib, version):
    version_type = pes_data.VERSION_TYPE[version]
    if version_type == "15":
        _get_descriptor15(dll_lib, version)
    elif version_type == "Old":
        _get_descriptorOld(dll_lib, version)
    elif version_type == "New":
        _get_descriptorNew(dll_lib, version)

def load_savefile17(dll_lib, optional_savefile_path=None):
    dll_lib.editor_loadData17.argtypes = [
        ctypes.c_char_p,
        ctypes.POINTER(ctypes.POINTER(pes_data.FileDescriptorOld)),
        ctypes.POINTER(ctypes.POINTER(pes_data.editor_player_entry)),
        ctypes.POINTER(ctypes.c_uint32),
        ctypes.POINTER(ctypes.POINTER(pes_data.editor_team_entry)),
        ctypes.POINTER(ctypes.c_uint32),
    ]
    dll_lib.editor_loadData17.restype = ctypes.c_int
    
    descriptor = ctypes.POINTER(pes_data.FileDescriptorOld)()
    players = ctypes.POINTER(pes_data.editor_player_entry)()
    teams = ctypes.POINTER(pes_data.editor_team_entry)()
    num_players = ctypes.c_uint32()
    num_teams = ctypes.c_uint32()
    path_to_encode = optional_savefile_path if optional_savefile_path is not None else pes_data.savefile_path
    encoded_path = path_to_encode.encode('utf-8')

    #ucrt = ctypes.CDLL('ucrtbase')
    result = dll_lib.editor_loadData17(encoded_path, ctypes.byref(descriptor), ctypes.byref(players), ctypes.byref(num_players), ctypes.byref(teams), ctypes.byref(num_teams))
    #ucrt.fflush(None) 
    if result != pes_data.OpResult.OK:
        raise RuntimeError(f"editor_loadData17 failed: {pes_data.OpResult(result).name}")
    return pes_data.SaveDataOld(descriptor=descriptor, players=players, num_players=num_players, teams=teams, num_teams=num_teams)
  
def save_savefile17(dll_lib, descriptor, players, teams, optional_savefile_path=None):
    dll_lib.editor_saveData17.argtypes = [
        ctypes.c_char_p,
        ctypes.POINTER(pes_data.FileDescriptorOld),
        ctypes.POINTER(pes_data.editor_player_entry),
        ctypes.POINTER(pes_data.editor_team_entry)
    ]
    dll_lib.editor_saveData17.restype = ctypes.c_int
    path_to_encode = optional_savefile_path if optional_savefile_path is not None else pes_data.savefile_path
    encoded_path = path_to_encode.encode('utf-8')
    
    result = dll_lib.editor_saveData17(encoded_path, descriptor, players, teams)
    if result != pes_data.OpResult.OK:
        raise RuntimeError(f"editor_saveData17 failed: {pes_data.OpResult(result).name}")
    return result
  
def unload_savefile_data(dll_lib, players, teams):
    dll_lib.editor_freeData.argtypes = [
        ctypes.POINTER(pes_data.editor_player_entry),
        ctypes.POINTER(pes_data.editor_team_entry),
    ]
    dll_lib.editor_freeData.restype = None
    dll_lib.editor_freeData(players, teams)
    
def unload_descriptor(dll_lib, descriptor, version):
    version_type = pes_data.VERSION_TYPE[version]
    if version_type == "15":
        _unload_descriptor15(dll_lib, descriptor)
    elif version_type == "Old":
        _unload_descriptorOld(dll_lib, descriptor)
    elif version_type == "New":
        _unload_descriptorNew(dll_lib, descriptor)
        
#####################################

def free_cache(dll_lib, cache):
    dll_lib.editor_freeCache.argtypes = [pes_data.EditorCache]
    dll_lib.editor_freeCache.restype = None
    dll_lib.editor_freeCache(cache)

def build_cache(dll_lib, players, num_players, teams, num_teams):
    out_cache = pes_data.EditorCache()
    dll_lib.editor_buildCache.argtypes = [
        ctypes.POINTER(pes_data.editor_player_entry),
        ctypes.c_uint32,
        ctypes.POINTER(pes_data.editor_team_entry),
        ctypes.c_uint32,
        ctypes.POINTER(pes_data.EditorCache), 
    ]
    dll_lib.editor_buildCache.restype = ctypes.c_int
    result = dll_lib.editor_buildCache(players, num_players, teams, num_teams, ctypes.byref(out_cache))
    return result, out_cache

def player_index_by_id(dll_lib, cache, player_id):
    out_index = ctypes.c_uint32()
    dll_lib.editor_playerIndexByID.argtypes = [
        pes_data.EditorCache,
        ctypes.c_uint32,  
        ctypes.POINTER(ctypes.c_uint32),
    ]
    dll_lib.editor_playerIndexByID.restype = ctypes.c_int
    result = dll_lib.editor_playerIndexByID(cache, player_id, ctypes.byref(out_index))
    return result, out_index.value

def team_index_by_id(dll_lib, cache, team_id):
    out_index = ctypes.c_uint32()
    dll_lib.editor_teamIndexByID.argtypes = [
        pes_data.EditorCache,
        ctypes.c_uint32,        
        ctypes.POINTER(ctypes.c_uint32), 
    ]
    dll_lib.editor_teamIndexByID.restype = ctypes.c_int
    result = dll_lib.editor_teamIndexByID(cache, team_id, ctypes.byref(out_index))
    return result, out_index.value

def player_indices_by_ids(dll_lib, cache, player_ids):
    count = len(player_ids)
    ids = (ctypes.c_uint32 * count)(*player_ids)
    out_indices = (ctypes.c_uint32 * count)()
    dll_lib.editor_playerIndicesByIDs.argtypes = [
        pes_data.EditorCache,
        ctypes.POINTER(ctypes.c_uint32),
        ctypes.c_uint32,          
        ctypes.POINTER(ctypes.c_uint32),
    ]
    dll_lib.editor_playerIndicesByIDs.restype = ctypes.c_int
    result = dll_lib.editor_playerIndicesByIDs(cache, ids, count, out_indices)
    return result, list(out_indices)

def team_indices_by_ids(dll_lib, cache, team_ids):
    count = len(team_ids)
    ids = (ctypes.c_uint32 * count)(*team_ids)
    out_indices = (ctypes.c_uint32 * count)()
    dll_lib.editor_teamIndicesByIDs.argtypes = [
        pes_data.EditorCache,
        ctypes.POINTER(ctypes.c_uint32),
        ctypes.c_uint32,      
        ctypes.POINTER(ctypes.c_uint32),
    ]
    dll_lib.editor_teamIndicesByIDs.restype = ctypes.c_int
    result = dll_lib.editor_teamIndicesByIDs(cache, ids, count, out_indices)
    return result, list(out_indices)

def get_team_player_indices(dll_lib, cache, team, max_count):
    out_indices = (ctypes.c_uint32 * max_count)()
    out_count = ctypes.c_uint32()
    dll_lib.editor_getTeamPlayerIndices.argtypes = [
        pes_data.EditorCache,
        ctypes.POINTER(pes_data.editor_team_entry),
        ctypes.POINTER(ctypes.c_uint32),
        ctypes.POINTER(ctypes.c_uint32),
    ]
    dll_lib.editor_getTeamPlayerIndices.restype = ctypes.c_int
    result = dll_lib.editor_getTeamPlayerIndices(cache, team, out_indices, ctypes.byref(out_count))
    return result, list(out_indices[:out_count.value])

def get_team_starting11_player_indices(dll_lib, cache, team, max_count=11):
    out_indices = (ctypes.c_uint32 * max_count)()
    out_count = ctypes.c_uint32()
    dll_lib.editor_getTeamStarting11PlayerIndices.argtypes = [
        pes_data.EditorCache,
        ctypes.POINTER(pes_data.editor_team_entry),
        ctypes.POINTER(ctypes.c_uint32),
        ctypes.POINTER(ctypes.c_uint32),
    ]
    dll_lib.editor_getTeamStarting11PlayerIndices.restype = ctypes.c_int
    result = dll_lib.editor_getTeamStarting11PlayerIndices(cache, team, out_indices, ctypes.byref(out_count))
    return result, list(out_indices[:out_count.value])
    
#####################################
    
def export_player_csv(dll_lib, player_id, players, cache, path):
    dll_lib.editor_export_player_csv.argtypes = [
        ctypes.c_uint32,
        ctypes.POINTER(pes_data.editor_player_entry),
        pes_data.EditorCache, 
        ctypes.c_char_p,
    ]
    dll_lib.editor_export_player_csv.restype = ctypes.c_int
    result = dll_lib.editor_export_player_csv(player_id, players, cache, path)
    return result
    
def export_team_players_csv(dll_lib, team_id, teams, players, cache, path):
    dll_lib.editor_export_team_players_csv.argtypes = [
        ctypes.c_uint32,
        ctypes.POINTER(pes_data.editor_team_entry),
        ctypes.POINTER(pes_data.editor_player_entry),
        pes_data.EditorCache, 
        ctypes.c_char_p,
    ]
    dll_lib.editor_export_team_players_csv.restype = ctypes.c_int
    result = dll_lib.editor_export_team_players_csv(team_id, teams, players, cache, path)
    return result
    
def export_team_starting11_csv(dll_lib, team_id, teams, players, cache, path):
    dll_lib.editor_export_team_starting11_csv.argtypes = [
        ctypes.c_uint32,
        ctypes.POINTER(pes_data.editor_team_entry),
        ctypes.POINTER(pes_data.editor_player_entry),
        pes_data.EditorCache, 
        ctypes.c_char_p,
    ]
    dll_lib.editor_export_team_starting11_csv.restype = ctypes.c_int
    result = dll_lib.editor_export_team_starting11_csv(team_id, teams, players, cache, path)
    return result
    
def import_players_csv(dll_lib, players, cache, path):
    dll_lib.editor_import_players_csv.argtypes = [
        ctypes.POINTER(pes_data.editor_player_entry),
        pes_data.EditorCache, 
        ctypes.c_char_p,
    ]
    dll_lib.editor_import_players_csv.restype = ctypes.c_int
    result = dll_lib.editor_import_players_csv(players, cache, path)
    return result
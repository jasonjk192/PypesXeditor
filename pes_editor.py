import pes_loader
import pes_data
import pes_schema

from abc import ABC, abstractmethod

try:
    import numpy as np
except ImportError:
    np = None

try:
    import pandas as pd
except ImportError:
    pd = None
    
class PESXEditor(ABC):
    VERSION = None

    def __init__(self, optional_savefile_path=None):
        self.dll_lib = pes_loader.load_dll()

        self.descriptor = None
        self.players = None
        self.num_players = None
        self.teams = None
        self.num_teams = None

        self._closed = False

        self._players_numpy = None
        self._teams_numpy = None
        self._players_df = None
        self._teams_df = None
        
        self._original_players = None
        self._original_teams = None
        
        self._cache = None

        result = self._load_savefile(optional_savefile_path)

        if result is None:
            # Since we already loaded the DLL, clean it up if appropriate.
            self._cleanup_failed_init()
            raise RuntimeError("load data failed")

        self.descriptor = result.descriptor
        self.players = result.players
        self.num_players = result.num_players
        self.teams = result.teams
        self.num_teams = result.num_teams
        self._take_snapshots()
        self._build_cache()

    @abstractmethod
    def _load_savefile(self, optional_savefile_path=None):
        """Load version-specific save data."""
        pass
        
    @abstractmethod
    def _save_savefile(self, optional_savefile_path=None):
        """Save version-specific save data."""
        pass

    @abstractmethod
    def _unload_descriptor(self):
        """Unload the version-specific descriptor."""
        pass

    def save(self):
        if self._closed:
            return
        if self.descriptor is None or self.players is None or self.teams is None:
            return
        self._update_changed_flags()
        result = self._save_savefile()
        if result != pes_data.OpResult.OK:
            raise RuntimeError(f"save failed: {pes_data.OpResult(result).name}")
        self._take_snapshots()
        
    def close(self):
        if self._closed:
            return
        self._closed = True

        if self.descriptor is not None:
            self._unload_descriptor()
        self.descriptor = None

        if self.players is not None or self.teams is not None:
            pes_loader.unload_savefile_data(self.dll_lib, self.players, self.teams)
            
        if self._cache is not None:
            self._free_cache()

        self.players = None
        self.teams = None
        self.num_players = None
        self.num_teams = None

        self._players_numpy = None
        self._teams_numpy = None
        self._players_df = None
        self._teams_df = None
        
        self._original_players = None
        self._original_teams = None
        
        self._cache = None

    def _cleanup_failed_init(self):
        """Cleanup resources if __init__ fails partway through."""
        if self.descriptor is not None:
            try:
                self._unload_descriptor()
            except Exception:
                pass

        if self.players is not None or self.teams is not None:
            try:
                pes_loader.unload_savefile_data(self.dll_lib, self.players, self.teams)
            except Exception:
                pass

        self.descriptor = None
        self.players = None
        self.teams = None

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.close()

    def __del__(self):
        try:
            self.close()
        except Exception:
            # Don't allow exceptions to escape from __del__
            pass
            
    def _snapshot_array(self, array, count):
        return [
            bytes(array[i])
            for i in range(count)
        ]

    def _take_snapshots(self):
        self._original_players = self._snapshot_array(
            self.players,
            self.num_players.value,
        )

        self._original_teams = self._snapshot_array(
            self.teams,
            self.num_teams.value,
        )
    
    def _mark_changed(self, array, original):
        for i, original_bytes in enumerate(original):
            if bytes(array[i]) != original_bytes:
                array[i].b_changed = 1

    def _update_changed_flags(self):
        self._mark_changed(self.players, self._original_players)
        self._mark_changed(self.teams, self._original_teams)
        
    def _build_cache(self):
        result = pes_loader.build_cache(self.dll_lib, self.players, self.num_players, self.teams, self.num_teams)
        self._cache = result[1]
    
    def _free_cache(self):
        pes_loader.free_cache(self.dll_lib, self._cache)
    
    @property
    def players_numpy(self):
        if self._players_numpy is not None:
            return self._players_numpy
        self._players_numpy = pes_schema.ctypes_to_numpy(self.players, self.num_players.value, pes_schema.PLAYER_SCHEMA)
        return self._players_numpy
    
    @property
    def teams_numpy(self):
        if self._teams_numpy is not None:
            return self._teams_numpy
        self._teams_numpy = pes_schema.ctypes_to_numpy(self.teams, self.num_teams.value, pes_schema.TEAM_SCHEMA)
        return self._teams_numpy
        
    def update_players_numpy(self):
        if self._players_numpy is None or self.players is None:
            return
        pes_schema.numpy_to_ctypes(self.players, self.num_players.value, self._players_numpy, pes_schema.PLAYER_SCHEMA)
        
    def update_teams_numpy(self):
        if self._teams_numpy is None or self.teams is None:
            return
        pes_schema.numpy_to_ctypes(self.teams, self.num_teams.value, self._teams_numpy, pes_schema.TEAM_SCHEMA)
        
    def get_team_index_by_id(self, team_id):
        result = pes_loader.team_index_by_id(self.dll_lib, self._cache, team_id)
        return result[1]
        
    def get_player_index_by_id(self, player_id):
        result = pes_loader.player_index_by_id(self.dll_lib, self._cache, player_id)
        return result[1]

    def get_player_indices_by_ids(self, player_ids):
        result = pes_loader.player_indices_by_ids(self.dll_lib, self._cache, player_ids)
        return result[1]
        
    def get_team_indices_by_ids(self, team_ids):
        result = pes_loader.team_indices_by_ids(self.dll_lib, self._cache, team_ids)
        return result[1]

    def get_team_player_indices(self, team_id):
        result = pes_loader.get_team_player_indices(self.dll_lib, self._cache, self.teams[self.get_team_index_by_id(team_id)], 40)
        return result[1]
    
    def get_team_starting11_player_indices(self, team_id):
        result = pes_loader.get_team_starting11_player_indices(self.dll_lib, self._cache, self.teams[self.get_team_index_by_id(team_id)], 11);
        return result[1]
        
    def export_player_csv(self, player_id, path):
        result = pes_loader.export_player_csv(self.dll_lib, player_id, self.players, self._cache, path)
        
    def export_team_players_csv(self, team_id, path):
        result = pes_loader.export_team_players_csv(self.dll_lib, team_id, self.teams, self.players, self._cache, path)
        
    def export_team_starting11_csv(self, team_id, path):
        result = pes_loader.export_team_starting11_csv(self.dll_lib, team_id, self.teams, self.players, self._cache, path)
        
    def import_players_csv(self, path):
        result = pes_loader.import_players_csv(self.dll_lib, self.players, self._cache, path)
    
class PES17Editor(PESXEditor):
    VERSION = 17

    def _load_savefile(self, optional_savefile_path=None):
        return pes_loader.load_savefile17(self.dll_lib, optional_savefile_path)

    def _unload_descriptor(self):
        pes_loader.unload_descriptor(self.dll_lib, self.descriptor, self.VERSION)
        
    def _save_savefile(self, optional_savefile_path=None):
        return pes_loader.save_savefile17(self.dll_lib, self.descriptor, self.players, self.teams, optional_savefile_path)
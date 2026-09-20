from collections.abc import Sequence


class PlayerReference:
    """
    A reference to a player ID stored inside a team entry.

    This is not the actual ctypes player structure. It provides convenient
    access to the corresponding player in the editor.
    """

    __slots__ = (
        "_editor",
        "_player_id",
    )

    def __init__(self, editor, player_id):
        self._editor = editor
        self._player_id = int(player_id)

    @property
    def id(self):
        return self._player_id

    def get_info(self):
        """
        Return the actual editor_player_entry corresponding to this ID.
        """
        try:
            return self._editor.players_by_id[self._player_id]
        except KeyError:
            raise KeyError(
                f"Player with ID {self._player_id} does not exist"
            ) from None

    @property
    def info(self):
        """
        Shorthand for get_info().
        """
        return self.get_info()

    def __int__(self):
        return self._player_id

    def __index__(self):
        return self._player_id

    def __eq__(self, other):
        if isinstance(other, PlayerReference):
            return self.id == other.id

        return self.id == other

    def __repr__(self):
        return f"PlayerReference(id={self.id})"


class TeamPlayersView(Sequence):
    """
    Python-facing view of the player IDs contained in a team.

    Instead of returning raw integers, indexing returns PlayerReference
    objects.
    """

    __slots__ = (
        "_editor",
        "_team",
    )

    def __init__(self, editor, team):
        self._editor = editor
        self._team = team

    def __len__(self):
        return len(self._team.players)

    def __getitem__(self, index):
        player_id = self._team.players[index]

        if isinstance(index, slice):
            return [
                PlayerReference(self._editor, value)
                for value in player_id
            ]

        return PlayerReference(self._editor, player_id)

    def __iter__(self):
        for player_id in self._team.players:
            yield PlayerReference(self._editor, player_id)


class TeamView:
    """
    Extended view of a single editor_team_entry.

    Unknown attributes are transparently forwarded to the underlying
    ctypes structure, so normal fields remain accessible.
    """

    __slots__ = (
        "_editor",
        "_team",
        "_players_view",
    )

    def __init__(self, editor, team):
        self._editor = editor
        self._team = team
        self._players_view = None

    @property
    def raw(self):
        """
        Return the underlying ctypes editor_team_entry.
        """
        return self._team

    @property
    def players(self):
        if self._players_view is None:
            self._players_view = TeamPlayersView(
                self._editor,
                self._team,
            )

        return self._players_view

    def __getattr__(self, name):
        return getattr(self._team, name)

    def __setattr__(self, name, value):
        if name in {
            "_editor",
            "_team",
            "_players_view",
        }:
            object.__setattr__(self, name, value)
            return

        setattr(self._team, name, value)

    def get_players(self):
        """
        Return all players currently assigned to this team.
        """
        return list(self.players)

    def __repr__(self):
        return f"TeamView(id={self.id})"


class TeamCollection(Sequence):
    """
    Extended collection providing TeamView objects.
    """

    __slots__ = (
        "_editor",
    )

    def __init__(self, editor):
        self._editor = editor

    def __len__(self):
        return self._editor.num_teams.value

    def __getitem__(self, index):
        teams = self._editor.teams

        if isinstance(index, slice):
            return [
                TeamView(self._editor, team)
                for team in teams[index]
            ]

        return TeamView(
            self._editor,
            teams[index],
        )

    def __iter__(self):
        for i in range(self._editor.num_teams):
            yield TeamView(
                self._editor,
                self._editor.teams[i],
            )


class PlayerView:
    """
    Extended view of an individual player.

    This currently mostly forwards to the underlying ctypes structure,
    but gives us a place to add player-specific convenience methods later.
    """

    __slots__ = (
        "_editor",
        "_player",
    )

    def __init__(self, editor, player):
        self._editor = editor
        self._player = player

    @property
    def raw(self):
        return self._player

    def __getattr__(self, name):
        return getattr(self._player, name)

    def __setattr__(self, name, value):
        if name in {
            "_editor",
            "_player",
        }:
            object.__setattr__(self, name, value)
            return

        setattr(self._player, name, value)

    def __repr__(self):
        return f"PlayerView(id={self.id})"


class PlayerCollection(Sequence):
    """
    Extended collection providing PlayerView objects.
    """

    __slots__ = (
        "_editor",
    )

    def __init__(self, editor):
        self._editor = editor

    def __len__(self):
        return self._editor.num_players.value

    def __getitem__(self, index):
        players = self._editor.players

        if isinstance(index, slice):
            return [
                PlayerView(self._editor, player)
                for player in players[index]
            ]

        return PlayerView(
            self._editor,
            players[index],
        )

    def __iter__(self):
        for i in range(self._editor.num_players):
            yield PlayerView(
                self._editor,
                self._editor.players[i],
            )


class PESXExtendedEditor:
    """
    High-level Python API built on top of PESXEditor.

    The underlying PESXEditor remains responsible for loading, saving,
    ctypes structures, NumPy conversion, etc.

    This class adds convenient relationships between those structures.
    """

    def __init__(self, editor):
        self._editor = editor

        self._players_by_id = None

        self._teams_view = TeamCollection(self._editor)
        self._players_view = PlayerCollection(self._editor)

    # ------------------------------------------------------------------
    # Core editor
    # ------------------------------------------------------------------

    @property
    def raw(self):
        """
        Return the underlying PESXEditor.
        """
        return self._editor

    # ------------------------------------------------------------------
    # Basic data
    # ------------------------------------------------------------------

    @property
    def descriptor(self):
        return self._editor.descriptor

    @property
    def num_players(self):
        return self._editor.num_players

    @property
    def num_teams(self):
        return self._editor.num_teams

    # ------------------------------------------------------------------
    # Extended collections
    # ------------------------------------------------------------------

    @property
    def players(self):
        return self._players_view

    @property
    def teams(self):
        return self._teams_view

    # ------------------------------------------------------------------
    # Player lookup
    # ------------------------------------------------------------------

    @property
    def players_by_id(self):
        """
        Dictionary mapping player ID -> raw ctypes player entry.

        Built lazily because not every user will need ID-based lookups.
        """
        if self._players_by_id is None:
            self._players_by_id = {
                int(self._editor.players[i].id):
                self._editor.players[i]
                for i in range(self._editor.num_players)
            }

        return self._players_by_id

    def get_player(self, player_id):
        """
        Return the raw player structure with the specified ID.
        """
        try:
            return self.players_by_id[int(player_id)]
        except KeyError:
            raise KeyError(
                f"Player with ID {player_id} does not exist"
            ) from None

    # ------------------------------------------------------------------
    # Saving
    # ------------------------------------------------------------------

    def save(self, *args, **kwargs):
        """
        Forward saving to the underlying editor.

        Any additional arguments are passed directly to PESXEditor.save().
        """
        result = self._editor.save(*args, **kwargs)

        # If saving can modify/reload the underlying data, invalidate
        # cached indexes here.
        self._players_by_id = None

        return result

    # ------------------------------------------------------------------
    # Attribute forwarding
    # ------------------------------------------------------------------

    def __getattr__(self, name):
        """
        Allow access to functionality that belongs to PESXEditor but
        hasn't been explicitly exposed above.

        For example:

            extended.players_numpy
            extended.teams_numpy
            extended.close()
        """
        return getattr(self._editor, name)

    def __repr__(self):
        return (
            f"{type(self).__name__}("
            f"players={self.num_players}, "
            f"teams={self.num_teams}"
            f")"
        )

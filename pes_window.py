import ctypes
import tkinter as tk
from tkinter import filedialog, ttk

from pes_editor import PES17Editor, PES21Editor


class PESApplication:

    def __init__(self):
        self.editor = None
        self.selected_player_index = None

        self.root = tk.Tk()
        self.root.title("PES Save Manager")
        self.root.geometry("1100x700")

        self.create_menu()
        self.create_tabs()

    # =========================================================
    # Menu
    # =========================================================

    def create_menu(self):
        menu_bar = tk.Menu(self.root)

        file_menu = tk.Menu(menu_bar, tearoff=0)

        # Autoload save
        autoload_menu = tk.Menu(file_menu, tearoff=0)

        autoload_menu.add_command(
            label="PES 17 save",
            command=self.autoload_pes17
        )

        autoload_menu.add_command(
            label="PES 21 save",
            command=self.autoload_pes21
        )

        file_menu.add_cascade(
            label="Autoload save",
            menu=autoload_menu
        )

        # Load savefile
        load_menu = tk.Menu(file_menu, tearoff=0)

        load_menu.add_command(
            label="PES 17 save",
            command=self.load_pes17
        )

        load_menu.add_command(
            label="PES 21 save",
            command=self.load_pes21
        )

        file_menu.add_cascade(
            label="Load savefile",
            menu=load_menu
        )

        file_menu.add_separator()
        
        file_menu.add_command(
            label="Save",
            command=self.save
        )

        file_menu.add_command(
            label="Save as...",
            command=self.save_as
        )

        file_menu.add_separator()

        file_menu.add_command(
            label="Exit",
            command=self.exit_application
        )

        menu_bar.add_cascade(
            label="File",
            menu=file_menu
        )
        # =========================================================
        # CSV menu
        # =========================================================

        csv_menu = tk.Menu(menu_bar, tearoff=0)

        csv_import_menu = tk.Menu(
            csv_menu,
            tearoff=0
        )

        csv_import_menu.add_command(
            label="Players",
            command=self.import_players_csv
        )

        csv_import_menu.add_command(
            label="Teams",
            command=self.import_teams_csv
        )

        csv_menu.add_cascade(
            label="Import",
            menu=csv_import_menu
        )

        csv_export_menu = tk.Menu(
            csv_menu,
            tearoff=0
        )

        csv_export_menu.add_command(
            label="Player",
            command=self.export_player_csv
        )

        csv_export_menu.add_command(
            label="Players",
            command=self.export_players_csv
        )

        csv_export_menu.add_separator()

        csv_export_menu.add_command(
            label="Team",
            command=self.export_team_csv
        )

        csv_export_menu.add_command(
            label="Teams",
            command=self.export_teams_csv
        )

        csv_export_menu.add_separator()

        csv_export_menu.add_command(
            label="Team players",
            command=self.export_team_players_csv
        )

        csv_export_menu.add_command(
            label="Team starting 11",
            command=self.export_team_starting11_csv
        )

        csv_menu.add_cascade(
            label="Export",
            menu=csv_export_menu
        )

        menu_bar.add_cascade(
            label="CSV",
            menu=csv_menu
        )


        self.root.config(menu=menu_bar)

    def show_player_import_dialog(self, imported_players, num_imported_players):
        dialog = tk.Toplevel(self.root)

        dialog.title("Import Players")
        dialog.geometry("1200x750")

        dialog.transient(self.root)
        dialog.grab_set()

        # ---------------------------------------------------------
        # Player selector
        # ---------------------------------------------------------

        selector_frame = ttk.Frame(dialog)
        selector_frame.pack(
            fill="x",
            padx=10,
            pady=10
        )

        ttk.Label(
            selector_frame,
            text="Player:"
        ).pack(
            side="left"
        )

        player_combo = ttk.Combobox(
            selector_frame,
            state="readonly",
            width=40
        )

        player_combo.pack(
            side="left",
            padx=10
        )
        
        # ---------------------------------------------------------
        # Lock
        # ---------------------------------------------------------
        
        lock_scroll = tk.BooleanVar(value=True)

        ttk.Checkbutton(
            selector_frame,
            text="Lock scrolling",
            variable=lock_scroll
        ).pack(
            side="right",
            padx=10
        )


        # ---------------------------------------------------------
        # Comparison area
        # ---------------------------------------------------------

        comparison_frame = ttk.Frame(dialog)
        comparison_frame.pack(
            fill="both",
            expand=True,
            padx=10,
            pady=10
        )

        existing_frame, existing_canvas, existing_scrollbar = self.create_scrollable_comparison_panel(
            comparison_frame,
            "Existing player"
        )

        imported_frame, imported_canvas,imported_scrollbar = self.create_scrollable_comparison_panel(
            comparison_frame,
            "Imported player"
        )
     
        def scroll_canvas(source, target, *args):
            source.yview(*args)

            if lock_scroll.get():
                position = source.yview()

                if position:
                    target.yview_moveto(position[0])


        existing_scrollbar.config(
            command=lambda *args: scroll_canvas(
                existing_canvas,
                imported_canvas,
                *args
            )
        )

        imported_scrollbar.config(
            command=lambda *args: scroll_canvas(
                imported_canvas,
                existing_canvas,
                *args
            )
        )

        def mousewheel(source, target, event):
            source.yview_scroll(
                int(-1 * (event.delta / 120)),
                "units"
            )

            if lock_scroll.get():
                position = source.yview()

                if position:
                    target.yview_moveto(position[0])

            return "break"

        existing_canvas.bind(
            "<MouseWheel>",
            lambda event: mousewheel(
                existing_canvas,
                imported_canvas,
                event
            )
        )

        imported_canvas.bind(
            "<MouseWheel>",
            lambda event: mousewheel(
                imported_canvas,
                existing_canvas,
                event
            )
        )


        # ---------------------------------------------------------
        # Buttons
        # ---------------------------------------------------------

        button_frame = ttk.Frame(dialog)
        button_frame.pack(
            fill="x",
            padx=10,
            pady=10
        )

        ttk.Button(
            button_frame,
            text="Cancel",
            command=dialog.destroy
        ).pack(
            side="right",
            padx=5
        )

        ttk.Button(
            button_frame,
            text="Confirm",
            command=dialog.destroy
        ).pack(
            side="right",
            padx=5
        )
        
        # ---------------------------------------------------------
        
        def on_import_player_selected(event):
            index = player_combo.current()

            if index < 0:
                return

            imported_player = imported_players[index]

            existing_index = (
                self.editor.get_player_index_by_id(
                    imported_player.id
                )
            )

            if existing_index < 0:
                return

            existing_player = self.editor.players[
                existing_index
            ]

            self.display_player_comparison(
                existing_frame,
                imported_frame,
                existing_player,
                imported_player
            )
        
        combo_values = []

        for i in range(num_imported_players.value):
            player = imported_players[i]

            combo_values.append(
                f"{player.id}    {player.data.name_string}"
            )

        player_combo["values"] = combo_values
        
        player_combo.bind(
            "<<ComboboxSelected>>",
            on_import_player_selected
        )
        
        if num_imported_players.value > 0:
            player_combo.current(0)
            on_import_player_selected(None)

    # =========================================================
    # Tabs
    # =========================================================

    def create_tabs(self):
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(
            fill="both",
            expand=True
        )

        self.teams_tab = ttk.Frame(self.notebook)
        self.players_tab = ttk.Frame(self.notebook)

        self.notebook.add(
            self.teams_tab,
            text="Teams"
        )

        self.notebook.add(
            self.players_tab,
            text="Players"
        )

        self.create_players_tab()

    # =========================================================
    # Players tab
    # =========================================================

    def create_players_tab(self):
        players_left = ttk.Frame(self.players_tab)
        players_left.pack(
            side="left",
            fill="y",
            padx=5,
            pady=5
        )

        players_right = ttk.Frame(self.players_tab)
        players_right.pack(
            side="left",
            fill="both",
            expand=True,
            padx=5,
            pady=5
        )

        # -----------------------------------------------------
        # Player list
        # -----------------------------------------------------

        self.player_listbox = tk.Listbox(
            players_left,
            selectmode=tk.EXTENDED,
            width=35
        )

        self.player_listbox.pack(
            side="left",
            fill="y"
        )

        player_scrollbar = ttk.Scrollbar(
            players_left,
            orient="vertical",
            command=self.player_listbox.yview
        )

        player_scrollbar.pack(
            side="right",
            fill="y"
        )

        self.player_listbox.config(
            yscrollcommand=player_scrollbar.set
        )

        self.player_listbox.bind(
            "<Button-1>",
            self.on_player_click
        )
        # -----------------------------------------------------
        # Player editor
        # -----------------------------------------------------

        self.create_player_editor(players_right)

    # =========================================================
    # Player editor
    # =========================================================

    def create_player_editor(self, parent):
        """
        Create a scrollable area for all player fields.
        """

        self.player_canvas = tk.Canvas(
            parent,
            highlightthickness=0
        )

        scrollbar = ttk.Scrollbar(
            parent,
            orient="vertical",
            command=self.player_canvas.yview
        )

        self.player_canvas.configure(
            yscrollcommand=scrollbar.set
        )

        scrollbar.pack(
            side="right",
            fill="y"
        )

        self.player_canvas.pack(
            side="left",
            fill="both",
            expand=True
        )

        self.player_fields_frame = ttk.Frame(
            self.player_canvas
        )

        self.player_canvas_window = self.player_canvas.create_window(
            (0, 0),
            window=self.player_fields_frame,
            anchor="nw"
        )

        self.player_fields_frame.bind(
            "<Configure>",
            lambda event: self.player_canvas.configure(
                scrollregion=self.player_canvas.bbox("all")
            )
        )

        self.player_canvas.bind(
            "<Configure>",
            self.resize_player_editor
        )

    def resize_player_editor(self, event):
        """
        Make the internal frame match the canvas width.
        """

        self.player_canvas.itemconfigure(
            self.player_canvas_window,
            width=event.width
        )

    # =========================================================
    # Editor management
    # =========================================================

    def close_current_editor(self):
        if self.editor is not None:
            self.editor.close()
            self.editor = None

        self.selected_player_index = None

        self.player_listbox.delete(
            0,
            tk.END
        )

        self.clear_player_editor()

    def load_editor(self, editor_class, filepath=None):
        self.close_current_editor()

        if filepath is None:
            self.editor = editor_class()
        else:
            self.editor = editor_class(filepath)

        print(f"Loaded {editor_class.__name__}")

        self.refresh_player_list()

    def get_csv_file(self, title):
        return filedialog.askopenfilename(
            title=title,
            filetypes=[
                ("CSV files", "*.csv"),
                ("All files", "*.*")
            ]
        )

    def get_csv_save_file(self, title):
        return filedialog.asksaveasfilename(
            title=title,
            defaultextension=".csv",
            filetypes=[
                ("CSV files", "*.csv"),
                ("All files", "*.*")
            ]
        )


    # =========================================================
    # Autoload
    # =========================================================

    def autoload_pes17(self):
        self.load_editor(PES17Editor)

    def autoload_pes21(self):
        self.load_editor(PES21Editor)

    # =========================================================
    # Load savefile
    # =========================================================

    def load_pes17(self):
        filepath = filedialog.askopenfilename(
            title="Load PES 17 save"
        )

        if filepath:
            self.load_editor(
                PES17Editor,
                filepath
            )

    def load_pes21(self):
        filepath = filedialog.askopenfilename(
            title="Load PES 21 save"
        )

        if filepath:
            self.load_editor(
                PES21Editor,
                filepath
            )
           
    # =========================================================
    # Save savefile
    # =========================================================
           
    def save(self):
        if self.editor is None:
            return

        self.editor.save()


    def save_as(self):
        if self.editor is None:
            return

        filepath = filedialog.asksaveasfilename(
            title="Save savefile"
        )

        if filepath:
            self.editor.save(filepath)

    # =========================================================
    # CSV
    # =========================================================
    
    def import_players_csv(self):
        if self.editor is None:
            return

        filepath = self.get_csv_file(
            "Import players CSV"
        )

        if not filepath:
            return

        imported_players, num_players = (
            self.editor.import_players_csv(filepath)
        )

        if num_players == 0:
            return

        self.show_player_import_dialog(imported_players, num_players)


    def import_teams_csv(self):
        if self.editor is None:
            return

        filepath = self.get_csv_file(
            "Import teams CSV"
        )

        if not filepath:
            return

        imported_teams, num_teams = (
            self.editor.import_teams_csv(filepath)
        )

        if num_teams == 0:
            return
        # self.show_team_import_dialog(imported_teams, num_teams)

            
    def export_player_csv(self):
        if self.editor is None:
            return

        selection = self.player_listbox.curselection()

        if len(selection) != 1:
            return

        index = selection[0]

        player = self.editor.players[index]

        filepath = self.get_csv_save_file(
            "Export player CSV"
        )

        if filepath:
            self.editor.export_player_csv(
                player.id,
                filepath
            )

    def export_players_csv(self):
        if self.editor is None:
            return

        selection = self.player_listbox.curselection()

        if not selection:
            return

        ids = [
            self.editor.players[index].id
            for index in selection
        ]

        filepath = self.get_csv_save_file(
            "Export players CSV"
        )

        if filepath:
            self.editor.export_players_csv(
                ids,
                filepath
            )

    def export_team_csv(self):
        if self.editor is None:
            return

        # TODO: obtain selected team ID

    def export_teams_csv(self):
        if self.editor is None:
            return

        # TODO: obtain selected team IDs
        
    def export_team_players_csv(self):
        if self.editor is None:
            return

        # TODO: obtain selected team ID
        
    def export_team_starting11_csv(self):
        if self.editor is None:
            return

        # TODO: obtain selected team ID



    # =========================================================
    # Player list
    # =========================================================

    def refresh_player_list(self):
        self.player_listbox.delete(
            0,
            tk.END
        )

        if self.editor is None:
            return

        for i in range(self.editor.num_players.value):
            player = self.editor.players[i]

            self.player_listbox.insert(
                tk.END,
                f"{player.id}    {player.data.name_string}"
            )

    def on_player_selected(self, event):
        selection = self.player_listbox.curselection()

        if not selection:
            return

        self.selected_player_index = selection[0]

        if self.editor is None:
            return

        player = self.editor.players[
            self.selected_player_index
        ]

        self.display_player(player)

    def on_player_click(self, event):
        index = self.player_listbox.nearest(event.y)

        if index < 0:
            return "break"

        # Ctrl is held on Windows/Linux when bit 0x0004 is set.
        ctrl_held = bool(event.state & 0x0004)

        if ctrl_held:
            # Toggle this player's selection.
            if index in self.player_listbox.curselection():
                self.player_listbox.selection_clear(index)
            else:
                self.player_listbox.selection_set(index)
        else:
            # Normal click = single selection.
            self.player_listbox.selection_clear(0, tk.END)
            self.player_listbox.selection_set(index)

        self.player_listbox.activate(index)
        self.player_listbox.see(index)

        self.update_player_selection_state()

        return "break"
        
    def update_player_selection_state(self):
        selection = self.player_listbox.curselection()

        if len(selection) == 1:
            # Later we'll show the editor here.
            self.show_player_fields()
            pass

        else:
            # Zero or multiple selected.
            # Later we'll hide the editor here.
            pass

    def show_player_fields(self):
        selection = self.player_listbox.curselection()

        if not selection:
            return

        self.selected_player_index = selection[0]

        if self.editor is None:
            return

        player = self.editor.players[
            self.selected_player_index
        ]

        self.display_player(player)

    # =========================================================
    # Display player
    # =========================================================

    def clear_player_editor(self):
        for widget in self.player_fields_frame.winfo_children():
            widget.destroy()

    def display_player(self, player):
        self.clear_player_editor()

        row = 0

        # -----------------------------------------------------
        # Player entry fields
        # -----------------------------------------------------

        # ID is deliberately read-only.
        self.create_readonly_field(
            row,
            "ID",
            player.id
        )

        row += 1

        # -----------------------------------------------------
        # editor_player_export fields
        # -----------------------------------------------------

        for field_name, field_type in player.data._fields_:

            # Internal fields used by 4ccEditor.
            if field_name.startswith("b_"):
                continue

            self.create_ctypes_field(
                row,
                player,
                field_name,
                field_type
            )

            row += 1

    # =========================================================
    # Field creation
    # =========================================================

    def create_readonly_field(self, row, label, value):
        ttk.Label(
            self.player_fields_frame,
            text=label
        ).grid(
            row=row,
            column=0,
            sticky="w",
            padx=10,
            pady=3
        )

        entry = ttk.Entry(
            self.player_fields_frame
        )

        entry.insert(
            0,
            str(value)
        )

        entry.configure(
            state="readonly"
        )

        entry.grid(
            row=row,
            column=1,
            sticky="ew",
            padx=10,
            pady=3
        )

        self.player_fields_frame.columnconfigure(
            1,
            weight=1
        )

    def create_ctypes_field(self, row, player, field_name, field_type    ):
        value = getattr(
            player.data,
            field_name
        )

        # -----------------------------------------------------
        # Name
        # -----------------------------------------------------

        if field_name == "name":
            self.create_entry_field(
                row,
                "name",
                player.data.name_string,
                lambda value: setattr(
                    player.data,
                    "name_string",
                    value
                )
            )

            return

        # -----------------------------------------------------
        # Shirt name
        # -----------------------------------------------------

        if field_name == "shirt_name":
            current_value = bytes(value).split(
                b"\0",
                1
            )[0].decode(
                "utf-8",
                errors="replace"
            )

            self.create_entry_field(
                row,
                field_name,
                current_value,
                lambda new_value: self.set_shirt_name(
                    player,
                    new_value
                )
            )

            return

        # -----------------------------------------------------
        # ctypes arrays
        # -----------------------------------------------------

        if issubclass(field_type, ctypes.Array):
            self.create_array_field(
                row,
                player,
                field_name,
                value
            )

            return

        # -----------------------------------------------------
        # Normal scalar field
        # -----------------------------------------------------

        self.create_entry_field(
            row,
            field_name,
            value,
            lambda new_value: self.set_scalar_field(
                player,
                field_name,
                field_type,
                new_value
            )
        )

    # =========================================================
    # Normal field
    # =========================================================

    def create_entry_field(self, row, field_name, value, setter):
        ttk.Label(self.player_fields_frame, text=field_name
        ).grid(
            row=row,
            column=0,
            sticky="w",
            padx=10,
            pady=3
        )

        entry = ttk.Entry( self.player_fields_frame)

        entry.insert(0, str(value))

        entry.grid(
            row=row,
            column=1,
            sticky="ew",
            padx=10,
            pady=3
        )

        entry.bind(
            "<FocusOut>",
            lambda event: self.commit_entry(
                entry,
                setter
            )
        )

        entry.bind(
            "<Return>",
            lambda event: self.commit_entry(
                entry,
                setter
            )
        )

        self.player_fields_frame.columnconfigure(
            1,
            weight=1
        )

    # =========================================================
    # Array field
    # =========================================================

    def create_array_field( self, row, player, field_name, value):
        ttk.Label( self.player_fields_frame, text=field_name
        ).grid(
            row=row,
            column=0,
            sticky="nw",
            padx=10,
            pady=3
        )

        array_frame = ttk.Frame(
            self.player_fields_frame
        )

        array_frame.grid(
            row=row,
            column=1,
            sticky="ew",
            padx=10,
            pady=3
        )

        for index in range(len(value)):
            entry = ttk.Entry(
                array_frame,
                width=8
            )

            entry.insert(
                0,
                str(value[index])
            )

            entry.pack(
                side="left",
                padx=2
            )

            entry.bind(
                "<FocusOut>",
                lambda event,
                e=entry,
                i=index:
                self.commit_array_entry(
                    e,
                    player,
                    field_name,
                    i
                )
            )

            entry.bind(
                "<Return>",
                lambda event,
                e=entry,
                i=index:
                self.commit_array_entry(
                    e,
                    player,
                    field_name,
                    i
                )
            )

    # =========================================================
    # Commit values
    # =========================================================

    def commit_entry(self, entry, setter):
        value = entry.get()

        try:
            setter(value)

        except ValueError:
            # Restore the old value if validation failed.
            self.bell()

    def commit_array_entry(self, entry, player, field_name, index):
        try:
            value = int(entry.get())

            array = getattr(
                player.data,
                field_name
            )

            array[index] = value

        except (ValueError, TypeError):
            self.bell()

    def set_scalar_field( self, player, field_name, field_type, value ):
        # All numeric fields in the structure currently
        # represented here can be converted to integers.
        if issubclass(
            field_type,
            ctypes._SimpleCData
        ):
            converted = field_type(value).value

            setattr(
                player.data,
                field_name,
                converted
            )

            return

        raise ValueError(
            f"Unsupported field type: {field_type}"
        )

    def set_shirt_name(self, player, value):
        encoded = value.encode(
            "utf-8"
        )

        if len(encoded) >= 21:
            raise ValueError(
                "Shirt name is too long"
            )

        player.data.shirt_name = (
            encoded + b"\0" * (21 - len(encoded))
        )

    # =========================================================
    # Comparison
    # =========================================================

    def create_scrollable_comparison_panel(self, parent, title):
        frame = ttk.LabelFrame(
            parent,
            text=title
        )

        frame.pack(
            side="left",
            fill="both",
            expand=True,
            padx=5
        )

        canvas = tk.Canvas(
            frame,
            highlightthickness=0
        )

        scrollbar = ttk.Scrollbar(
            frame,
            orient="vertical",
            command=canvas.yview
        )

        content = ttk.Frame(canvas)

        canvas.configure(
            yscrollcommand=scrollbar.set
        )

        scrollbar.pack(
            side="right",
            fill="y"
        )

        canvas.pack(
            side="left",
            fill="both",
            expand=True
        )

        canvas_window = canvas.create_window(
            (0, 0),
            window=content,
            anchor="nw"
        )

        # Update scrollable region when content changes.
        content.bind(
            "<Configure>",
            lambda event: canvas.configure(
                scrollregion=canvas.bbox("all")
            )
        )

        # Make the content frame follow the canvas width.
        canvas.bind(
            "<Configure>",
            lambda event: canvas.itemconfigure(
                canvas_window,
                width=event.width
            )
        )
        
        return content, canvas, scrollbar


    def get_player_field_value(self, player, field_name):
        if field_name == "name":
            return player.data.name_string

        value = getattr(
            player.data,
            field_name
        )

        if isinstance(value, ctypes.Array):
            return list(value)

        if isinstance(value, bytes):
            return value.rstrip(b"\0").decode(
                "utf-8",
                errors="replace"
            )

        return value
        
    def player_fields_equal( self, existing_player, imported_player, field_name):
        existing_value = self.get_player_field_value( existing_player, field_name)
        imported_value = self.get_player_field_value( imported_player, field_name)
        return existing_value == imported_value

    def display_player_comparison( self, existing_frame, imported_frame, existing_player, imported_player):
        for widget in existing_frame.winfo_children():
            widget.destroy()

        for widget in imported_frame.winfo_children():
            widget.destroy()

        row = 0

        # ID
        self.create_comparison_value(
            existing_frame,
            row,
            "ID",
            existing_player.id,
            False
        )

        self.create_comparison_value(
            imported_frame,
            row,
            "ID",
            imported_player.id,
            False
        )

        row += 1

        for field_name, field_type in (
            existing_player.data._fields_
        ):
            # Hide internal editor fields.
            if field_name.startswith("b_"):
                continue

            existing_value = self.get_player_field_value(
                existing_player,
                field_name
            )

            imported_value = self.get_player_field_value(
                imported_player,
                field_name
            )

            different = (
                existing_value != imported_value
            )

            self.create_comparison_value(
                existing_frame,
                row,
                field_name,
                existing_value,
                different
            )

            self.create_comparison_value(
                imported_frame,
                row,
                field_name,
                imported_value,
                different
            )

            row += 1

    def create_comparison_value( self, parent, row, field_name, value, different ):
        ttk.Label(
            parent,
            text=field_name
        ).grid(
            row=row,
            column=0,
            sticky="nw",
            padx=8,
            pady=3
        )

        if isinstance(value, list):
            value_text = ", ".join(
                str(v) for v in value
            )
        else:
            value_text = str(value)

        label = tk.Label(
            parent,
            text=value_text,
            anchor="w",
            justify="left",
            bg = "#ffe0e0" if different else "#ffffff"
        )

        label.grid(
            row=row,
            column=1,
            sticky="ew",
            padx=8,
            pady=3
        )

        parent.columnconfigure(
            1,
            weight=1
        )


    # =========================================================
    # Application
    # =========================================================

    def exit_application(self):
        self.close_current_editor()
        self.root.destroy()

    def run(self):
        self.root.mainloop()


if __name__ == "__main__":
    app = PESApplication()
    app.run()

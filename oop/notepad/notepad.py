import json
import os
import tkinter as tk
import tkinter.font as tkfont
from tkinter import colorchooser, filedialog, messagebox, ttk

# Menu: (label, method name, shown shortcut, key binding), None is a separator
MENU_ITEMS = [
    (
        "File",
        [
            ("New tab", "new_tab", "Ctrl+N", "<Control-n>"),
            ("Open...", "open_file", "Ctrl+O", "<Control-o>"),
            ("Save", "save_file", "Ctrl+S", "<Control-s>"),
            ("Save as...", "save_file_as", "Ctrl+Shift+S", "<Control-S>"),
            ("Close tab", "close_tab", "Ctrl+W", "<Control-w>"),
            None,
            ("Exit", "exit_app", "", None),
        ],
    ),
    (
        "Edit",
        [
            ("Undo", "undo", "Ctrl+Z", None),
            ("Redo", "redo", "Ctrl+Y", None),
            None,
            ("Find & Replace...", "open_find_dialog", "Ctrl+F", "<Control-f>"),
        ],
    ),
]

# Style buttons on the toolbar (label, tag name, button font)
STYLE_BUTTONS = [
    ("B", "bold", ("Arial", 12, "bold")),
    ("I", "italic", ("Arial", 12, "italic")),
    ("U", "underline", ("Arial", 12, "underline")),
]

# Find & Replace window: buttons (label, method name) and directions
DIALOG_BUTTONS = [
    ("Find next", "find_next"),
    ("Replace", "replace_one"),
    ("Replace all", "replace_all"),
]
DIRECTIONS = [("Up", "up"), ("Down", "down")]

# File types for the open and save windows
FILE_TYPES = [
    ("Styled text", "*.json"),
    ("Text files", "*.txt"),
    ("All files", "*.*"),
]

# Default style for the text that has no style
DEFAULT_FAMILY = "Arial"
DEFAULT_SIZE = 14
DEFAULT_COLOR = "#000000"
FONT_SIZES = [8, 9, 10, 11, 12, 14, 16, 18, 20, 24, 28, 32, 36, 48, 72]

# Every style is a separate tag, so they can overlap on the same text
# (family:Arial, size:14, color:#ff0000, bold, italic, underline)
# font:... is the tag that really draws the font, it is made from the others
# (Tk can use only one font for a character)
FAMILY_PREFIX = "family:"
SIZE_PREFIX = "size:"
COLOR_PREFIX = "color:"
FONT_PREFIX = "font:"
# Tags with no value, they are just on or off
STYLE_TAGS = ["bold", "italic", "underline"]

# Color palette
LIGHT_GRAY = "#D4D4D2"
SELECT_BLUE = "#3399FF"
WHITE = "white"
BLACK = "black"


class FindReplaceDialog(tk.Toplevel):
    """Window for finding and replacing text"""
    def __init__(self, app) -> None:
        """Setting up the window and the variables"""
        super().__init__(app)
        # The main window (needed to get the current text)
        self.app = app
        self.title("Find & Replace")
        self.resizable(False, False)
        # Keep this window above the main one
        self.transient(app)

        # Variables linked to the entries and buttons
        self.find_var = tk.StringVar()
        self.replace_var = tk.StringVar()
        self.direction = tk.StringVar(value="down")
        self.match_case = tk.BooleanVar(value=False)
        # Label for messages (Not found, Replaced...)
        self.status = tk.Label(self, text="", anchor="w")

        self.build_gui()

    def build_gui(self):
        """Build the Find & Replace window"""
        # Find row
        tk.Label(self, text="Find:").grid(row=0, column=0, sticky="e", padx=4, pady=4)
        find_entry = tk.Entry(self, textvariable=self.find_var, width=30)
        find_entry.grid(row=0, column=1, columnspan=2, padx=4)
        find_entry.focus_set()

        # Replace row
        tk.Label(self, text="Replace:").grid(row=1, column=0, sticky="e", padx=4)
        tk.Entry(self, textvariable=self.replace_var, width=30).grid(
            row=1, column=1, columnspan=2, padx=4
        )

        # Direction row (radio buttons from DIRECTIONS)
        tk.Label(self, text="Direction:").grid(row=2, column=0, sticky="e", padx=4)
        for column, (label, value) in enumerate(DIRECTIONS, start=1):
            tk.Radiobutton(
                self, text=label, variable=self.direction, value=value
            ).grid(row=2, column=column, sticky="w")

        # Match case checkbox
        tk.Checkbutton(self, text="Match case", variable=self.match_case).grid(
            row=3, column=1, sticky="w"
        )

        # Buttons from DIALOG_BUTTONS (getattr gets the method from its name)
        for row, (label, method) in enumerate(DIALOG_BUTTONS):
            tk.Button(self, text=label, width=12, command=getattr(self, method)).grid(
                row=row, column=3, padx=4, pady=2
            )

        # Message label at the bottom
        self.status.grid(row=4, column=0, columnspan=4, sticky="we", padx=4, pady=4)

    def find_next(self):
        """Find the text in the current tab, returns True if found"""
        text = self.app.current_text()
        query = self.find_var.get()
        # Check if there is something to look for
        if not query:
            self.status["text"] = "Type something to find"
            return False

        # Up starts from the start of the selection, down from its end
        # (if nothing is selected, from the cursor)
        backwards = self.direction.get() == "up"
        has_selection = bool(text.tag_ranges("sel"))
        if backwards:
            start = "sel.first" if has_selection else "insert"
            searches = [(start, "1.0"), ("end", "1.0")]
        else:
            start = "sel.last" if has_selection else "insert"
            searches = [(start, "end"), ("1.0", "end")]

        # length will get the size of the found text
        length = tk.IntVar()
        # Search from the start point, if nothing is found try from the other end (wrap around)
        for attempt, (start, stop) in enumerate(searches):
            position = text.search(
                query,
                start,
                stopindex=stop,
                backwards=backwards,
                nocase=not self.match_case.get(),
                count=length,
            )
            if position:
                break

        # Nothing found even after the wrap around
        if not position:
            self.status["text"] = "Not found"
            return False

        # Get the end of the found text
        end = f"{position}+{length.get()}c"
        # Select the found text (remove the old selection first)
        text.tag_remove("sel", "1.0", "end")
        text.tag_add("sel", position, end)
        # Put the cursor at the start (up) or at the end (down)
        text.mark_set("insert", position if backwards else end)
        # Scroll to the found text
        text.see(position)
        # attempt is 1 only if the wrap around search found it
        self.status["text"] = "Wrapped around" if attempt else ""
        return True

    def replace_range(self, text, start, end):
        """Replace start-end with the new text, returns the index after it"""
        # Get the tags of the old text (except the selection) to keep its style
        tags = [tag for tag in text.tag_names(start) if tag != "sel"]
        # Delete the old text and insert the new one with the same tags
        text.delete(start, end)
        text.insert(start, self.replace_var.get(), tuple(tags))
        # Mark the text as changed
        text.edit_modified(True)
        # Get the index after the new text
        return text.index(f"{start}+{len(self.replace_var.get())}c")

    def replace_one(self):
        """Replace the selected text if it matches, then find the next one"""
        text = self.app.current_text()
        query = self.find_var.get()
        if not query:
            return

        # Replace only if the selection is the searched text
        if text.tag_ranges("sel"):
            selected = text.get("sel.first", "sel.last")
            # Compare with or without the case
            if self.match_case.get():
                same = selected == query
            else:
                same = selected.lower() == query.lower()

            if same:
                new_end = self.replace_range(
                    text, text.index("sel.first"), text.index("sel.last")
                )
                text.mark_set("insert", new_end)
        # Jump to the next match
        self.find_next()

    def replace_all(self):
        """Replace all the matches in the current tab"""
        text = self.app.current_text()
        query = self.find_var.get()
        if not query:
            self.status["text"] = "Type something to find"
            return

        # count = replaced matches, position = where to search from
        count = 0
        position = "1.0"
        length = tk.IntVar()
        # Search until there are no matches left
        while True:
            found = text.search(
                query,
                position,
                stopindex="end",
                nocase=not self.match_case.get(),
                count=length,
            )
            if not found:
                break

            # Continue after the new text, or replacing "a" with "aa" would loop forever
            position = self.replace_range(text, found, f"{found}+{length.get()}c")
            count += 1

        # Show how many were replaced
        self.status["text"] = f"Replaced {count} occurrence(s)"


class Notepad(tk.Tk):
    """The main window"""
    def __init__(self) -> None:
        """Setting up the window and the variables"""
        super().__init__()
        # Window settings
        self.title("Notepad")
        self.geometry("900x600")
        self.minsize(500, 300)

        # Open tabs (tab id: {"text": Text widget, "path": file path})
        self.tabs = {}
        # Key bindings, filled by build_menu
        self.shortcuts = []
        # The Find & Replace window (None until it is opened)
        self.find_dialog = None

        # Let the tabs (row 1) take all the space when resizing
        self.rowconfigure(1, weight=1)
        self.columnconfigure(0, weight=1)

        # Build the menu, the toolbar with the tabs and the key bindings
        self.build_menu()
        self.build_gui()
        self.bind_shortcuts(self)
        # Closing the window runs exit_app (asks to save first)
        self.protocol("WM_DELETE_WINDOW", self.exit_app)
        # Start with one empty tab
        self.new_tab()

    def build_menu(self):
        """Build the menu bar from MENU_ITEMS"""
        menu_bar = tk.Menu(self)
        # Loop for every menu (File, Edit)
        for title, items in MENU_ITEMS:
            menu = tk.Menu(menu_bar, tearoff=False)
            # Loop for every item of the menu
            for item in items:
                # None means a separator line
                if item is None:
                    menu.add_separator()
                    continue

                # Unpack the item
                label, method, accelerator, sequence = item
                # Add the item (getattr gets the method from its name)
                menu.add_command(
                    label=label,
                    accelerator=accelerator,
                    command=getattr(self, method),
                )
                # Save the key binding, it is bound later in bind_shortcuts
                if sequence:
                    self.shortcuts.append((sequence, method))
            # Add the menu to the bar
            menu_bar.add_cascade(label=title, menu=menu)
        # Show the menu bar
        self.config(menu=menu_bar)

    def build_gui(self):
        """Build the toolbar and the tabs holder"""
        # Variables linked to the font comboboxes
        self.family_var = tk.StringVar(value=DEFAULT_FAMILY)
        self.size_var = tk.StringVar(value=str(DEFAULT_SIZE))

        # Toolbar (font family, size, B I U and color)
        toolbar = tk.Frame(self, background=LIGHT_GRAY)
        toolbar.grid(row=0, column=0, sticky="we")

        # Font family (pick only, from all the fonts of the system)
        family_box = ttk.Combobox(
            toolbar,
            textvariable=self.family_var,
            values=sorted(set(tkfont.families())),
            width=24,
            state="readonly",
        )
        family_box.grid(row=0, column=0, padx=4, pady=4)
        # Apply the font to the selected text when picked
        family_box.bind(
            "<<ComboboxSelected>>",
            lambda event: self.apply_exclusive(FAMILY_PREFIX, self.family_var.get()),
        )

        # Font size (can be typed too)
        size_box = ttk.Combobox(
            toolbar, textvariable=self.size_var, values=FONT_SIZES, width=4
        )
        size_box.grid(row=0, column=1, padx=4)
        # Apply the size when picked or when Enter is pressed
        size_box.bind("<<ComboboxSelected>>", self.size_changed)
        size_box.bind("<Return>", self.size_changed)

        # B, I and U buttons from STYLE_BUTTONS (tag=tag keeps the tag of each button)
        for column, (label, tag, button_font) in enumerate(STYLE_BUTTONS, start=2):
            button = tk.Button(
                toolbar,
                text=label,
                font=button_font,
                width=3,
                command=lambda tag=tag: self.toggle_style(tag),
            )
            button.grid(row=0, column=column, padx=1)

        # Color button
        color_button = tk.Button(
            toolbar, text="Color", font=("Arial", 12), command=self.choose_color
        )
        color_button.grid(row=0, column=len(STYLE_BUTTONS) + 2, padx=4)

        # Tabs holder
        self.notebook = ttk.Notebook(self)
        self.notebook.grid(row=1, column=0, sticky="nsew")
        # Run tab_changed when another tab is selected
        self.notebook.bind("<<NotebookTabChanged>>", self.tab_changed)

    def bind_shortcuts(self, widget):
        """Bind all the key shortcuts to a widget"""
        for sequence, name in self.shortcuts:
            # name=name keeps the name of each shortcut (same trick as in the calculator)
            widget.bind(sequence, lambda event, name=name: self.run_shortcut(name))

    def run_shortcut(self, name):
        """Run the method with this name"""
        getattr(self, name)()
        # Returning "break" stops the default Tk key actions (Ctrl+O would add a new line)
        return "break"

    def new_tab(self):
        """Create a new empty tab"""
        # Every tab is a frame with a text and a scrollbar
        frame = tk.Frame(self.notebook)
        # Text (the last 2 options keep the selection visible when it is not focused)
        text = tk.Text(
            frame,
            font=(DEFAULT_FAMILY, DEFAULT_SIZE),
            background=WHITE,
            foreground=BLACK,
            wrap="word",
            undo=True,
            padx=6,
            pady=6,
            exportselection=False,
            inactiveselectbackground=SELECT_BLUE,
        )
        # Scrollbar linked to the text
        scrollbar = tk.Scrollbar(frame, command=text.yview)
        text.config(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        text.pack(side="left", fill="both", expand=True)

        # Tag that draws the underline
        text.tag_configure("underline", underline=True)
        # Key bindings for this text too (Text has its own actions for some keys)
        self.bind_shortcuts(text)

        # Save the tab (the name of the frame is the key)
        self.tabs[str(frame)] = {"text": text, "path": None}
        # Add the tab and select it
        self.notebook.add(frame, text="Untitled")
        self.notebook.select(frame)
        # A new tab has no changes
        text.edit_modified(False)
        text.focus_set()

    def current_tab(self):
        """Get the data of the selected tab"""
        return self.tabs[self.notebook.select()]

    def current_text(self):
        """Get the text of the selected tab"""
        return self.current_tab()["text"]

    def is_blank_tab(self):
        """Check if the selected tab is empty and untouched"""
        tab = self.current_tab()
        text = tab["text"]
        # No file, no changes and no text
        return (
            tab["path"] is None
            and not text.edit_modified()
            and text.get("1.0", "end-1c") == ""
        )

    def set_tab_title(self, path):
        """Set the tab title and the window title from the file name"""
        # Use the file name, or Untitled if there is no file
        name = os.path.basename(path) if path else "Untitled"
        self.notebook.tab(self.notebook.select(), text=name)
        self.title(f"Notepad - {name}")

    def tab_changed(self, event=None):
        """Update the title and the focus when the tab changes"""
        # Skip if there are no tabs
        if self.tabs:
            self.set_tab_title(self.current_tab()["path"])
            self.current_text().focus_set()

    def close_tab(self):
        """Close the selected tab, returns False if the user cancels"""
        tab = self.current_tab()

        # Ask to save if there are unsaved changes
        if tab["text"].edit_modified():
            answer = messagebox.askyesnocancel("Notepad", "Save changes before closing?")
            # Cancel, so do not close
            if answer is None:
                return False
            # Yes means save first, if the saving fails do not close
            if answer and not self.save_file():
                return False

        # Remove the tab and its data
        key = self.notebook.select()
        self.notebook.forget(key)
        self.tabs.pop(key)
        self.nametowidget(key).destroy()

        # Keep at least one tab open
        if not self.tabs:
            self.new_tab()
        return True

    def exit_app(self):
        """Close all the tabs one by one, then the window"""
        # list() makes a copy, because the tabs are removed inside the loop
        for key in list(self.tabs):
            self.notebook.select(key)
            # Stop if the user cancels
            if not self.close_tab():
                return
        self.destroy()

    def open_file(self):
        """Open a file in a tab"""
        # Ask for the file
        path = filedialog.askopenfilename(filetypes=FILE_TYPES)
        if not path:
            return

        # Try to read the file
        try:
            with open(path, "r", encoding="utf-8", errors="replace") as file:
                content = file.read()
        except OSError as error:
            messagebox.showerror("Error", str(error))
            return

        # Use the empty tab, if there is one, instead of opening another
        if not self.is_blank_tab():
            self.new_tab()

        # Put the content into the tab
        tab = self.current_tab()
        text = tab["text"]
        # json files have the text and the styles, the others are plain text
        if path.lower().endswith(".json"):
            try:
                self.json_to_text(content, text)
            except (ValueError, KeyError, TypeError, tk.TclError):
                messagebox.showerror("Error", "Not a valid styled text file")
                return
        else:
            text.insert("1.0", content)

        # Save the path and set the titles
        tab["path"] = path
        self.set_tab_title(path)
        # Clear the undo history and the changed flag (so Ctrl+Z does not undo the opening)
        text.edit_reset()
        text.edit_modified(False)

    def save_file(self):
        """Save the tab, asks for a path if it has none"""
        path = self.current_tab()["path"]
        # No path yet, so it works like Save as
        if path is None:
            return self.save_file_as()
        return self.write_file(path)

    def save_file_as(self):
        """Ask for a path and save the tab there"""
        path = filedialog.asksaveasfilename(
            defaultextension=".json", filetypes=FILE_TYPES
        )
        # The user cancelled
        if not path:
            return False
        return self.write_file(path)

    def write_file(self, path):
        """Write the content of the tab to the path, returns True if it worked"""
        tab = self.current_tab()
        text = tab["text"]
        # Try to write the file
        try:
            # json keeps the styles, the others save just the text
            if path.lower().endswith(".json"):
                content = self.text_to_json(text)
            else:
                content = text.get("1.0", "end-1c")

            with open(path, "w", encoding="utf-8") as file:
                file.write(content)
        except OSError as error:
            messagebox.showerror("Error", str(error))
            return False

        # The tab belongs to this file now
        tab["path"] = path
        self.set_tab_title(path)
        # Saved, so there are no unsaved changes
        text.edit_modified(False)
        return True

    def undo(self):
        """Undo the last change"""
        try:
            self.current_text().edit_undo()
        except tk.TclError:
            # Nothing to undo
            pass

    def redo(self):
        """Redo the last undone change"""
        try:
            self.current_text().edit_redo()
        except tk.TclError:
            # Nothing to redo
            pass

    def open_find_dialog(self):
        """Open the Find & Replace window (only one at a time)"""
        # If it is already open, just bring it to the front
        if self.find_dialog is not None and self.find_dialog.winfo_exists():
            self.find_dialog.lift()
            return
        self.find_dialog = FindReplaceDialog(self)

    def get_selection(self, text):
        """Get the start and the end of the selection, None if nothing is selected"""
        try:
            return text.index("sel.first"), text.index("sel.last")
        except tk.TclError:
            # Nothing is selected
            return None

    def get_style(self, tags):
        """Get the style values from a list of tags (defaults if a tag is missing)"""
        # Start with the defaults
        family, size, color = DEFAULT_FAMILY, DEFAULT_SIZE, DEFAULT_COLOR
        # Cut the prefix off the tag to get its value (size:14 gives 14)
        for tag in tags:
            if tag.startswith(FAMILY_PREFIX):
                family = tag[len(FAMILY_PREFIX):]
            elif tag.startswith(SIZE_PREFIX):
                size = int(tag[len(SIZE_PREFIX):])
            elif tag.startswith(COLOR_PREFIX):
                color = tag[len(COLOR_PREFIX):]
        # bold, italic and underline have no value, they are just there or not
        return family, size, "bold" in tags, "italic" in tags, "underline" in tags, color

    def apply_exclusive(self, prefix, value):
        """Apply family, size or color to the selection (one value at a time)"""
        text = self.current_text()
        # Get the selection
        selection = self.get_selection(text)
        if selection is None:
            return

        start, end = selection
        # Remove the old tags with this prefix (e.g. every size:)
        for tag in text.tag_names():
            if tag.startswith(prefix):
                text.tag_remove(tag, start, end)

        # Add the new tag
        new_tag = prefix + str(value)
        text.tag_add(new_tag, start, end)
        # Color tags draw by themselves, the others need the combined font tag
        if prefix == COLOR_PREFIX:
            text.tag_configure(new_tag, foreground=value)
        else:
            self.refresh_fonts(text, start, end)

        # Mark as changed and give the focus back to the text
        text.edit_modified(True)
        text.focus_set()

    def toggle_style(self, name):
        """Turn bold, italic or underline on or off for the selection"""
        # The first selected character decides: if it has the style, remove it from all
        text = self.current_text()
        selection = self.get_selection(text)
        if selection is None:
            return

        start, end = selection
        if name in text.tag_names(start):
            text.tag_remove(name, start, end)
        else:
            text.tag_add(name, start, end)

        # Underline draws by itself, bold and italic need the combined font tag
        if name != "underline":
            self.refresh_fonts(text, start, end)

        # Mark as changed and give the focus back to the text
        text.edit_modified(True)
        text.focus_set()

    def size_changed(self, event=None):
        """Apply the size from the combobox"""
        # The size can be typed, so check that it is a number
        try:
            size = int(self.size_var.get())
        except ValueError:
            return
        # Only positive sizes
        if size > 0:
            self.apply_exclusive(SIZE_PREFIX, size)

    def choose_color(self):
        """Open the color picker and apply the color"""
        # askcolor gives ((r, g, b), "#rrggbb"), take the hex one
        color = colorchooser.askcolor(parent=self)[1]
        # It is empty if the user cancels
        if color:
            self.apply_exclusive(COLOR_PREFIX, color)

    def refresh_fonts(self, text, start, end):
        """Rebuild the combined font tag of every character from start to end"""
        # Go through the characters one by one
        index = text.index(start)
        while text.compare(index, "<", end):
            # Get the style of this character from its tags
            tags = text.tag_names(index)
            family, size, bold, italic, underline, color = self.get_style(tags)

            # Name of the combined tag (e.g. font:Arial|14|1|0)
            name = f"{FONT_PREFIX}{family}|{size}|{int(bold)}|{int(italic)}"
            # Bold and italic go into the font as words
            styles = [style for style, on in (("bold", bold), ("italic", italic)) if on]
            # Make the tag draw this font
            text.tag_configure(name, font=(family, size, *styles))

            # Remove the old combined tag
            for tag in tags:
                if tag.startswith(FONT_PREFIX) and tag != name:
                    text.tag_remove(tag, index)
            # Add the new combined tag
            text.tag_add(name, index)

            # Move to the next character
            index = text.index(f"{index}+1c")

    def text_to_json(self, text):
        """Make the json text from the text and its styles"""
        # Save only the style tags (the font: tags are made again when opening)
        tags = []
        for name in text.tag_names():
            # Style tags are bold, italic, underline and the ones with a prefix
            is_style = name in STYLE_TAGS or name.startswith(
                (FAMILY_PREFIX, SIZE_PREFIX, COLOR_PREFIX)
            )
            if is_style:
                ranges = text.tag_ranges(name)
                # tag_ranges gives start, end, start, end..., so go 2 by 2
                for i in range(0, len(ranges), 2):
                    tags.append([name, str(ranges[i]), str(ranges[i + 1])])

        # Put the text and the tags together
        data = {"text": text.get("1.0", "end-1c"), "tags": tags}
        return json.dumps(data, ensure_ascii=False)

    def json_to_text(self, content, text):
        """Put the text and the styles from the json content into the text"""
        # Read the json (it raises an error if the file is not valid)
        data = json.loads(content)
        # Insert the text first, the tags need it to exist
        text.insert("1.0", data["text"])

        # Add every style tag back
        for name, start, end in data["tags"]:
            text.tag_add(name, start, end)
            # Color tags need their color set again
            if name.startswith(COLOR_PREFIX):
                text.tag_configure(name, foreground=name[len(COLOR_PREFIX):])

        # Make the combined font tags
        self.refresh_fonts(text, "1.0", "end-1c")

    def center_window(self):
        # Get window and screen width and height
        window_height = self.winfo_height()
        window_width = self.winfo_width()
        screen_height = self.winfo_screenheight()
        screen_width = self.winfo_screenwidth()

        # Calculate the (x,y) coords to center the window on the screen later
        window_x = int((screen_width / 2) - (window_width / 2))
        window_y = int((screen_height / 2) - (window_height / 2))

        # Center the windows on the user's screen (check the format below)
        # format "(w)x(h)+(x)+(y)"
        self.geometry(f"{window_width}x{window_height}+{window_x}+{window_y}")


# Run the app
app = Notepad()
app.update()
app.center_window()

app.mainloop()
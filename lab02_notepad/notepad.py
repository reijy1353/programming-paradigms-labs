import json
import os
import tkinter as tk
import tkinter.font as tkfont
from tkinter import colorchooser, filedialog, messagebox, ttk

# Menu layout: (label, method name, shown shortcut, key binding). None is a separator
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

# Toolbar buttons: (label, tag name, font of the button)
STYLE_BUTTONS = [
    ("B", "bold", ("Arial", 12, "bold")),
    ("I", "italic", ("Arial", 12, "italic")),
    ("U", "underline", ("Arial", 12, "underline")),
]

# Find & Replace dialog: buttons (label, method name) and search directions
DIALOG_BUTTONS = [
    ("Find next", "find_next"),
    ("Replace", "replace_one"),
    ("Replace all", "replace_all"),
]
DIRECTIONS = [("Up", "up"), ("Down", "down")]

# Open/Save dialog file types
FILE_TYPES = [
    ("Styled text", "*.json"),
    ("Text files", "*.txt"),
    ("All files", "*.*"),
]

# Defaults for text that has no style applied
DEFAULT_FAMILY = "Arial"
DEFAULT_SIZE = 14
DEFAULT_COLOR = "#000000"
FONT_SIZES = [8, 9, 10, 11, 12, 14, 16, 18, 20, 24, 28, 32, 36, 48, 72]

# Every style lives in its own tag, so styles can overlap on the same text:
#   family:Arial  size:14  color:#ff0000  bold  italic  underline
# font:... is a combined tag (family + size + bold + italic) built from the others,
# because Tk can only draw ONE font per character
FAMILY_PREFIX = "family:"
SIZE_PREFIX = "size:"
COLOR_PREFIX = "color:"
FONT_PREFIX = "font:"
STYLE_TAGS = ["bold", "italic", "underline"]

# Color palette
LIGHT_GRAY = "#D4D4D2"
SELECT_BLUE = "#3399FF"
WHITE = "white"
BLACK = "black"


class FindReplaceDialog(tk.Toplevel):
    def __init__(self, app) -> None:
        super().__init__(app)
        self.app = app
        self.title("Find & Replace")
        self.resizable(False, False)
        self.transient(app)

        self.find_var = tk.StringVar()
        self.replace_var = tk.StringVar()
        self.direction = tk.StringVar(value="down")
        self.match_case = tk.BooleanVar(value=False)
        self.status = tk.Label(self, text="", anchor="w")

        self.build_gui()

    def build_gui(self):
        tk.Label(self, text="Find:").grid(row=0, column=0, sticky="e", padx=4, pady=4)
        find_entry = tk.Entry(self, textvariable=self.find_var, width=30)
        find_entry.grid(row=0, column=1, columnspan=2, padx=4)
        find_entry.focus_set()

        tk.Label(self, text="Replace:").grid(row=1, column=0, sticky="e", padx=4)
        tk.Entry(self, textvariable=self.replace_var, width=30).grid(
            row=1, column=1, columnspan=2, padx=4
        )

        tk.Label(self, text="Direction:").grid(row=2, column=0, sticky="e", padx=4)
        for column, (label, value) in enumerate(DIRECTIONS, start=1):
            tk.Radiobutton(
                self, text=label, variable=self.direction, value=value
            ).grid(row=2, column=column, sticky="w")

        tk.Checkbutton(self, text="Match case", variable=self.match_case).grid(
            row=3, column=1, sticky="w"
        )

        for row, (label, method) in enumerate(DIALOG_BUTTONS):
            tk.Button(self, text=label, width=12, command=getattr(self, method)).grid(
                row=row, column=3, padx=4, pady=2
            )

        self.status.grid(row=4, column=0, columnspan=4, sticky="we", padx=4, pady=4)

    def find_next(self):
        text = self.app.current_text()
        query = self.find_var.get()
        if not query:
            self.status["text"] = "Type something to find"
            return False

        # Going up starts at the beginning of the selection, going down at its end
        backwards = self.direction.get() == "up"
        has_selection = bool(text.tag_ranges("sel"))
        if backwards:
            start = "sel.first" if has_selection else "insert"
            stop = "1.0"
        else:
            start = "sel.last" if has_selection else "insert"
            stop = "end"

        length = tk.IntVar()
        position = text.search(
            query,
            start,
            stopindex=stop,
            backwards=backwards,
            nocase=not self.match_case.get(),
            count=length,
        )
        if not position:
            self.status["text"] = "Not found"
            return False

        end = f"{position}+{length.get()}c"
        text.tag_remove("sel", "1.0", "end")
        text.tag_add("sel", position, end)
        text.mark_set("insert", position if backwards else end)
        text.see(position)
        self.status["text"] = ""
        return True

    def replace_range(self, text, start, end):
        # Keep the style of the replaced text (but not the selection)
        tags = [tag for tag in text.tag_names(start) if tag != "sel"]
        text.delete(start, end)
        text.insert(start, self.replace_var.get(), tuple(tags))
        text.edit_modified(True)
        return text.index(f"{start}+{len(self.replace_var.get())}c")

    def replace_one(self):
        text = self.app.current_text()
        query = self.find_var.get()
        if not query:
            return

        # Replace only if the current selection IS the searched text, then jump on
        if text.tag_ranges("sel"):
            selected = text.get("sel.first", "sel.last")
            if self.match_case.get():
                same = selected == query
            else:
                same = selected.lower() == query.lower()

            if same:
                new_end = self.replace_range(
                    text, text.index("sel.first"), text.index("sel.last")
                )
                text.mark_set("insert", new_end)
        self.find_next()

    def replace_all(self):
        text = self.app.current_text()
        query = self.find_var.get()
        if not query:
            self.status["text"] = "Type something to find"
            return

        count = 0
        position = "1.0"
        length = tk.IntVar()
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

            # Continue AFTER the replacement, or "a" -> "aa" would loop forever
            position = self.replace_range(text, found, f"{found}+{length.get()}c")
            count += 1

        self.status["text"] = f"Replaced {count} occurrence(s)"


class Notepad(tk.Tk):
    def __init__(self) -> None:
        super().__init__()
        self.title("Notepad")
        self.geometry("900x600")
        self.minsize(500, 300)

        # Open tabs: notebook tab id -> {"text": Text widget, "path": file path}
        self.tabs = {}
        self.shortcuts = []
        self.find_dialog = None

        self.rowconfigure(1, weight=1)
        self.columnconfigure(0, weight=1)

        self.build_menu()
        self.build_gui()
        self.bind_shortcuts(self)
        self.protocol("WM_DELETE_WINDOW", self.exit_app)
        self.new_tab()

    def build_menu(self):
        menu_bar = tk.Menu(self)
        for title, items in MENU_ITEMS:
            menu = tk.Menu(menu_bar, tearoff=False)
            for item in items:
                if item is None:
                    menu.add_separator()
                    continue

                label, method, accelerator, sequence = item
                menu.add_command(
                    label=label,
                    accelerator=accelerator,
                    command=getattr(self, method),
                )
                if sequence:
                    self.shortcuts.append((sequence, method))
            menu_bar.add_cascade(label=title, menu=menu)
        self.config(menu=menu_bar)

    def build_gui(self):
        self.family_var = tk.StringVar(value=DEFAULT_FAMILY)
        self.size_var = tk.StringVar(value=str(DEFAULT_SIZE))

        # Toolbar with the font controls
        toolbar = tk.Frame(self, background=LIGHT_GRAY)
        toolbar.grid(row=0, column=0, sticky="we")

        family_box = ttk.Combobox(
            toolbar,
            textvariable=self.family_var,
            values=sorted(set(tkfont.families())),
            width=24,
            state="readonly",
        )
        family_box.grid(row=0, column=0, padx=4, pady=4)
        family_box.bind(
            "<<ComboboxSelected>>",
            lambda event: self.apply_exclusive(FAMILY_PREFIX, self.family_var.get()),
        )

        size_box = ttk.Combobox(
            toolbar, textvariable=self.size_var, values=FONT_SIZES, width=4
        )
        size_box.grid(row=0, column=1, padx=4)
        size_box.bind("<<ComboboxSelected>>", self.size_changed)
        size_box.bind("<Return>", self.size_changed)

        for column, (label, tag, button_font) in enumerate(STYLE_BUTTONS, start=2):
            button = tk.Button(
                toolbar,
                text=label,
                font=button_font,
                width=3,
                command=lambda tag=tag: self.toggle_style(tag),
            )
            button.grid(row=0, column=column, padx=1)

        color_button = tk.Button(
            toolbar, text="Color", font=("Arial", 12), command=self.choose_color
        )
        color_button.grid(row=0, column=len(STYLE_BUTTONS) + 2, padx=4)

        # Tabs
        self.notebook = ttk.Notebook(self)
        self.notebook.grid(row=1, column=0, sticky="nsew")
        self.notebook.bind("<<NotebookTabChanged>>", self.tab_changed)

    def bind_shortcuts(self, widget):
        for sequence, name in self.shortcuts:
            widget.bind(sequence, lambda event, name=name: self.run_shortcut(name))

    def run_shortcut(self, name):
        getattr(self, name)()
        # "break" stops Tk's own Text bindings (Ctrl+O would insert a newline)
        return "break"

    def new_tab(self):
        frame = tk.Frame(self.notebook)
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
        scrollbar = tk.Scrollbar(frame, command=text.yview)
        text.config(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        text.pack(side="left", fill="both", expand=True)

        text.tag_configure("underline", underline=True)
        self.bind_shortcuts(text)

        self.tabs[str(frame)] = {"text": text, "path": None}
        self.notebook.add(frame, text="Untitled")
        self.notebook.select(frame)
        text.edit_modified(False)
        text.focus_set()

    def current_tab(self):
        return self.tabs[self.notebook.select()]

    def current_text(self):
        return self.current_tab()["text"]

    def is_blank_tab(self):
        tab = self.current_tab()
        text = tab["text"]
        return (
            tab["path"] is None
            and not text.edit_modified()
            and text.get("1.0", "end-1c") == ""
        )

    def set_tab_title(self, path):
        name = os.path.basename(path) if path else "Untitled"
        self.notebook.tab(self.notebook.select(), text=name)
        self.title(f"Notepad - {name}")

    def tab_changed(self, event=None):
        if self.tabs:
            self.set_tab_title(self.current_tab()["path"])
            self.current_text().focus_set()

    def close_tab(self):
        tab = self.current_tab()

        # Ask before throwing away unsaved work
        if tab["text"].edit_modified():
            answer = messagebox.askyesnocancel("Notepad", "Save changes before closing?")
            if answer is None:
                return False
            if answer and not self.save_file():
                return False

        key = self.notebook.select()
        self.notebook.forget(key)
        self.tabs.pop(key)
        self.nametowidget(key).destroy()

        if not self.tabs:
            self.new_tab()
        return True

    def exit_app(self):
        for key in list(self.tabs):
            self.notebook.select(key)
            if not self.close_tab():
                return
        self.destroy()

    def open_file(self):
        path = filedialog.askopenfilename(filetypes=FILE_TYPES)
        if not path:
            return

        try:
            with open(path, "r", encoding="utf-8", errors="replace") as file:
                content = file.read()
        except OSError as error:
            messagebox.showerror("Error", str(error))
            return

        # Reuse the empty starting tab instead of leaving it open next to the file
        if not self.is_blank_tab():
            self.new_tab()

        tab = self.current_tab()
        text = tab["text"]
        if path.lower().endswith(".json"):
            try:
                self.json_to_text(content, text)
            except (ValueError, KeyError, TypeError, tk.TclError):
                messagebox.showerror("Error", "Not a valid styled text file")
                return
        else:
            text.insert("1.0", content)

        tab["path"] = path
        self.set_tab_title(path)
        text.edit_reset()
        text.edit_modified(False)

    def save_file(self):
        path = self.current_tab()["path"]
        if path is None:
            return self.save_file_as()
        return self.write_file(path)

    def save_file_as(self):
        path = filedialog.asksaveasfilename(
            defaultextension=".json", filetypes=FILE_TYPES
        )
        if not path:
            return False
        return self.write_file(path)

    def write_file(self, path):
        tab = self.current_tab()
        text = tab["text"]
        try:
            if path.lower().endswith(".json"):
                content = self.text_to_json(text)
            else:
                content = text.get("1.0", "end-1c")

            with open(path, "w", encoding="utf-8") as file:
                file.write(content)
        except OSError as error:
            messagebox.showerror("Error", str(error))
            return False

        tab["path"] = path
        self.set_tab_title(path)
        text.edit_modified(False)
        return True

    def undo(self):
        try:
            self.current_text().edit_undo()
        except tk.TclError:
            pass

    def redo(self):
        try:
            self.current_text().edit_redo()
        except tk.TclError:
            pass

    def open_find_dialog(self):
        if self.find_dialog is not None and self.find_dialog.winfo_exists():
            self.find_dialog.lift()
            return
        self.find_dialog = FindReplaceDialog(self)

    def get_selection(self, text):
        try:
            return text.index("sel.first"), text.index("sel.last")
        except tk.TclError:
            return None

    def get_style(self, tags):
        # Reads every style out of a set of tags: one value per property
        family, size, color = DEFAULT_FAMILY, DEFAULT_SIZE, DEFAULT_COLOR
        for tag in tags:
            if tag.startswith(FAMILY_PREFIX):
                family = tag[len(FAMILY_PREFIX):]
            elif tag.startswith(SIZE_PREFIX):
                size = int(tag[len(SIZE_PREFIX):])
            elif tag.startswith(COLOR_PREFIX):
                color = tag[len(COLOR_PREFIX):]
        return family, size, "bold" in tags, "italic" in tags, "underline" in tags, color

    def apply_exclusive(self, prefix, value):
        # For styles with ONE value at a time (family, size, color): replace the old one
        text = self.current_text()
        selection = self.get_selection(text)
        if selection is None:
            return

        start, end = selection
        for tag in text.tag_names():
            if tag.startswith(prefix):
                text.tag_remove(tag, start, end)

        new_tag = prefix + str(value)
        text.tag_add(new_tag, start, end)
        if prefix == COLOR_PREFIX:
            text.tag_configure(new_tag, foreground=value)
        else:
            self.refresh_fonts(text, start, end)

        text.edit_modified(True)
        text.focus_set()

    def toggle_style(self, name):
        # Decided by the FIRST selected character: it has the style -> remove from all
        text = self.current_text()
        selection = self.get_selection(text)
        if selection is None:
            return

        start, end = selection
        if name in text.tag_names(start):
            text.tag_remove(name, start, end)
        else:
            text.tag_add(name, start, end)

        if name != "underline":
            self.refresh_fonts(text, start, end)

        text.edit_modified(True)
        text.focus_set()

    def size_changed(self, event=None):
        try:
            size = int(self.size_var.get())
        except ValueError:
            return
        if size > 0:
            self.apply_exclusive(SIZE_PREFIX, size)

    def choose_color(self):
        color = colorchooser.askcolor(parent=self)[1]
        if color:
            self.apply_exclusive(COLOR_PREFIX, color)

    def refresh_fonts(self, text, start, end):
        # Rebuilds the combined font tag of every character in the range
        index = text.index(start)
        while text.compare(index, "<", end):
            tags = text.tag_names(index)
            family, size, bold, italic, underline, color = self.get_style(tags)

            name = f"{FONT_PREFIX}{family}|{size}|{int(bold)}|{int(italic)}"
            styles = [style for style, on in (("bold", bold), ("italic", italic)) if on]
            text.tag_configure(name, font=(family, size, *styles))

            for tag in tags:
                if tag.startswith(FONT_PREFIX) and tag != name:
                    text.tag_remove(tag, index)
            text.tag_add(name, index)

            index = text.index(f"{index}+1c")

    def text_to_json(self, text):
        # The file holds the text and, for every style tag, where it starts and ends
        tags = []
        for name in text.tag_names():
            is_style = name in STYLE_TAGS or name.startswith(
                (FAMILY_PREFIX, SIZE_PREFIX, COLOR_PREFIX)
            )
            if is_style:
                ranges = text.tag_ranges(name)
                for i in range(0, len(ranges), 2):
                    tags.append([name, str(ranges[i]), str(ranges[i + 1])])

        data = {"text": text.get("1.0", "end-1c"), "tags": tags}
        return json.dumps(data, ensure_ascii=False)

    def json_to_text(self, content, text):
        data = json.loads(content)
        text.insert("1.0", data["text"])

        for name, start, end in data["tags"]:
            text.tag_add(name, start, end)
            if name.startswith(COLOR_PREFIX):
                text.tag_configure(name, foreground=name[len(COLOR_PREFIX):])

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


app = Notepad()
app.update()
app.center_window()

app.mainloop()
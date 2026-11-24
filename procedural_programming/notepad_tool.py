import tkinter as tk
from tkinter import filedialog, messagebox

# Open and save dialog file types
FILE_TYPES = [("Text files", "*.txt"), ("All files", "*.*")]

# Encoding: the printable ASCII characters (from space to ~) move this many places
CODE_SHIFT = 3
FIRST_CHAR = 32
CHAR_COUNT = 95

# Path of the opened file (None if the text was never opened or saved)
current_path = None

# The window and the text area, they are created in build_gui
root = None
text_area = None


# Words and expressions
def imparte_in_cuvinte(text):
    """Split the text into lowercase words (letters and digits only)"""
    words = []
    word = ""

    # Add the letters to the word, any other character ends it
    for char in text:
        if char.isalnum():
            word += char.lower()
        elif word != "":
            words.append(word)
            word = ""

    # Last word, if the text ends with a letter
    if word != "":
        words.append(word)

    return words


def frecventa_expresii(words, n):
    """Count how many times every expression of n words appears"""
    frequency = {}

    # Take every group of n words that follow each other
    for i in range(len(words) - n + 1):
        expression = " ".join(words[i : i + n])
        if expression in frequency:
            frequency[expression] += 1
        else:
            frequency[expression] = 1

    return frequency


def gaseste_cel_mai_frecvent(text, n=1):
    """Find the most frequent word (n = 1) or expression of n words, returns (expression, count)"""
    frequency = frecventa_expresii(imparte_in_cuvinte(text), n)
    best = None
    best_count = 0

    # Keep the expression with the biggest count (the first one wins a tie)
    for expression in frequency:
        if frequency[expression] > best_count:
            best = expression
            best_count = frequency[expression]

    return best, best_count


# Hash
def hash_text(text):
    """Simple DJB2 hash of the text (32 bits)"""
    hash_value = 5381

    # hash * 33 + the code of the character, kept in 32 bits
    for char in text:
        hash_value = (hash_value * 33 + ord(char)) & 0xFFFFFFFF

    return hash_value


# Encoding
def shift_char(char, shift):
    """Move one printable ASCII character by shift places, any other character stays"""
    code = ord(char)
    if FIRST_CHAR <= code < FIRST_CHAR + CHAR_COUNT:
        return chr((code - FIRST_CHAR + shift) % CHAR_COUNT + FIRST_CHAR)
    return char


def codifica_text(text, shift=CODE_SHIFT):
    """Encode the text by moving every character in the ASCII table"""
    result = ""
    for char in text:
        result += shift_char(char, shift)
    return result


def decodifica_text(text, shift=CODE_SHIFT):
    """Decode the text, the same move but backwards"""
    return codifica_text(text, -shift)


def verifica_codificarea(text):
    """Check that decoding the encoded text gives back the original"""
    return decodifica_text(codifica_text(text)) == text


# Sentences
def imparte_in_propozitii(text):
    """Split the text into sentences (they end with . ! or ?)"""
    pieces = []
    piece = ""

    # Close the piece after a . ! or ? (a group like ... or ?! counts as one end)
    for i in range(len(text)):
        piece += text[i]
        if text[i] in ".!?" and (i + 1 == len(text) or text[i + 1] not in ".!?"):
            pieces.append(piece)
            piece = ""

    # Text after the last . ! or ?
    pieces.append(piece)

    # One space between words, and skip the pieces without words (like "...")
    sentences = []
    for piece in pieces:
        sentence = " ".join(piece.split())
        if len(imparte_in_cuvinte(sentence)) > 0:
            sentences.append(sentence)

    return sentences


def lungime_medie_propozitii(text):
    """Average length of the sentences, in words"""
    sentences = imparte_in_propozitii(text)
    if len(sentences) == 0:
        return 0

    total = 0
    for sentence in sentences:
        total += len(imparte_in_cuvinte(sentence))

    return total / len(sentences)


def propozitia_cea_mai_lunga(text):
    """Find the sentence with the most words, returns (sentence, number of words)"""
    longest = None
    longest_length = 0

    for sentence in imparte_in_propozitii(text):
        length = len(imparte_in_cuvinte(sentence))
        if length > longest_length:
            longest = sentence
            longest_length = length

    return longest, longest_length


# Statistics
def numar_cuvinte(text):
    """Number of words"""
    return len(imparte_in_cuvinte(text))


def numar_caractere(text):
    """Number of characters (spaces and new lines too)"""
    return len(text)


def numar_linii(text):
    """Number of lines"""
    return len(text.splitlines())


def numar_cuvinte_unice(text):
    """Number of different words"""
    return len(set(imparte_in_cuvinte(text)))


# Sorting
def sorteaza_dupa_lungime(items):
    """Sort a list of strings from the shortest to the longest"""
    return sorted(items, key=len)


def sorteaza_linii(text):
    """Sort the lines of the text by length (empty lines are skipped)"""
    lines = []
    for line in text.splitlines():
        if line.strip() != "":
            lines.append(line)

    return sorteaza_dupa_lungime(lines)


def sorteaza_propozitii(text):
    """Sort the sentences of the text by length"""
    return sorteaza_dupa_lungime(imparte_in_propozitii(text))


# Editor: text and files
def get_text():
    """Get all the text from the editor"""
    return text_area.get("1.0", "end-1c")


def set_text(new_text):
    """Replace all the text in the editor"""
    text_area.delete("1.0", "end")
    text_area.insert("1.0", new_text)


def get_text_or_warn():
    """Get the text, or show a warning and return None if the editor is empty"""
    text = get_text()
    if text.strip() == "":
        messagebox.showwarning("Empty text", "Write or open some text first")
        return None
    return text


def set_title():
    """Show the name of the file in the window title"""
    if current_path is None:
        root.title("Notepad - Untitled")
    else:
        root.title("Notepad - " + current_path)


def new_file():
    """Clear the editor and forget the file"""
    global current_path

    set_text("")
    current_path = None
    set_title()


def open_file():
    """Ask for a file and show it in the editor"""
    global current_path

    path = filedialog.askopenfilename(filetypes=FILE_TYPES)

    # The user cancelled
    if not path:
        return

    # Try to read the file
    try:
        with open(path, "r", encoding="utf-8", errors="replace") as file:
            content = file.read()
    except OSError as error:
        messagebox.showerror("Error", str(error))
        return

    set_text(content)
    current_path = path
    set_title()


def write_file(path):
    """Write the text of the editor into the file, returns True if it worked"""
    global current_path

    # Try to write the file
    try:
        with open(path, "w", encoding="utf-8") as file:
            file.write(get_text())
    except OSError as error:
        messagebox.showerror("Error", str(error))
        return False

    current_path = path
    set_title()
    return True


def save_file_as():
    """Ask for a path and save the text there"""
    path = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=FILE_TYPES)

    # The user cancelled
    if not path:
        return

    write_file(path)


def save_file():
    """Save the text, asks for a path if the file has none"""
    if current_path is None:
        save_file_as()
    else:
        write_file(current_path)


# Editor: showing the results
def make_result_window(title):
    """Create a window with a bar on top and a read only text area, returns both"""
    window = tk.Toplevel(root)
    window.title(title)

    # The bar is empty, only some windows put something in it
    bar = tk.Frame(window)
    bar.pack(side="top", fill="x")

    result_area = tk.Text(window, wrap="word", width=60, height=15, font=("Arial", 12))
    scrollbar = tk.Scrollbar(window, command=result_area.yview)
    result_area.config(yscrollcommand=scrollbar.set)
    scrollbar.pack(side="right", fill="y")
    result_area.pack(side="left", fill="both", expand=True)

    return bar, result_area


def set_result(result_area, message):
    """Replace the message of a result window (it is locked, so unlock it first)"""
    result_area.config(state="normal")
    result_area.delete("1.0", "end")
    result_area.insert("1.0", message)
    result_area.config(state="disabled")


def show_result(title, message):
    """Show a result in a new window"""
    bar, result_area = make_result_window(title)
    set_result(result_area, message)


def update_cel_mai_frecvent(size_var, result_area):
    """Show the most frequent expression, for the number of words from the box"""
    # The box can hold anything while the user types
    try:
        n = int(size_var.get())
    except ValueError:
        n = 0

    if n < 1:
        set_result(result_area, "Write a whole number of words, 1 or more")
        return

    # Always use the text that is in the editor now
    expression, count = gaseste_cel_mai_frecvent(get_text(), n)
    if expression is None:
        set_result(result_area, f"The text has no expression of {n} words")
    else:
        set_result(
            result_area,
            f'Most frequent expression of {n} word(s):\n"{expression}"\n\n'
            f"It appears {count} time(s)",
        )


def afiseaza_cel_mai_frecvent():
    """Open the window of the most frequent word or expression"""
    text = get_text_or_warn()
    if text is None:
        return

    bar, result_area = make_result_window("Most frequent")

    # The number of words in the expression (1 = a single word)
    size_var = tk.StringVar(value="1")
    tk.Label(bar, text="Words in the expression:").pack(side="left", padx=6, pady=4)
    tk.Spinbox(bar, from_=1, to=20, width=4, textvariable=size_var).pack(side="left")

    # Update the result every time the number changes (arrows or typing)
    size_var.trace_add(
        "write", lambda *args: update_cel_mai_frecvent(size_var, result_area)
    )
    update_cel_mai_frecvent(size_var, result_area)


def afiseaza_hash():
    """Show the hash of the text"""
    text = get_text_or_warn()
    if text is None:
        return

    hash_value = hash_text(text)
    show_result(
        "Hash (DJB2)",
        f"Decimal: {hash_value}\nHexadecimal: {hash_value:08x}",
    )


def codifica_in_editor():
    """Replace the text of the editor with the encoded text"""
    set_text(codifica_text(get_text()))


def decodifica_in_editor():
    """Replace the text of the editor with the decoded text"""
    set_text(decodifica_text(get_text()))


def afiseaza_verificarea():
    """Show if encoding and then decoding the text gives back the original"""
    text = get_text_or_warn()
    if text is None:
        return

    if verifica_codificarea(text):
        answer = "OK, the decoded text is the same as the original"
    else:
        answer = "ERROR, the decoded text is different"

    show_result(
        "Encoding check",
        f"Encoded text:\n{codifica_text(text)}\n\n{answer}",
    )


def afiseaza_lungime_medie():
    """Show the average length of the sentences"""
    text = get_text_or_warn()
    if text is None:
        return

    count = len(imparte_in_propozitii(text))
    average = lungime_medie_propozitii(text)
    show_result(
        "Average sentence length",
        f"Sentences: {count}\nAverage length: {average:.2f} words",
    )


def afiseaza_propozitia_lunga():
    """Show the longest sentence"""
    text = get_text_or_warn()
    if text is None:
        return

    sentence, length = propozitia_cea_mai_lunga(text)
    if sentence is None:
        show_result("Longest sentence", "There are no sentences in the text")
    else:
        show_result("Longest sentence", f"{sentence}\n\n({length} words)")


def afiseaza_statistica():
    """Show the words, characters, lines and unique words"""
    text = get_text_or_warn()
    if text is None:
        return

    show_result(
        "Statistics",
        f"Words: {numar_cuvinte(text)}\n"
        f"Characters: {numar_caractere(text)}\n"
        f"Lines: {numar_linii(text)}\n"
        f"Unique words: {numar_cuvinte_unice(text)}",
    )


def afiseaza_linii_sortate():
    """Show the lines sorted by length"""
    text = get_text_or_warn()
    if text is None:
        return

    show_result("Lines by length", "\n".join(sorteaza_linii(text)))


def afiseaza_propozitii_sortate():
    """Show the sentences sorted by length"""
    text = get_text_or_warn()
    if text is None:
        return

    show_result("Sentences by length", "\n".join(sorteaza_propozitii(text)))


# Editor: the window
def build_menu():
    """Build the menu bar (None in a list means a separator)"""
    menus = [
        (
            "File",
            [
                ("New", new_file),
                ("Open...", open_file),
                ("Save", save_file),
                ("Save as...", save_file_as),
                None,
                ("Exit", root.destroy),
            ],
        ),
        (
            "Analyze",
            [
                ("Most frequent word or expression", afiseaza_cel_mai_frecvent),
                ("Statistics", afiseaza_statistica),
                None,
                ("Average sentence length", afiseaza_lungime_medie),
                ("Longest sentence", afiseaza_propozitia_lunga),
                None,
                ("Sort lines by length", afiseaza_linii_sortate),
                ("Sort sentences by length", afiseaza_propozitii_sortate),
            ],
        ),
        (
            "Tools",
            [
                ("Hash of the text", afiseaza_hash),
                None,
                ("Encode text", codifica_in_editor),
                ("Decode text", decodifica_in_editor),
                ("Check encoding", afiseaza_verificarea),
            ],
        ),
    ]

    menu_bar = tk.Menu(root, tearoff=False)

    # Loop for every menu (File, Analyze, Tools)
    for title, items in menus:
        menu = tk.Menu(menu_bar, tearoff=False)

        # Loop for every item of the menu
        for item in items:
            if item is None:
                menu.add_separator()
            else:
                menu.add_command(label=item[0], command=item[1])

        menu_bar.add_cascade(label=title, menu=menu)

    root.config(menu=menu_bar)


def build_gui():
    """Create the window with the text area and the menu"""
    global root, text_area

    root = tk.Tk()
    root.geometry("800x550")

    # The text area with a scrollbar
    text_area = tk.Text(
        root, wrap="word", undo=True, font=("Arial", 14), padx=6, pady=6
    )
    scrollbar = tk.Scrollbar(root, command=text_area.yview)
    text_area.config(yscrollcommand=scrollbar.set)
    scrollbar.pack(side="right", fill="y")
    text_area.pack(side="left", fill="both", expand=True)

    build_menu()
    set_title()


def center_window():
    """Put the window in the middle of the screen"""
    # Get window and screen width and height
    window_height = root.winfo_height()
    window_width = root.winfo_width()
    screen_height = root.winfo_screenheight()
    screen_width = root.winfo_screenwidth()

    # Calculate the (x,y) coords to center the window on the screen
    window_x = int((screen_width / 2) - (window_width / 2))
    window_y = int((screen_height / 2) - (window_height / 2))

    root.geometry(f"{window_width}x{window_height}+{window_x}+{window_y}")


if __name__ == "__main__":
    build_gui()
    root.update()
    center_window()
    root.mainloop()

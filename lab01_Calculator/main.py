import tkinter as tk
from math import sqrt, sin, cos, tan, log, log10, radians

# Button on the calculator (add more for higher grade)
BUTTON_VALUES = [
    ["MC", "MR", "M+", "M-"],
    ["sin", "cos", "tan", "log"],
    ["ln", "x²", "1/x", "HEX"],
    ["AC", "+/-", "%", "÷"],
    ["7", "8", "9", "×"],
    ["4", "5", "6", "-"],
    ["1", "2", "3", "+"],
    ["0", ".", "√", "="],
]

# Row and column count
ROW_COUNT = len(BUTTON_VALUES)
COLUMN_COUNT = len(BUTTON_VALUES[0])

# Reference button for color palette
RIGHT_SYMBOLS = ["÷", "×", "-", "+", "="]
TOP_SYMBOLS = ["AC", "+/-", "%"]
MEM_SYMBOLS = ["MC", "MR", "M+", "M-"]
SCI_SYMBOLS = ["sin", "cos", "tan", "log", "ln", "x²", "1/x", "HEX"]

# Color palette
LIGHT_GRAY = "#D4D4D2"
BLACKBOARD = "#1C1C1C"
HEATHER_GRAY = "#505050"
VIVID_GAMBOGE = "#FF9500"
MEM_BLUE = "#2C3E70"
SCI_TEAL = "#1F4E4C"
WHITE = "white"
BLACK = "black"


class Calculator(tk.Tk):
    def __init__(self) -> None:
        super().__init__()
        self.title("Calculator")
        self.resizable(False, False)
        # self.frame = tk.Frame(self)
        self.label = tk.Label(
            self,
            text="0",
            font=("Arial", 45),
            background=BLACK,
            foreground=WHITE,
            anchor="e",
            width=COLUMN_COUNT,
        )

        # Parts of the calculus + operator
        self.a = "0"
        self.b = None
        self.operator = None
        self.new_entry = False
        self.memory = 0
        self.is_hex = False

        self.label.grid(row=0, column=0, columnspan=COLUMN_COUNT, sticky="we")
        self.build_gui()

    def build_gui(self):
        for row in range(ROW_COUNT):
            for column in range(COLUMN_COUNT):
                value = BUTTON_VALUES[row][column]
                button = tk.Button(
                    self,
                    text=value,
                    font=("Arial", 30),
                    width=COLUMN_COUNT - 1,
                    height=1,
                    command=lambda value=value: self.button_clicked(value),
                )
                button.grid(row=row + 1, column=column)

                if value in TOP_SYMBOLS:
                    button.config(foreground=BLACK, background=LIGHT_GRAY)
                elif value in RIGHT_SYMBOLS:
                    button.config(foreground=WHITE, background=VIVID_GAMBOGE)
                elif value in MEM_SYMBOLS:
                    button.config(foreground=WHITE, background=MEM_BLUE)
                elif value in SCI_SYMBOLS:
                    button.config(foreground=WHITE, background=SCI_TEAL)
                else:
                    button.config(foreground=WHITE, background=HEATHER_GRAY)

    def calculate(self):
        self.b = self.label["text"]
        try:
            num_A = float(self.a)
            num_B = float(self.b)

            if self.operator == "+":
                result = num_A + num_B
            elif self.operator == "-":
                result = num_A - num_B
            elif self.operator == "×":
                result = num_A * num_B
            elif self.operator == "÷":
                result = num_A / num_B
            else:
                return

            self.label["text"] = self.remove_zero_decimal(round(result, 10))
        except (ZeroDivisionError, ValueError, OverflowError):
            self.label["text"] = "Error"

    def clear_all(self):
        self.a = "0"
        self.b = None
        self.operator = None
        self.is_hex = False

    def remove_zero_decimal(self, num):
        if num % 1 == 0:
            num = int(num)
        return str(num)

    def button_clicked(self, value):
        if value in RIGHT_SYMBOLS:
            if value == "=":
                if self.a is not None and self.operator is not None:
                    self.calculate()
                    self.clear_all()
                    self.a = self.label["text"]
                    self.new_entry = True

            elif value in ["÷", "×", "-", "+"]:
                if self.operator is not None and not self.new_entry:
                    self.calculate()
                self.a = self.label["text"]
                self.operator = value
                self.new_entry = True

        elif value in TOP_SYMBOLS:
            if value == "AC":
                self.clear_all()
                self.label["text"] = "0"

            elif value == "+/-":
                self.label["text"] = self.remove_zero_decimal(
                    float(self.label["text"]) * -1
                )

            elif value == "%":
                self.label["text"] = self.remove_zero_decimal(
                    float(self.label["text"]) / 100
                )
        elif value in MEM_SYMBOLS:
            try:
                current = float(self.label["text"])
            except ValueError:
                current = 0

            if value == "MC":
                self.memory = 0
            elif value == "MR":
                self.label["text"] = self.remove_zero_decimal(self.memory)
                self.new_entry = True
            elif value == "M+":
                self.memory += current
            elif value == "M-":
                self.memory -= current

        elif value in SCI_SYMBOLS:
            try:
                current = float(self.label["text"])
                if value == "sin":
                    result = sin(radians(current))
                elif value == "cos":
                    result = cos(radians(current))
                elif value == "tan":
                    result = tan(radians(current))
                elif value == "log":
                    result = log10(current)
                elif value == "ln":
                    result = log(current)
                elif value == "x²":
                    result = current ** 2
                elif value == "1/x":
                    result = 1 / current
                elif value == "HEX":
                    if self.is_hex:
                        result = int(self.label["text"], 16)
                    else:
                        result = int(current)
                        self.label["text"] = format(result, "X")
                        self.is_hex = True
                        self.new_entry = True
                        raise StopIteration
                    self.is_hex = False

                self.label["text"] = self.remove_zero_decimal(round(result, 10))
                self.new_entry = True
            except StopIteration:
                pass
            except (ValueError, ZeroDivisionError, OverflowError):
                self.label["text"] = "Error"
                self.is_hex = False

        else:
            if value == ".":
                if value not in self.label["text"]:
                    self.label["text"] += value
            elif value in "0123456789":
                if self.new_entry or self.label["text"] == "0":
                    self.label["text"] = value
                    self.new_entry = False
                else:
                    self.label["text"] += value
            elif value == "√":
                try:
                    result = sqrt(float(self.label["text"]))
                    self.label["text"] = self.remove_zero_decimal(round(result, 10))
                except ValueError:
                    self.label["text"] = "Error"

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


app = Calculator()
app.update()
app.center_window()

app.mainloop()
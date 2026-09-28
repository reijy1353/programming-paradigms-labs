import tkinter as tk
from math import sqrt

# Button on the calculator (add more for higher grade)
BUTTON_VALUES = [
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

# Color palette
LIGHT_GRAY = "#D4D4D2"
BLACKBOARD = "#1C1C1C"
HEATHER_GRAY = "#505050"
VIVID_GAMBOGE = "#FF9500"
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

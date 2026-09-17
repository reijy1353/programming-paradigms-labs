import tkinter as tk


# Button on the calculator (add more for higher grade)
BUTTON_VALUES = [
    ["AC", "+/-", "%", "÷"],
    ["7", "8", "9", "×"],
    ["4", "5", "6", "-"],
    ["1", "2", "3", "+"],
    ["0", ".", "√", "="],
]

# Reference button for color palette
RIGHT_SYMBOLS = ["÷", "×", "-", "+", "="]
TOP_SYMBOLS = ["AC", "+/-", "%"]

# Color palette
LIGHT_GRAY = "#D4D4D2"
BLACKBOARD = "#1C1C1C"
HEATHER_GRAY = "#505050"
VIVID_GAMBOGE = "#FF9500"
WHITE = "white"


class Calculator(tk.Tk):
    def __init__(self) -> None:
        super().__init__()
        self.title("Calculator")
        self.resizable(False, False)


app = Calculator()
app.mainloop()

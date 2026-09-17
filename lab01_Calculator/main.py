import tkinter as tk


class Calculator(tk.Tk):
    def __init__(self) -> None:
        super().__init__()
        self.title("Calculator")
        self.resizable(False, False)


app = Calculator()
app.mainloop()

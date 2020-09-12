from interface import FolderInspector
import tkinter as tk


def launcher():
    root = tk.Tk()
    root.title("Folder Inspector")
    FolderInspector(root)
    root.geometry("900x535+300+300")
    root.resizable(True, False)
    root.mainloop()


if __name__ == "__main__":
    launcher()

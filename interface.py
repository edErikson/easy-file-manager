import os
import tkinter as tk
from tkinter import filedialog
from services import get_file_list, get_folder_counter, open_path
from database import db_search, insert_data, first_time_db

FONTS_FOLDER = ('Arial', 14)
FONTS_SEARCH = ('Arial', 13)


class ListViewer(tk.Listbox):

    def __init__(self, master, **kw):
        super().__init__(master, **kw)

        self.scrollbar = tk.Scrollbar(master, orient=tk.VERTICAL)
        self.list = tk.Listbox(master, selectmode=tk.EXTENDED, yscrollcommand=self.scrollbar.set)
        self.list.config(height=20)
        self.scrollbar.config(command=self.list.yview)

        self.popup_menu = tk.Menu(self.list, tearoff=0)
        self.popup_menu.add_command(label='Open file location', command=self.open_path)
        self.popup_menu.add_command(label='Open file in Notepad', command=self.open_file_notepad)
        self.list.bind("<Button-3>", self.popup)

        self.print_btn = tk.Button(master, text="Print selection", command=self.print_selection)
        self.delete_btn = tk.Button(master, text="Delete selection", command=self.delete_selected_items)

        self.scrollbar.grid(column=3, row=5, sticky='nsew')
        self.list.grid(column=0, row=5, columnspan=2, padx=(10, 1), sticky='nsew')
        self.print_btn.grid(column=0, row=6, padx=(10, 1), sticky='nsew')
        self.delete_btn.grid(column=1, row=6, sticky='nsew')

    def list_size(self):
        return self.list.size()

    def all_list_items(self):
        return self.list.get(0, tk.END)

    def clear_list(self):
        self.list.delete(0, tk.END)

    def populate_list(self, item):
        self.list.insert(0, item)

    def get_current_selection(self):
        """
        If in Listbox selected more than 1 item:
                return list with items
            else:
                return item string
        """
        current_selection = self.list.curselection()
        selected_items = [self.list.get(i) for i in current_selection]
        if len(selected_items) == 1:
            return self.list.get(current_selection)
        return selected_items

    def popup(self, event):
        self.popup_menu.tk_popup(event.x_root, event.y_root, 0)

    def open_path(self):
        file_path = self.get_current_selection()
        open_path(file_path)

    def open_file_notepad(self):
        file_path = self.get_current_selection()
        if isinstance(file_path, str):
            open_path(file_path, notepad=True)
        else:
            for path in file_path:
                open_path(path, notepad=True)

    def print_selection(self):
        selected_items = self.get_current_selection()
        top = tk.Toplevel()
        selection_list = ListViewer(top)
        selection_list.grid(column=0, row=5, sticky='nsew')

        if isinstance(selected_items, list):
            max_len_str = max(selected_items, key=len)
            selection_list.config(width=len(max_len_str))
            for item in selected_items:
                selection_list.populate_list(item)
        else:
            selection_list.populate_list(selected_items)
            selection_list.config(width=len(selected_items))

    def delete_selected_items(self):
        selection = self.list.curselection()
        for i in reversed(selection):
            self.list.delete(i)


class FolderInspector(tk.Frame):

    def __init__(self, master, **kw):
        super().__init__(master, **kw)
        self.pack(fill=tk.X)
        for x in range(2):
            tk.Grid.columnconfigure(self, x, weight=1)

        self.counter_label = tk.StringVar()
        self.search_str = tk.StringVar()
        self.folder_path = tk.StringVar()

        if not os.path.isfile("folder.db"):
            self.folder_path.set('Select folder to get all file paths')
            first_time_db()
        else:
            self.folder_path.set('Database detected')

        self.widgets()
        self.list = ListViewer(self)
        self.list.grid(column=0, row=5)

    def widgets(self):
        tk.Button(self, text='Select Folder', font=FONTS_FOLDER, fg='#58F',
                  command=self.chosen_folder_details).grid(column=0, row=0, padx=(10, 1), sticky='nsew')
        tk.Button(self, text='Current folder to DB', font=FONTS_FOLDER, fg='#58F',
                  command=self.save_paths_to_db).grid(column=1, row=0, sticky='nsew')
        tk.Button(self, text='Current list to DB', font=FONTS_FOLDER, fg='#58F',
                  command=self.save_list_to_db).grid(column=0, row=1, padx=(10, 1), sticky='nsew')

        tk.Label(self, textvariable=self.folder_path, fg='#81F',
                 font=FONTS_FOLDER).grid(column=1, row=1, sticky='nsew')
        tk.Label(self, textvariable=self.counter_label, fg='#81F',
                 font=FONTS_FOLDER).grid(column=1, row=2, sticky='nsew')
        tk.Button(self, text='Print files to list', fg='#58F', font=FONTS_FOLDER,
                  command=self.print_details).grid(column=0, row=2, padx=(10, 1), sticky='nsew')

        tk.Button(self, text='Search in list', font=FONTS_SEARCH, fg='#57F',
                  command=self.search_in_list).grid(column=0, row=3, padx=(10, 1), sticky='nsew')

        self.entry = tk.Entry(self, font=FONTS_FOLDER, textvariable=self.search_str, bd=2)
        self.entry.insert(0, 'Search str...')
        self.entry.bind('<FocusIn>', self.on_entry_click)
        self.entry.bind('<FocusOut>', self.on_focus_out)
        self.entry.config(fg='grey')
        self.entry.grid(column=1, row=3, sticky='nsew')

        tk.Button(self, text='Search in DB', font=FONTS_SEARCH, fg='#57F',
                  command=self.search_in_db).grid(column=1, row=4, sticky='nsew')
        tk.Button(self, text="Get all data from DB", font=FONTS_SEARCH, fg='#57F',
                  command=self.get_paths_from_db).grid(column=0, row=4, padx=(10, 1), sticky='nsew')

    def on_entry_click(self, event):
        if self.entry.get() == 'Search str...':
            self.entry.delete(0, tk.END)
            self.entry.insert(0, '')
            self.entry.config(fg='black')

    def on_focus_out(self, event):
        if self.entry.get() == '':
            self.entry.insert(0, 'Search str...')
            self.entry.config(fg='grey')

    def print_details(self):
        for item in get_file_list(self.folder_path.get()):
            self.list.populate_list(item)
        self.counter_label.set(f'total files: {self.list.list_size()}')

    def chosen_folder_details(self):
        folder = filedialog.askdirectory()
        self.folder_path.set(folder)
        file_folder_count = get_folder_counter(folder)
        self.counter_label.set(f'total folders: {file_folder_count[0]} - total files: {file_folder_count[1]}')

    def search_in_list(self):
        found_items = []
        search_str = self.search_str.get()
        for file_path in self.list.all_list_items():
            if search_str.lower() in file_path.lower():
                found_items.append(file_path)
        self.list.clear_list()
        [self.list.populate_list(item) for item in found_items]
        self.counter_label.set(f'total files: {len(found_items)}')

    def search_in_db(self):
        search_str = self.search_str.get()
        self.list.clear_list()
        for item in db_search(search_str):
            self.list.populate_list(str(item[0]))
        self.counter_label.set(f'total files: {self.list.list_size()}')

    def save_list_to_db(self):
        for file_path in self.list.all_list_items():
            insert_data(file_path)
        self.folder_path.set('items added')

    def save_paths_to_db(self):
        for item in get_file_list(self.folder_path.get()):
            insert_data(item)
        self.folder_path.set('items added')

    def get_paths_from_db(self):
        for item in db_search():
            self.list.populate_list(str(item[0]))
        self.counter_label.set(f'total files: {self.list.list_size()}')


if __name__ == "__main__":
    root = tk.Tk()
    root.title("Folder Inspector")
    app = FolderInspector(root)
    root.geometry("1200x560+300+300")
    root.resizable(True, False)
    root.mainloop()

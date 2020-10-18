import os
import tkinter as tk
from tkinter import filedialog
from services import get_file_list, get_folder_counter, open_path, get_file_size, get_file_name
from database import first_time_db, insert_data, insert_path_data, db_delete_record
from database import get_table_names, create_table, db_search
from distribution_module import distribution_module_app

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
        self.popup_menu.add_command(label='Delete selected items', command=self.delete_selected_items)
        self.list.bind("<Button-3>", self.popup)
        self.scrollbar.grid(column=3, row=5, sticky='nsew')
        self.list.grid(column=0, row=5, columnspan=2, padx=(10, 1), sticky='nsew')

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
        open_path(file_path[1])

    def open_file_notepad(self):
        file_path = self.get_current_selection()
        if isinstance(file_path, tuple):
            open_path(file_path[1], notepad=True)
        else:
            for path in file_path:
                open_path(path[1], notepad=True)

    def delete_selected_items(self):
        current_selection = self.list.curselection()
        for i in reversed(current_selection):
            self.list.delete(i)


class SelectedList(ListViewer):
    def __init__(self, master, **kw):
        super().__init__(master, **kw)
        self.creator_frame = tk.Frame(master)
        self.creator_frame.grid()
        self.print_btn = tk.Button(self.creator_frame, text="Create New Table", command=self.new_table)
        self.table_name = tk.Entry(self.creator_frame)
        self.add_data_btn = tk.Button(self.creator_frame, text="Add items to db", command=self.add_items_to_table)
        self.info_label = tk.Label(self.creator_frame)
        self.txt_label = tk.Label(self.creator_frame, text='existing dbs :')
        self.choice_variable = tk.StringVar()
        self.choice_variable.set('')
        self.choice_variable.trace("w", self.choice_callback)
        self.btn_choice = tk.OptionMenu(self.creator_frame, self.choice_variable, *get_table_names())
        self.txt_label.grid(column=4, row=0)
        self.btn_choice.grid(column=5, row=0)

        self.print_btn.grid(column=0, row=0)
        self.table_name.grid(column=1, row=0)
        self.add_data_btn.grid(column=2, row=0)
        self.info_label.grid(column=3, row=0)

    def choice_callback(self, *args):
        print(self.choice_variable.get())
        clean_name = self.choice_variable.get()[2:-3]
        self.table_name.delete(0, tk.END)
        self.table_name.insert(0, clean_name)

    def new_table(self):
        name = self.table_name.get()
        print(self.list_size())
        self.info_label['text'] = f'created {name} table'
        self.info_label.config(fg="green")
        create_table(name)

    def add_items_to_table(self):
        name = self.table_name.get()
        errors = 0
        for item in self.all_list_items():
            try:
                insert_data(item[0], get_file_name(item[1]), get_file_size(item[1]), table_name=name)
            except FileNotFoundError:
                errors += 1
                print(item)
                continue
        self.info_label['text'] = f'{self.list_size()} items added and there was {errors} errors'


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
        tk.Button(self, text="Delete selected from DB", font=FONTS_SEARCH, fg='#57F',
                  command=self.delete_selected_from_db).grid(column=0, row=4, padx=(10, 1), sticky='nsew')

        self.print_btn = tk.Button(self, text="Selected items create or extend table ", command=self.print_selection)
        self.delete_btn = tk.Button(self, text="Delete selection", command=self.delete_selected_items)
        self.print_btn.grid(column=0, row=6, padx=(10, 1), sticky='nsew')
        self.delete_btn.grid(column=1, row=6, sticky='nsew')

        tk.Button(self, text="OPEN EXTENDED TABLES", font=FONTS_SEARCH, fg='#57F',
                  command=distribution_module_app).grid(column=0, row=7, columnspan=2, padx=(10, 1), sticky='nsew')

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
            if search_str.lower() in file_path[1].lower():
                found_items.append(file_path)
        self.list.clear_list()
        [self.list.populate_list(item) for item in found_items]
        self.counter_label.set(f'total files: {len(found_items)}')

    def search_in_db(self):
        search_str = self.search_str.get()
        self.list.clear_list()
        for item in db_search(search_str):
            item_id = item[0], str(item[1])
            self.list.populate_list(item_id)
        self.counter_label.set(f'total files: {self.list.list_size()}')

    def save_list_to_db(self):
        for file_path in self.list.all_list_items():
            insert_path_data(file_path)
        self.folder_path.set('items added')

    def save_paths_to_db(self):
        for item in get_file_list(self.folder_path.get()):
            insert_path_data(item)
        self.folder_path.set('items added')

    def delete_selected_from_db(self):
        selection = self.list.get_current_selection()
        if isinstance(selection, list):
            for item in selection:
                db_delete_record(item[0])
            self.folder_path.set(f'{len(selection)} items deleted')
        if isinstance(selection, tuple):
            self.folder_path.set('item deleted')
            db_delete_record(selection[0])

    def print_selection(self):
        selected_items = self.list.get_current_selection()
        top = tk.Toplevel()
        selection_list = SelectedList(top)
        selection_list.grid(column=0, row=5, sticky='nsew')

        if isinstance(selected_items, list):
            max_len_str = 60
            for item in selected_items:
                if len(item[1]) > max_len_str:
                    max_len_str = len(item[1])
                selection_list.populate_list(item)
            selection_list.config(width=max_len_str)
        else:
            selection_list.populate_list(selected_items)
            selection_list.config(width=len(selected_items[1]))

    def delete_selected_items(self):
        self.list.delete_selected_items()


if __name__ == "__main__":
    root = tk.Tk()
    root.title("Folder Inspector")
    app = FolderInspector(root)
    root.geometry("1200x580+300+300")
    root.resizable(True, False)
    root.mainloop()

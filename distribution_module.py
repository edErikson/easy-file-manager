from database import get_table_names, get_table_data, get_item_path, sorted_name, sorted_size
import tkinter as tk
from tkinter import ttk
from services import open_path, pdf_page_counter, text_file_line_counter, get_media_properties

table = ''


class BasicTreeviewer(ttk.Treeview):

    def __init__(self, master, table_columns):
        self.columns = table_columns
        ttk.Treeview.__init__(self, master)

        self.tree = ttk.Treeview(self, columns=self.columns, height=15, show='headings')

        style = ttk.Style()
        style.configure("Treeview.Heading", font=(None, 10))

        self.tree.column('id', width=39, anchor=tk.W)
        self.tree.column('name', width=400, anchor=tk.W)
        self.tree.column('size', width=95, anchor=tk.W)

        self.tree.heading('id', text='id')
        self.tree.heading('name', text='name', command=self.sort_by_name)
        self.tree.heading('size', text='size', command=self.sort_by_size)

        self.tree.pack(side=tk.LEFT)

        self.vsb = ttk.Scrollbar(master, orient="vertical", command=self.tree.yview)
        self.hsb = ttk.Scrollbar(master, orient="horizontal", command=self.tree.xview)
        self.hsb.pack(side=tk.BOTTOM, fill=tk.X)
        self.vsb.pack(side=tk.RIGHT, fill=tk.Y)
        self.tree.configure(yscrollcommand=self.vsb.set)
        self.tree.configure(xscrollcommand=self.hsb.set)

        self.menu = tk.Menu(self.master, tearoff=0)
        self.menu.add_command(label="Open file folder", command=self.open_directory)
        self.menu.add_command(label="Exit")

        self.tree.bind('<ButtonRelease-1>', self.selected_item)
        self.tree.bind("<Button-3>", self.show_menu)
        self.column_focus_name = tk.StringVar()
        self.selected_item_id = tk.StringVar()

    def selected_item(self, e):
        current_item = self.tree.focus()
        print(self.tree.item(current_item)['values'])
        try:
            item_id = self.tree.item(current_item)['values'][0]
            self.selected_item_id.set(item_id)
        except IndexError:
            pass

    def delete_tree(self):
        [self.tree.delete(i) for i in self.tree.get_children()]

    def show_menu(self, e):
        self.menu.post(e.x_root, e.y_root)

    def open_directory(self):
        global table
        item = self.tree.selection()[0]
        file_id, file, *args = self.tree.item(item, "value")
        clean_name = table[2:-3]
        open_path(get_item_path(file_id, table_name=clean_name)[0][0])

    def sort_by_name(self):
        self.delete_tree()
        global table
        clean_name = table[2:-3]
        return [self.tree.insert('', 'end', values=row) for row in sorted_name(clean_name)]

    def sort_by_size(self):
        self.delete_tree()
        global table
        clean_name = table[2:-3]
        return [self.tree.insert('', 'end', values=row) for row in sorted_size(clean_name)]

class App:
    """ main class for the application """
    def __init__(self, master):

        style = ttk.Style()
        style.configure("BW.TLabel", foreground="black", background='#d7d8e0')
        self.mainframe = ttk.Frame(master)
        self.topframe = ttk.Frame(self.mainframe, style="BW.TLabel")
        self.centerframe = ttk.Frame(self.mainframe)
        self.bottomframe = ttk.Frame(self.mainframe, borderwidth=2, relief="groove")

        self.columns = ['id', 'name', 'size']
        self.treeviewer = BasicTreeviewer(self.centerframe, table_columns=self.columns)
        self.treeviewer.pack()

        self.choice_variable = tk.StringVar()
        self.btn_fill = tk.Button(self.topframe, text='Fill tree', command=self.populate_tree)
        self.btn_choice = tk.OptionMenu(self.topframe, self.choice_variable, *get_table_names()[1:])
        self.btn_fill.pack(side=tk.LEFT)
        self.btn_choice.pack(side=tk.LEFT)
        self.btn_inspect = tk.Button(self.topframe, text='Inspect selected item', command=self.inspect_item)
        self.btn_delete = tk.Button(self.topframe, text='Delete Tree', command=self.delete_tree)
        self.btn_inspect.pack(side=tk.LEFT)
        self.btn_delete.pack(side=tk.LEFT)

        self.line_counter = tk.StringVar()
        self.lbl_file_info = tk.Label(self.bottomframe, text='File info frame :')
        self.lbl_line_counter = tk.Label(self.bottomframe, textvariable=self.line_counter, font=('Arial', 15))
        self.btn_delete = tk.Button(self.bottomframe, text='Clear Text', command=self.clear_text)
        self.text_pdf_info = tk.Text(self.bottomframe, font=('Arial', 10), height=4)

        self.lbl_file_info.grid(column=0, row=0, sticky='nsew')
        self.lbl_line_counter.grid(column=0, row=1)
        self.btn_delete.grid(column=1, row=1)
        self.text_pdf_info.grid(column=0, row=2, columnspan=2)

        self.topframe.pack(side=tk.TOP, fill=tk.X)
        self.centerframe.pack(side=tk.TOP)
        self.mainframe.pack(side=tk.TOP, expand=True, fill=tk.BOTH)
        self.bottomframe.pack(side=tk.TOP, expand=True, fill=tk.BOTH)

    def inspect_item(self):
        item_id = self.treeviewer.selected_item_id.get()
        global table
        table = self.choice_variable.get()
        clean_name = table[2:-3]
        full_path = get_item_path(item_id, table_name=clean_name)[0][0]
        if full_path[-4:] == ".pdf":
            pdf_info = pdf_page_counter(get_item_path(item_id, table_name=clean_name)[0][0])
            print(pdf_info)
            self.line_counter.set(pdf_info[0])
            self.text_pdf_info.insert(tk.END, pdf_info[1])
            self.text_pdf_info.insert(tk.END, '\n')
        if full_path[-4:] == ".txt":
            total_lines = text_file_line_counter(get_item_path(item_id, table_name=clean_name)[0][0])
            self.line_counter.set(total_lines)
        if full_path[-4:] == ".png":
            print("picture detected by path : \n", full_path)
        if full_path[-4:] == ".mp4":
            self.text_pdf_info.insert(tk.END, get_media_properties(full_path)[1])
            self.text_pdf_info.insert(tk.END, '\n')

    def clear_text(self):
        self.text_pdf_info.delete("1.0", "end")

    def delete_tree(self):
        self.treeviewer.delete_tree()

    def populate_tree(self):
        global table
        table = self.choice_variable.get()
        clean_name = table[2:-3]
        return [self.treeviewer.tree.insert('', 'end', values=row) for row in get_table_data(clean_name)]


def distribution_module_app():
    top = tk.Toplevel()
    App(top)


if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)
    root.title("File Manager")
    root.geometry("560x520+300+200")
    root.resizable(True, False)
    root.mainloop()

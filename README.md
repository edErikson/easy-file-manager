# Simple file manager
Database based file manager for easy file search. 
Used tkinter and sqlite3


## Usage:
1. Select Folder ---> current folder to DB or print files to list
    List is in EXTENDED mode:
     (multiple ranges of items can be chosen, using the Shift and Control keyboard modifiers)
     
2.Search has 2 options:
    a) In database (possible after list or folder added to db)
    b) In list (seeks string in list with file paths)

start:
 main.py
### Behaviour:
Print files to list    - adds items to list without removing previous items  

Right click in list will open menu with some options 

![](images\main_window.png)

Selected items passed to create extended database table
data - id, name, size

Steps:
1. enter table name in entry :
2. then press Create New Table
3. add items to db


![](images\extended_table_creator.png)

P.S. if choose from existing dbs then skip first 2


in extended table can switch between created table and fill treeview with items
inspect selected item - if .txt returned line count
                      - if .pdf returned page count
![](images\extended_viewer.png)


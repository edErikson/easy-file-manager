import os
import subprocess

notepad_path = r'C:\Program Files (x86)\Notepad++\notepad++.exe'


def get_file_list(dir_path):
    for root_dir, dirs, files in os.walk(dir_path):
        for name in files:
            yield os.path.join(root_dir, name)


def get_folder_counter(dir_path):
    folder_count = 0
    file_count = 0
    for root_dir, dirs, files in os.walk(dir_path, topdown=False):
        folder_count += len(dirs)
        file_count += len(files)
    return folder_count, file_count


def open_path(file_path, notepad=False):
    if notepad:
        try:
            subprocess.Popen([notepad_path, file_path])
        except FileNotFoundError as e:
            print(e)
    else:
        head, tail = os.path.split(file_path)
        os.startfile(head)


if __name__ == '__main__':
    path = r'C:\Users'
    print("'get_folder_counter' : ")
    print('**' * 6)
    folder_counter = get_folder_counter(path)
    print(f'total folders : {folder_counter[0]}- total files : {folder_counter[1]}')

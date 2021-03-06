import os
import subprocess
from PyPDF2 import PdfFileReader
import datetime

notepad_path = r'C:\Program Files (x86)\Notepad++\notepad++.exe'


def get_media_properties(filename):
    result = subprocess.Popen(['hachoir-metadata', filename, '--raw', '--level=7'],
                              stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    results = result.stdout.read().decode('utf-8').split('\r\n')
    properties = {}
    for item in results:
        if item.startswith('- duration: '):
            duration = item.lstrip('- duration: ')
            if '.' in duration:
                t = datetime.datetime.strptime(item.lstrip('- duration: '), '%H:%M:%S.%f')
            else:
                t = datetime.datetime.strptime(item.lstrip('- duration: '), '%H:%M:%S')
            seconds = (t.microsecond / 1e6) + t.second + (t.minute * 60) + (t.hour * 3600)
            properties['duration'] = round(seconds)
        if item.startswith('- width: '):
            properties['width'] = int(item.lstrip('- width: '))
        if item.startswith('- height: '):
            properties['height'] = int(item.lstrip('- height: '))
    return properties, results


def word_count_dict(filename):
    """Returns a word/count dict for this filename."""
    word_count = {}
    input_file = open(filename, 'r', encoding="utf8")
    for line in input_file:
        words = line.split()
        for word in words:
            word = word.lower()
            if not word in word_count:
                word_count[word] = 1
            else:
                word_count[word] = word_count[word] + 1
    input_file.close()
    return word_count


def get_count(word_count_tuple):
    """Returns the count from a dict word/count tuple  -- used for custom sort."""
    return word_count_tuple[1]


def print_top(filename):
    """Prints the top count listing for the given file."""
    word_count = word_count_dict(filename)
    # Each item is a (word, count) tuple.
    # Sort them so the big counts are first using key=get_count() to extract count.
    items = sorted(word_count.items(), key=get_count, reverse=True)
    return items


def text_file_line_counter(file):
    with open(file, 'r', encoding="utf8") as f:
        lines = len(f.readlines())
    return "lines:", lines


def pdf_page_counter(pdf_file):
    try:
        with open(pdf_file, "rb") as file:
            pdf = PdfFileReader(file)
            info = pdf.getDocumentInfo()
            pages = "total pages " + str(pdf.getNumPages())
            return pages, info
    except Exception as e:
        print("Error occured", pdf_file)
        print("with error : ", e)
        return 0


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


def get_file_size(file_path):
    return os.path.getsize(file_path)


def get_file_name(file_path):
    return os.path.basename(file_path)


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

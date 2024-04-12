import platform
import os

# import win32clipboard
import pyperclip


RELATED_LINES_UP_COUNT = 5
RELATED_LINES_DOWN_COUNT = 10


current_clipboard_content = ""

pt = platform.platform()


def read_from_clipboard():
    if "Windows" in pt:
        data = pyperclip.paste()
        return data
    else:
        import subprocess
        return subprocess.check_output(
            'pbpaste', env={'LANG': 'en_US.UTF-8'}).decode('utf-8')



def all_lines_of_path(path):
    """
    path: filepath or directory path
    return: list of all lines
    """
    result = {}    

    if os.path.isfile(path):
        with open(path, 'r') as f:
            result = f.readlines()
            result.update({path, })

    elif os.path.isdir(path):
        for document_dir in settings.get('document_dirs'):
            for path, subdirs, files in os.walk(document_dir):
                for name in files:
                    if not name.endswith(tuple(settings.get('extensions'))):
                        continue
                    with open(f'{path}/{name}', encoding='UTF-8') as f:
                        # 便于监控文件变化
                        files_modifytime.update({f'{path}/{name}': os.stat(f'{path}/{name}').st_mtime})
                        for _line in f.readlines():
                            # print(f'Inserting {_line}')
                            cursor.execute(f"insert into {TABLE}(file, content) values(?, ?)", (f"{path}/{name}", _line))

    return result
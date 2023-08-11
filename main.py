import sys
import os
from typing import List

from DIRECTORY_fat32 import Directory, File, get_absolute_path
from VFS_fat32 import Virtual_FS
from FS_fat32 import close_fat32_file, open_fat32_file


file_host = open_fat32_file(sys.argv[1])

# allocate 20 MB for file
data_size = 20 * 1024 * 1024
# set cluster size as 4KB
cluster_size = 4 * 1024

file_system = Virtual_FS(data_size, cluster_size)

file_system.deserialize(file_host.read(20 * 1024), file_host.read(20 * 1024 * 1024))

# Create directory instances
# root = Directory('root', 0)
# documents = Directory('Documents', 1)
# pictures = Directory('Pictures', 2)
# code = Directory('Code', 3)
#
# # Add subdirectories
# root.add_subdirectory(documents)
# root.add_subdirectory(pictures)
# root.add_subdirectory(code)
#
# # Add files to root directory
# readme = File('readme', "txt", 4, "Hello readme".encode('UTF-8'))
# root.add_file(readme)
# lic = File('readme', "txt", 5, "Hello license".encode('UTF-8'))
# root.add_file(lic)
#
# # Add files to subdirectories
# report = File('report', "docx", 6, "Hello report".encode('UTF-8'))
# documents.add_file(report)
#
# presentation = File('presentation', "pptx", 7, "Hello presentation".encode('UTF-8'))
# documents.add_file(presentation)
#
# vacation = File('vacation', "jpg", 8, "Hello vacation".encode('UTF-8'))
# pictures.add_file(vacation)
#
# family = File('family', "jpg", 9, "Hello family".encode('UTF-8'))
# pictures.add_file(family)
#
# script = File('script', "py", 10, "Hello script".encode('UTF-8'))
# code.add_file(script)
#
# app = File('app', "js", 11, "Hello app".encode('UTF-8'))
# code.add_file(app)
#
# file_system.write_object(root)
# file_system.write_object(documents)
# file_system.write_object(pictures)
# file_system.write_object(code)
# file_system.write_object(readme)
# file_system.write_object(lic)
# file_system.write_object(report)
# file_system.write_object(presentation)
# file_system.write_object(vacation)
# file_system.write_object(family)
# file_system.write_object(script)
# file_system.write_object(app)
#
# file_system.write_by_addr(0, root.serialize())
# file_system.write_by_addr(1, documents.serialize())
# file_system.write_by_addr(2, pictures.serialize())
# file_system.write_by_addr(3, code.serialize())
# file_system.write_by_addr(4, readme.serialize())
# file_system.write_by_addr(5, lic.serialize())
# file_system.write_by_addr(6, report.serialize())
# file_system.write_by_addr(7, presentation.serialize())
# file_system.write_by_addr(8, vacation.serialize())
# file_system.write_by_addr(9, family.serialize())
# file_system.write_by_addr(10, script.serialize())
# file_system.write_by_addr(11, app.serialize())

root = file_system.get_dir_by_addr(0, "root")

current_directories = [root]
current_path = get_absolute_path(current_directories)
while True:
    print(current_path, end='>')
    command = str(input())

    if command == 'exit':
        break

    if command == 'ls':
        print(' '.join(current_directories[-1].get_dir_names_list()))
        continue

    if command.startswith("cd"):
        path = command.split(' ')[1]

        if path == "root/" or path == "root":
            current_directories = [root]
            current_path = get_absolute_path(current_directories)
            continue

        path_fragment = path.lstrip('/').rstrip('/').split('/', 1)

        old_directories = current_directories.copy()

        while len(path_fragment) > 0:

            next_path = path_fragment[0]

            if next_path in current_directories[-1].get_dir_names_list():

                next_dir = current_directories[-1].get_directory_by_name(next_path)

                if next_dir is None:
                    print(f"Cant find directory: {next_path}")
                    current_directories = old_directories
                    current_path = get_absolute_path(current_directories)
                    break

                current_directories.append(next_dir)
                current_path = get_absolute_path(current_directories)
            elif next_path == '..':
                current_directories.pop()
                current_path = get_absolute_path(current_directories)
            else:
                print(f"Cant find directory: {next_path}")
                current_directories = old_directories
                current_path = get_absolute_path(current_directories)
                break

            if len(path_fragment) > 1:
                path_fragment = path_fragment[1].lstrip('/').rstrip('/').split('/', 1)
            else:
                path_fragment = []

        continue

    if command.startswith("touch"):
        filename = command.split(' ')[1]

        if filename not in current_directories[-1].get_files_list():

            next_cluster = file_system.fat_table.get_next_cluster_index()

            name = filename.rsplit('.', 1)[0]
            extension = filename.rsplit('.', 1)[1]

            new_file = File(name, extension, next_cluster, f"Hello {name}".encode('UTF-8'))
            current_directories[-1].add_file(new_file)

            file_system.write_object(new_file)
            file_system.write_object(current_directories[-1])

        else:
            print(f"file: {filename} already exists")
        continue

    if command.startswith("mkdir"):
        dirname = command.split(' ')[1]

        if dirname not in current_directories[-1].get_dirs_list():

            next_cluster = file_system.fat_table.get_next_cluster_index()

            new_dir = Directory(dirname, next_cluster)
            current_directories[-1].add_subdirectory(new_dir)

            file_system.write_object(new_dir)
            file_system.write_object(current_directories[-1])

        else:
            print(f"file: {dirname} already exists")
        continue

    if command == "format":
        file_system.format()
        print("System formatted")

        current_directories = [root]
        root.clear_subentries()
        current_path = get_absolute_path(current_directories)

        continue

    print(f"Unrecognized command: {command}")

# write all data into file
file_host.seek(0)
file_host.write(file_system.serialize())

close_fat32_file(file_host)

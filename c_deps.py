#!/usr/bin/python3
"""This script recursively finds dependencies of a C/C++ file.
The implementation is naive, so don't expect 100% accuracy."""

import sys, getopt, os.path, re

def main(argv):
    help_text = "c_deps.py -I <include directory path> -f inputfile"
    try:
        opts, args = getopt.getopt(argv, "hI:f:")
    except getopt.GetoptError:
        print(help_text)
        sys.exit(1)

    include_directories = []
    file_abs_path = ""
    for opt, arg in opts:
        if opt == "-h":
            print(help_text)
            sys.exit()
        elif opt == "-I":
            abs_path = os.path.abspath(arg)
            include_directories.append(abs_path)
        elif opt == "-f":
            file_abs_path = os.path.abspath(arg)

    if not include_directories or not file_abs_path:
        print(help_text)
        sys.exit(1)

    dependencies = []
    find_dependencies(file_abs_path, dependencies, include_directories)
    dependencies.sort()
    for dependency in dependencies:
        print(dependency)


def find_dependencies(file_abs_path, dependencies, include_directories):
    if file_abs_path in dependencies:
        return
    dependencies.append(file_abs_path)

    headers = list_headers(file_abs_path)
    for header in headers:
        if header[0] == '<':
            if header not in dependencies:
                dependencies.append(header)
            continue
        header_abs_path = find_header_file(header[1:-1], include_directories)
        if not header_abs_path:
            print(f"Warning. Unable to find header {header} "
                  "in the include directories.")
            continue
        if header_abs_path in dependencies:
            continue
        find_dependencies(header_abs_path, dependencies, include_directories)

    # If there is a c/cpp file, get its dependencies.
    root, extension = os.path.splitext(file_abs_path)
    if extension == ".h":
        c_file = root + ".c"
        cpp_file = root + ".cpp"
        if os.path.isfile(c_file):
            find_dependencies(c_file, dependencies, include_directories)
        elif os.path.isfile(cpp_file):
            find_dependencies(cpp_file, dependencies, include_directories)


def list_headers(file_abs_path):
    pattern = re.compile("#include ([\"<].+[\">])")
    with open(file_abs_path, 'r') as file:
        return re.findall(pattern, file.read())


def find_header_file(file_rel_path, include_directories):
    file_abs_path = ""
    for include_directory in include_directories:
        abs_path_candidate = os.path.join(include_directory, file_rel_path)
        if os.path.isfile(abs_path_candidate):
            file_abs_path = abs_path_candidate
            break
    return file_abs_path


if __name__ == "__main__":
    main(sys.argv[1:])

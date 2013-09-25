#!/usr/bin/env python
# coding: utf-8

from __future__ import absolute_import, unicode_literals
import shutil
import sys
import os

PROJECT_PATH = os.path.sep.join(os.path.abspath(__file__).split(os.path.sep)[:-2])


def simple_copy(src, build, file_name, extension):
    shutil.copyfile(src, build)


def handle_yaml(src, build, file_name, extension):
    if file_name == "app":
        app_src = open(src, "r")
        app_build = open(build, "w")
        for line in app_src:
            if line.startswith("application"):
                #alterar para variavel depois
                line = "application: %s\n" % sys.argv[1]
            if line.startswith("version"):
                #alterar para variavel depois
                line = "version: %s\n" % sys.argv[2]
            app_build.write(line)
        app_src.close()
        app_build.close()
    else:
        shutil.copyfile(src, build)


handler_dct = {
    "yaml": handle_yaml
}

if __name__ == "__main__":
    src_dir = os.path.abspath(os.path.join(PROJECT_PATH, "src"))
    build_dir = os.path.abspath(os.path.join(PROJECT_PATH, "build"))
    if os.path.exists(build_dir):
        shutil.rmtree(build_dir)
    os.mkdir(build_dir)
    index_yaml = os.path.abspath(os.path.join(PROJECT_PATH, "index.yaml"))
    if os.path.exists(index_yaml):
        shutil.copyfile(index_yaml, os.path.join(build_dir, "index.yaml"))
    ignored_extensions = ("pyc", "less", "egg-info", "egg", "pth")

    def copy_files(arg, dirname, files):
        build = dirname.replace(src_dir, build_dir, 1)
        if not os.path.exists(build):
            os.mkdir(build)
        for f in files:
            src = os.path.join(src_dir, dirname, f)
            if os.path.isfile(src):
                slices = f.split(".")
                file_name = ".".join(slices[:-1])
                file_extension = slices[-1]
                if not (file_extension in ignored_extensions):
                    build = src.replace(src_dir, build_dir, 1)
                    fcn = handler_dct.get(file_extension, simple_copy)
                    fcn(src, build, file_name, file_extension)

    os.path.walk(src_dir, copy_files, None)
    # coping libs
    src_dir = os.path.abspath(os.path.join(PROJECT_PATH, "lib", "python2.7", "site-packages"))
    build_dir = os.path.abspath(os.path.join(PROJECT_PATH, "build", "lib"))
    os.mkdir(build_dir)
    os.path.walk(src_dir, copy_files, None)

    # removing not desired dirs

    for item in os.listdir(build_dir):
        file=os.path.join(build_dir,item)
        if os.path.isdir(file) and (file.endswith('.egg') or file.endswith('.egg-info')):
            shutil.rmtree(file)

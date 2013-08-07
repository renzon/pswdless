# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals
import os


def create_or_update_catalog(loc, compile_target, msgs_pot):
    result = os.system("pybabel update -l %s -d %s -i %s" % (loc, compile_target, msgs_pot))
    if result != 0:
        os.system("pybabel init -l %s -d %s -i %s" % (loc, compile_target, msgs_pot))


def compile_po_files(compile_target, locale_target):
    for root, dirs, files in os.walk(compile_target):
        file_name = "messages.po" if "messages.po" in files else None
        if file_name:
            po_file=os.path.join(root,file_name)
            mo_dir=root.replace(r"./locale",locale_target)
            mo_file=os.path.join(mo_dir,"messages.mo")
            if not os.path.exists(mo_dir):
                os.makedirs(mo_dir)
                print "Created dir: %s"%mo_dir

            c = "pybabel compile -f -i %s -o %s " % (po_file, mo_file)
            print c
            os.system(c)


if __name__ == "__main__":
    babel_cfg = os.path.join(".", "babel.cfg")
    compile_target = os.path.join(".", "locale")
    target = os.path.join("..", "src")
    locale_target = os.path.join(target, "locale")
    msgs_pot = os.path.join(compile_target, "messages.pot")

    os.system("pybabel extract -F %s -o %s %s" % (babel_cfg, msgs_pot, target))
    locales = ["en_US", "pt_BR"]
    for loc in locales:
        create_or_update_catalog(loc, compile_target, msgs_pot)

    compile_po_files(compile_target, locale_target)




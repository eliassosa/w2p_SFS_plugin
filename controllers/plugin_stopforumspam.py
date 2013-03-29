# -*- coding: utf-8 -*-
from plugin_stopforumspam import StopForumSpam as SFS
import os

folder = os.path.join(request.folder, 'private', 'stopforumspam')

def create_folder(folder):
    if not os.path.isdir(folder):
        os.makedirs(folder)

#@auth.requires_login()
def index():
    create_folder(folder)
    form = FORM(
        INPUT(_type="file", _name="zipfile"),
        BR(),
        BUTTON("Upload a new file", _type="submit")
        )
    if form.process().accepted and 'zipfile' in form.vars:
        filename = os.path.join(folder, os.path.basename(form.vars.zipfile.filename))
        with open(filename, 'wb') as g:
            g.write(form.vars.zipfile.file.read())
    elif form.errors:
        response.flash = 'No file selected'
    else:
        response.flash = 'Please upload your file'

    files = os.listdir(folder)

    return dict(form=form, files=files)

def import_file():
    filename = request.vars.filename
    if not filename:
        raise HTTP(404)
    filename = os.path.join(folder, filename)
    if not os.path.isfile(filename):
        raise HTTP(404)
    print 'called on %s' % filename
    sfs = SFS(db)
    sfs.import_from_file(filename)
    return 'ok'


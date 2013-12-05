# -*- coding: utf-8 -*-
"""  StreetSign Digital Signage Project
     (C) Copyright 2013 Daniel Fairhead

    StreetSign is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    StreetSign is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with StreetSign.  If not, see <http://www.gnu.org/licenses/>.

    ---------------------------
    uploaded image post type.

"""



from flask import render_template_string, request, g, flash
from werkzeug import secure_filename # pylint: disable=no-name-in-module
from os.path import splitext, join as pathjoin, isdir, abspath
from subprocess import check_call
from os import makedirs

def my(ending):
    ''' given '.html', returns (if this is the foobar module)
        the contents of: /where/this/file/is/foodbar.html '''

    with open(splitext(abspath(__file__))[0] + ending,'r') as f:
        return f.read()

def allow_filetype(filename):
    return splitext(filename)[-1].lower() in \
        ['.png','.jpg','.jpeg','.gif','.bmp','.svg']

def form(data):
    return render_template_string(my('.form.html'), **data)

def receive(data):
    if 'upload' in data:
        f = request.files['image_file']
        if f and allow_filetype(f.filename):
            filename = secure_filename(f.filename)
            where = pathjoin(g.site_vars['user_dir'],'post_images')
            if not isdir(where):
                makedirs(where)

            f.save(pathjoin(where, filename))
            try:
                check_call([splitext(abspath(__file__))[0] +'.makesmall.sh',
                        pathjoin(where, filename)])
                flash ('image imported and resized')
            except:
                flash('tried to resize... oh well.')
        else:
            raise IOError('Invalid file. Sorry')
    else:
        filename = data.get('filename')
        if filename and allow_filetype(filename):
            filename = secure_filename(filename)
        else:
            raise Exception('Tried to change the file, huh? Not happening')
            # TODO

    return {'content': filename,
            'filename': filename,
            'file_url': g.site_vars['user_url']+'/post_images/'+filename}

def display(data):
    return ('<img class="post_image" src="{0}"'
           ' style="width:100%;height:auto" />'.format(data['file_url']))

def screen_js():
    return my('.screen.js')
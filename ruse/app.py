 #
 # Copyright (c) 2012 Meg Ford
 #
 # Ruse is free software; you can redistribute it and/or modify
 # it under the terms of the GNU General Public License as published by the
 # Free Software Foundation; either version 2 of the License, or (at your
 # option) any later version.
 #
 # Ruse is distributed in the hope that it will be useful, but
 # WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY
 # or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License
 # for more details.
 #
 # You should have received a copy of the GNU General Public License along
 # with Ruse; if not, write to the Free Software Foundation,
 # Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
 #
 # Author: Meg Ford <megford@gnome.org>
 #
 #
from flask import Flask
from flask import render_template
from flask import redirect, url_for, request, session, g, flash
import flask.views
import os
import webcolors
import gdata.photos.service
import gdata.media
import gdata.geo
import struct
import Image
import scipy
import scipy.misc
import scipy.cluster
import urllib, cStringIO
from random import randint, randrange
from werkzeug import secure_filename
 
app = flask.Flask(__name__)
col =''
@app.route('/')
def colorRand(): 
    color = genRandomColor()
    global col
    col = color 
    return render_template('hello.html', randomColor=col)

@app.route('/', methods=['GET', 'Post'])
def get():
    required = ""
    required = flask.request.form['pics']
    if required == "":
        color1=genRandomColor()
        global col
        col = color1
        return render_template('hello.html', randomColor = col, hexcol=col)
    if required != "":
        print col
        print 'next!'
        picturestr1, picturestr2, picturestr3 = get_pictures(required)
        if picturestr1 != 'none' and picturestr2 == 'none' and picturestr3 == 'none':
            return render_template('picture.html', photoUrl1=picturestr1)
        if picturestr1 != 'none' and picturestr2 != 'none' and picturestr3 == 'none':
            return render_template('picture2.html', photoUrl1=picturestr1, photoUrl2=picturestr2)
        if picturestr1 != 'none' and picturestr2 != 'none' and picturestr3 != 'none':
            return render_template('picture3.html', photoUrl1=picturestr1, photoUrl2=picturestr2, photoUrl3=picturestr3)
        if picturestr1 == 'none' and picturestr2 == 'none' and picturestr3 == 'none':
            color1=genRandomColor()
            col = color1
            return render_template('hello.html', randomColor = col, hexcol=col)


def genRandomColor():
     a = [0, 0, 0, 0, 0, 0]
     for i in range(0, 6):
      num1 = randint(0, 1)
      if num1 == 0:
          # Generate number
          num2 = randint(48, 57)
      else:
          # Generate letter
          num2 = randint(65, 70)
      a[i] = num2
      b = [a, a, a, a, a, a]
      for i in range(0, 6):
        b[i] = chr(a[i])
      thestr = "#"
     for i in range(0, 6):
      thestr = thestr + b[i]
     print thestr
     return thestr 

def get_pictures(required):
    gd_client = gdata.photos.service.PhotosService()
    photos = gd_client.SearchCommunityPhotos(required, limit='50')
    no_error = False
    j = 0
    count = 0
    purl1 = 'none'
    purl2 = 'none'
    purl3 = 'none'
    for photo in photos.entry:
        if j < 50:
            purl=photo.content.src
            NUM_CLUSTERS = 5
            print 'reading image'
            URL = purl
            file = cStringIO.StringIO(urllib.urlopen(URL).read())
            im = Image.open(file)
            im = im.resize((150, 150))      # optional, to reduce time
            ar = scipy.misc.fromimage(im)
            shape = ar.shape
            ar = ar.reshape(scipy.product(shape[:2]), shape[2])
            print 'finding clusters'
            codes, dist = scipy.cluster.vq.kmeans(ar, NUM_CLUSTERS)
            print 'cluster centres:\n', codes
            vecs, dist = scipy.cluster.vq.vq(ar, codes)         # assign codes
            counts, bins = scipy.histogram(vecs, len(codes))    # count occurrences
            index_max = scipy.argmax(counts)                    # find most frequent
            peak = codes[index_max]
            color = ''.join(chr(c) for c in peak).encode('hex')
            various=''.join(['#', color])
            new_color=get_color_name(various, peak)
            new_name=webcolors.name_to_hex(new_color, spec='css3')
            print new_name
            print 'most frequent is %s (#%s)' % (peak, color)
            cat = col.lower()
            req = webcolors.hex_to_rgb(cat)
            new_cat=get_color_name(cat, req)
            print cat
            j += 1
            print j
            if new_color == new_cat:
                no_error = True
                count += 1
                print count
                if count == 1:
                    purl1 = purl
                if count == 2:
                    purl2 = purl
                if count == 3:
                    purl3 = purl
            if j == 50 or count == 3: 
                return purl1, purl2, purl3            

def get_color_name(various, peak):
        try:
        	closest_name = actual_name = webcolors.hex_to_name(various)
        except ValueError:
        	closest_name = closest_color(peak)
        	actual_name = None
	print "Actual color name:", actual_name, ", closest color name:", closest_name
        return closest_name
     
def closest_color(peak):
    min_colors = {}
    for key, name in webcolors.css3_hex_to_names.items():
        r_c, g_c, b_c = webcolors.hex_to_rgb(key)
        rd = (r_c - peak[0]) ** 2
        gd = (g_c - peak[1]) ** 2
        bd = (b_c - peak[2]) ** 2
        min_colors[(rd + gd + bd)] = name
    return min_colors[min(min_colors.keys())]
if __name__ == '__main__':
    app.run('cs.neiu.edu',8081)
    

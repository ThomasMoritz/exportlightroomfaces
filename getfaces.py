#!/usr/bin/python
# -*- coding: utf-8 -*-

import sqlite3
import os.path
from PIL import Image
import piexif
import argparse

# Commandline Handling

parser = argparse.ArgumentParser(description='Export faces from Lightroom DB')
parser.add_argument('-d', '--database', help='Input Database', required=True)
parser.add_argument('-o', '--output', help='Output Directory', required=True)
parser.add_argument('-n', '--name', help='Name of Person', required=True)
args = parser.parse_args()

# Add trailing slash to output path if missing
output_path = os.path.join(args.output, '')
# get the working directory
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# load the Lightroom Database
db_path = os.path.join(BASE_DIR, args.database)
conn = sqlite3.connect(db_path)
conn.row_factory = sqlite3.Row
cursor = conn.execute(
    'select Folder.pathFromRoot, File.baseName, File.extension, File.folder,Hist.*, Faces.*, kwf.*,kw.*,rf.* from  Adobe_libraryImageFaceProcessHistory AS Hist inner join Adobe_images AS Img ON Hist.image = Img.id_local  inner join AgLibraryFile AS File on  Img.rootFile = File.id_local inner join AgLibraryFolder AS Folder on File.folder = Folder.id_local inner join AgLibraryFace AS Faces on Hist.image = Faces.image inner join AgLibraryKeywordFace As kwf  on Faces.id_local = kwf.face inner join AgLibraryKeyword as kw on kwf.tag = kw.id_local inner join AgLibraryRootFolder as rf on Folder.rootFolder = rf.id_local where lc_name  like "' + args.name + '"   order by dateCreated')
# iterate over all images the contain the face
for row in cursor:
    img = Image.open(row['absolutePath'] + row['pathFromRoot'] + row['baseName'] + '.' + row['extension'])
    print row['absolutePath'] + row['pathFromRoot'] + row['baseName'] + '.' + row['extension']
    x_size, y_size = img.size
    orientation = ""

    if "exif" in img.info:
        exif_dict = piexif.load(img.info["exif"])
        if piexif.ImageIFD.Orientation in exif_dict["0th"]:
            orientation = exif_dict["0th"].pop(piexif.ImageIFD.Orientation)
            if orientation == 2:
                img = img.transpose(Image.FLIP_LEFT_RIGHT)
            elif orientation == 3:
                img = img.rotate(180)
            elif orientation == 4:
                img = img.rotate(180).transpose(Image.FLIP_LEFT_RIGHT)
            elif orientation == 5:
                img = img.rotate(-90).transpose(Image.FLIP_LEFT_RIGHT)
            elif orientation == 6:
                img = img.rotate(-90, expand=True)
            elif orientation == 7:
                img = img.rotate(90).transpose(Image.FLIP_LEFT_RIGHT)
            elif orientation == 8:
                img = img.rotate(90, expand=True)

    else:
        exif_dict = ""

    exif_bytes = piexif.dump(exif_dict)
    # Workaround to fix orientation Problems
    img.save('temp.' + row['extension'], exif=exif_bytes)
    img2 = Image.open('temp.' + row['extension'])
    x_new_size, y_new_size = img2.size
    # set the space around the face
    clipping_factor = 75
    # calculate Image Size based on Image orientation
    if orientation == 6 or orientation == 8 or orientation == -1:
        top_x = row['tl_x'] * y_size
        top_y = row['tl_y'] * x_size
        bottom_x = row['br_x'] * y_size
        bottom_y = row['br_y'] * x_size
    else:
        top_x = row['tl_x'] * x_size
        top_y = row['tl_y'] * y_size
        bottom_x = row['br_x'] * x_size
        bottom_y = row['br_y'] * y_size

    # Extend the Clipping
    while True:
        d_top_x = int(top_x - clipping_factor)
        d_top_y = int(top_y - clipping_factor)
        d_bottom_x = int(bottom_x + clipping_factor)
        d_bottom_y = int(bottom_y + clipping_factor)
        # Check if Clipping Frame ist bigger then actual Image

        if (d_top_x >= 0 and d_top_y >= 0 and d_bottom_x < x_new_size and d_bottom_y < y_new_size):
            top_x = int(top_x - clipping_factor)
            top_y = int(top_y - clipping_factor)
            bottom_x = int(bottom_x + clipping_factor)
            bottom_y = int(bottom_y + clipping_factor)
            break
            # decrement factor till it fits
            clipping_factor -= 1
    # finaly - crop the image
    img3 = img2.crop((top_x, top_y, bottom_x, bottom_y))
    # dump the old exif data to the image
    exif_bytes = piexif.dump(exif_dict)
    # save me! now!
    img3.save(output_path + row['name'] + "_" + row['baseName'] + '_neu' + '.' + row['extension'], exif=exif_bytes)

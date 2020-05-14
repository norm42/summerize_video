#
# Copyright https://github.com/norm42/summerize_video/blob/master/LICENSE.md
# (Mit license)
#
import os
import sys
import vidimg as vi
from datetime import date
from datetime import time
from datetime import timedelta


def out_img_header(f):
    f.write('{% extends "base.html" %} \n')
    f.write('{% block title %}Flasky{% endblock %} \n')
    f.write('{% block page_content %} \n')
    f.write('<div class="container-fluid"> \n')
    f.write('<meta charset="utf-8">\n')
    f.write('<div class="container">\n')
    return ()


def out_div(f):
    f.write('</div>\n')
    f.write('<div class="container-fluid">\n')


def out_img_blk(f, image_name, vid_date, vid_time):
    # take in f (file to write to),file name, date, time
    # file name is a vid:jpg combined name.
    sdate = vid_date[0:4] + '-' + vid_date[4:6] + '-' + vid_date[6:8] + ' '
    stime = vid_time[0:2] + ':' + vid_time[2:4] + ':' + vid_time[4:6]
    sepfiles = image_name.split(":")
    vidfile = "vid/" + sepfiles[0]
    jpgfile = "img/" + sepfiles[1]
    # f.write('    <div class="alert alert-success"> \n')
    # f.write('        <h3>' + sdate + stime + '</h3> \n')
    # f.write('    </div> \n')
    # f.write('    <img src="' + image_name + '" height="540" width="960" > \n')

    f.write('    <a href=#>\n')
    f.write('        <button type="button" class="btn btn-primary">' + sdate + stime + '</button>\n')
    f.write('    </a>\n')
    f.write('    <div>\n')
    f.write('    <video width="960" height="540" poster={{ url_for("static", filename="' + \
            jpgfile + '") }} controls preload="none">\n')
    f.write('       <source src={{ url_for("static", filename="' + vidfile + '") }} type="video/mp4">\n')
    f.write('    </video>\n')
    f.write('    </div>\n')
    return ()


def out_img_end(f):
    f.write('</div> \n')
    f.write('{% endblock %} \n')
    return ()


def img_date_time(img_name):
    cam_date = img_name.split(".")  # get rid of ".jpg"
    jpg_date_time = cam_date[0].split("_")
    return (jpg_date_time[1], jpg_date_time[2])  # date time


def out_img_button(f, img_date_list):
    for uniq_date in img_date_list:
        f.write('    <a href="#' + uniq_date + '" > \n')
        f.write('        <button type="button" class="btn btn-primary">' + uniq_date + '</button>\n')
        f.write('    </a>\n')


def out_date_tag(f, img_date):
    f.write('    <h2 id="' + img_date + '">' + img_date + '</h2>\n')


def sel_one(list_element):
    return (list_element[1])


def do_html_file(outfile_name, filter_date=None):
    walk_dir = "static/img/"
    img_list = []
    date_list = []
    jpg_dir = "./static/img"
    vid_dir = "./static/vid"

    vidimg_list = vi.make_file_pair(jpg_dir, vid_dir)

    if filter_date is not None:
        vidimg_list = vi.filter_date(vidimg_list, filter_date)

    if len(vidimg_list) == 0:
        return
    html_name = "templates/" + outfile_name
    out_file = open(html_name, "w")
    out_img_header(out_file)

    for entry in vidimg_list:
        camdate = entry.split(":")
        img_date, img_time = img_date_time(camdate[1])
        img_comb = img_date + img_time
        date_list.append(img_date)
        img_list.append((entry, img_comb, img_date, img_time))

    img_list.sort(key=sel_one, reverse=True)
    # for i in img_list:
    #    print(i[0])

    img_date_unique = list(set(date_list))
    img_date_unique.sort(reverse=True)
    # print(img_date_unique)
    # do Buttons
    out_img_button(out_file, img_date_unique)
    out_div(out_file)

    for uniq_date in img_date_unique:
        # print unique date tag
        out_date_tag(out_file, uniq_date)
        for vid_date in img_list:
            if vid_date[2] == uniq_date:
                out_img_blk(out_file, vid_date[0], vid_date[2], vid_date[3])
                # print(vid_date[0], " ", vid_date[2])
        # print("------------------------------------------")

    out_img_end(out_file)
    out_file.close()

# this is the full file
do_html_file("imglist.html")

# generate the html for today
x = date.today()
y = str(x)
z = y.replace("-", "")  # make into yyyymmdd
print(z)
do_html_file("imglist_today.html", z)

# generate the html for yesterday
d_yesterday = x - timedelta(days=1)
d_y_str = str(d_yesterday)
d_y_yyyymmmddd = d_y_str.replace("-", "")
print(d_y_yyyymmmddd)
do_html_file("imglist_yesterday.html", d_y_yyyymmmddd)



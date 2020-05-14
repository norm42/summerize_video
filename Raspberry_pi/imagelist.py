#
# Copyright https://github.com/norm42/summerize_video/blob/master/LICENSE.md
# (Mit license)
#
from flask import Flask, render_template, jsonify, request
from flask_bootstrap import Bootstrap
import os
import sys
import json, signal

app = Flask(__name__)

bootstrap = Bootstrap(app)


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'), 500


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/today')
def today():
    return render_template("imglist_today.html")
    
@app.route('/yesterday')
def yesterday():
    return render_template("imglist_yesterday.html")
    
    
@app.route('/image')
def image():
    return render_template('imglist.html')

#ug - does not work...
#@app.route('/stopServer', methods=['GET'])
#def stopServer():
#    print("PID: ", os.getpid())
#    os.kill(os.getpid(), signal.SIGKILL)
#    return jsonify({ "success": True, "message": "Server is shutting down..." })

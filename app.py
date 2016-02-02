from flask import Flask, render_template, request, redirect, url_for, g
from werkzeug import secure_filename
import sys
import os
import sqlite3
import short_url
from get_thumbnail import get_thumbnail

DEBUG= True
BASE_DIR='/var/www/html/'
STATIC_DIR='/../static/'
TEMPLATES_DIR='/../templates/'
UPLOAD_FOLDER = '/var/www/html/pics/'
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif', 'PNG', 'JPG', 'JPEG', 'GIF'])

app = Flask(__name__)

def save_thumbnail(imgpath):
	imgin = 'pics/'+imgpath
	imgout = '/var/www/html/pics/thumbnails/'+imgpath+'.jpg'
	get_thumbnail(imgin, imgout)

def connect_db():
	return sqlite3.connect('db.db')

@app.before_request
def before_request():
	g.db = connect_db()

def recentlyUploaded():
	#SELECT imgpath FROM pics ORDER BY id DESC LIMIT 8
	recently = []
	n = g.db.execute('SELECT imgpath,url FROM pics ORDER BY id DESC LIMIT 12')
	for i in n:
		recently.append(i)
	return recently

def get_last_id():
	#SELECT id FROM pics ORDER BY id DESC LIMIT 1;
	n = g.db.execute('SELECT id FROM pics ORDER BY id DESC LIMIT 1;').fetchone()[0]
	return n

def allowed_file(filename):
	return '.' in filename and filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

@app.route("/", methods=['GET', 'POST'])
def upload_img():
	#http://flask.pocoo.org/docs/0.10/patterns/fileuploads/
	if request.method == 'POST':
		file = request.files['file']
		if file and allowed_file(file.filename):
			try:
				filename = secure_filename(file.filename)
				if len(filename) > 30:
					filename = filename[0:30]+'~.'+filename.split('.')[-1]
				new_id = get_last_id() + 1
				new_filename = filename
				new_url = short_url.encode_url(new_id)
				img_path = new_url+'.'+filename.split('.')[-1]
				file.save(os.path.join(UPLOAD_FOLDER, img_path))
				g.db.execute("INSERT INTO pics (id, filename, url, imgpath) VALUES (?, ?, ?, ?)", (new_id, new_filename, new_url, img_path))
				g.db.commit()
				save_thumbnail(img_path)
				#return redirect(url_for('upload_img', filename=filename))
				return redirect('/show/'+new_url)
			except Exception as e:
				return str(e)
		else:
			return "Wrong file!"
	else:
		recent = recentlyUploaded()
		return render_template('index.html', STATIC_DIR = STATIC_DIR, TEMPLATES_DIR=TEMPLATES_DIR, recent = recent,)

@app.route('/show/<fileurl>')
def show_pic(fileurl):
	#SELECT url FROM pics;
	urls = g.db.execute('SELECT url FROM pics;')
	for url in urls:
		if fileurl == url[0]:
			#SELECT * FROM pics WHERE url = '25t52';
			data = g.db.execute("SELECT * FROM pics WHERE url = (?)", (fileurl,)).fetchall()[0]
			img = '/pics/'+data[3]
			# 0 - id
			# 1 - filename
			# 2 - url
			# 3 - imgpath
			filename = data[1]
			imgurl = data[2]
			return render_template('show.html', STATIC_DIR = STATIC_DIR, TEMPLATES_DIR=TEMPLATES_DIR, filename=filename, img=img, imgurl=imgurl)
	else:
		return 'Wrong url!'

	

if __name__ == "__main__":
	app.run(host='0.0.0.0', port=8080,debug=DEBUG)
	app.config['MAX_CONTENT_LENGTH'] = 3 * 16 * 1024 * 1024

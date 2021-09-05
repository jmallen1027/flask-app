
import os ## Importing Operating System for Docker File
import sys
import json
import requests
from tracing import init_tracer, flask_to_scope
import opentracing
from opentracing.ext import tags
from opentracing_instrumentation.client_hooks import install_all_patches
from flask_opentracing import FlaskTracer
from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from datetime import datetime

app = Flask(__name__)
init_tracer('clean Blog')
install_all_patches()
flask_tracer = FlaskTracer(opentracing.tracer, True, app)

app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:Vikings123!@localhost:3306/blog'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
migrate = Migrate(app, db)



class Blogpost(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(50))
    subtitle = db.Column(db.String(50))
    author = db.Column(db.String(20))
    date_posted = db.Column(db.DateTime)
    content = db.Column(db.Text)

@app.route('/')
def index():
    with flask_to_scope(flask_tracer, request) as scope:
        posts = Blogpost.query.order_by(Blogpost.date_posted.desc()).all()
        opentracing.tracer.active_span.set_tag('response', posts)
        return render_template('index.html', posts=posts)

@app.route('/about')
def about():
    #with tracer.start_as_current_span("about") as span:
    return render_template('about.html')

@app.route('/post/<int:post_id>')
def post(post_id):
    #with tracer.start_as_current_span("post") as span:
    post = Blogpost.query.filter_by(id=post_id).one()

    return render_template('post.html', post=post)

@app.route('/add')
def add():
    #with tracer.start_as_current_span("add") as span:
    return render_template('add.html')

@app.route('/addpost', methods=['POST'])
def addpost():
    #with tracer.start_as_current_span("add/post") as span:
    title = request.form['title']
    subtitle = request.form['subtitle']
    author = request.form['author']
    content = request.form['content']

    post = Blogpost(title=title, subtitle=subtitle, author=author, content=content, date_posted=datetime.now())

    db.session.add(post)
    db.session.commit()

    return redirect(url_for('index'))

#if __name__ == '__main__':
    #port = int(os.environ.get('PORT', 5000))
    #app.run(host='0.0.0.0', port=port, debug=True)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5003)

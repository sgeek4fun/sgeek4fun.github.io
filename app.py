import os
from flask import Flask, session, abort, redirect, request, render_template, url_for, flash,send_file
from flask_mail import Mail, Message
import imghdr
from wtforms.validators import ValidationError
from flask_sqlalchemy import SQLAlchemy
from flask_admin import Admin
from flask_admin.form.upload import FileUploadField
from flask_admin.contrib.sqla import ModelView
from flask_admin.contrib.fileadmin import FileAdmin
import random
import base64
import sqlalchemy
from config import mail_username, mail_password, admin_login_username, admin_login_password, recipients_email

basedir= os.path.abspath(os.path.dirname(__file__))
app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] =\
        'sqlite:///' + os.path.join(basedir, 'sk.db')
app.config['SECRET_KEY'] = '34FIB0EJDFKJSVWKJDJF0VWIJJ'
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USE_SSL'] = False
app.config['MAIL_USERNAME'] = mail_username
app.config['MAIL_PASSWORD'] = mail_password



db = SQLAlchemy(app)
admin = Admin(app, name='microblog', template_mode='bootstrap3')
mail = Mail(app)

class Posts(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    category = db.Column(db.String(255))
    title = db.Column(db.String(255))
    subtitle = db.Column(db.String(255))
    content = db.Column(db.Text)
    author = db.Column(db.String(255))
    date_posted = db.Column(db.DateTime)
    slug = db.Column(db.String(255))
    image_name = db.Column(db.String(255))


class SecureModelView(ModelView):
    def is_accessible(self):
        if "logged_in" in session:
            return True
        else:
            abort(403)


admin.add_view(SecureModelView(Posts, db.session))
path = os.path.join(os.path.dirname(__file__), 'static')
admin.add_view(FileAdmin(path, '/static/', name='Static Files'))


@app.route("/")
def index():
    posts = Posts.query.all()
    return render_template('index.html', posts=posts)


@app.route("/post/<string:slug>")
def post(slug):
    try:
        post = Posts.query.filter_by(slug=slug).one()
        return render_template("post.html", post=post)
    except sqlalchemy.exc.NoResultFound:
        abort(404)

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        if request.form.get("username") == admin_login_username and request.form.get("pass") == admin_login_password:
            session['logged_in'] = True
            return redirect("/admin")
        else:
            return render_template("login.html", failed=True)
    return render_template("login.html")
    

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")

@app.route("/contact", methods=['GET', 'POST'])
def contact():
    if request.method == "POST":
        name = request.form.get('name')
        email = request.form.get('email')
        message = request.form.get('message')

        msg = Message(subject=f"Mail from {name}", body=f"Name: {name}\nE-mail: {email}\n{message}\n\n\n", sender=mail_username, recipients=[recipients_email])
        mail.send(msg)
        return render_template("contact.html", success=True)
    return render_template("contact.html")

if __name__ == "__main__":
    app.run(host="0.0.0.0")

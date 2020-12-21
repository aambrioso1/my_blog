# Three thing I would like to do with this:
# (1)  Make a properly authenticated login for a single user. Look at the LoginManager docs.
# (2)  Display all the POSTS on one page rather than all the links.
# (3)  Find a way to include comments without using Disqus.

from flask import Flask, render_template_string, redirect
from sqlalchemy import create_engine, MetaData
from flask_login import UserMixin, LoginManager, login_user, logout_user
from flask_blogging import SQLAStorage, BloggingEngine

import os
basedir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)
app.config["SECRET_KEY"] = "secret"  # for WTF-forms and login
app.config["BLOGGING_URL_PREFIX"] = "/blog"
# Leaving this configuration out removes the comment section AND the sponsored ads!
# app.config["BLOGGING_DISQUS_SITENAME"] = "test" 
app.config["BLOGGING_SITEURL"] = "https://alexambrioso.com"
app.config["BLOGGING_SITENAME"] = "My Site"
app.config["BLOGGING_KEYWORDS"] = ["blog", "meta", "keywords"]
app.config["FILEUPLOAD_IMG_FOLDER"] = "fileupload"
app.config["FILEUPLOAD_PREFIX"] = "/fileupload"
app.config["FILEUPLOAD_ALLOWED_EXTENSIONS"] = ["png", "jpg", "jpeg", "gif"]

# This configuration will make the app less hackable.
app.config["ADMIN_PASSWORD"] = os.environ.get("ADMIN_PASSWORD")

# extensions
db_file = 'sqlite:///' + os.path.join(basedir, 'data-dev.sqlite')
engine = create_engine(db_file)
meta = MetaData()
sql_storage = SQLAStorage(engine, metadata=meta)
blog_engine = BloggingEngine(app, sql_storage)
login_manager = LoginManager(app)
meta.create_all(bind=engine)
    
class User(UserMixin):
    def __init__(self, user_id):
        self.id = user_id

    def get_name(self):
        return "Alex Ambrioso"  # typically the user's name

@login_manager.user_loader
@blog_engine.user_loader
def load_user(user_id):
    return User(user_id)

index_template1 = """
<!DOCTYPE html>
<html>

    <link rel="shortcut icon" href="{{ url_for('static', filename='favicon.ico') }}" type="image/x-icon">
    <link rel="icon" href="{{ url_for('static', filename='favicon.ico') }}" type="image/x-icon">
    <title>Alex's Blog</title>
    <head> </head>

    <body>

        {% if current_user.is_authenticated %}
            <a href="/logout/"> Logout </a>
        {% else %}
            <a href="/login/"> Login </a>
        {% endif %}
        &nbsp&nbsp<a href="/blog/"> Blog </a>
        &nbsp&nbsp<a href="/blog/sitemap.xml">Sitemap</a>
        &nbsp&nbsp<a href="/blog/feeds/all.atom.xml">ATOM</a>
        &nbsp&nbsp<a href="/fileupload/">FileUpload</a>
    </body>
</html>
"""

index_template2 = """
<!DOCTYPE html>
<html>
    <body>
        
        <link rel="shortcut icon" href="{{ url_for('static', filename='favicon.ico') }}" type="image/x-icon">
        <link rel="icon" href="{{ url_for('static', filename='favicon.ico') }}" type="image/x-icon">
            
        <title>Alex's Blog</title>
            <head>

            

                &nbsp&nbsp<a href="/blog/"> Blog </a>
                &nbsp&nbsp<a href="/blog/sitemap.xml">Sitemap</a>
                &nbsp&nbsp<a href="/blog/feeds/all.atom.xml">ATOM</a>
                &nbsp&nbsp<a href="/fileupload/">FileUpload</a>
                
            </head>
    </body>
</html>
"""

@app.route("/")
def index():
    print('inside index')
    return redirect("/blog/")

@app.route("/login/<string:name>")
def login(name):
    user = User(name)
    print(f"inside login: name = {name}")
    if name == app.config["ADMIN_PASSWORD"]:
        print('inside if, inside login')
        login_user(user)
        return redirect("/blog/")
    else:
        print('inside else, inside login')
        logout_user()
        return redirect("/blog/")

@app.route("/logout/")
def logout():
    print('inside logout')
    logout_user()
    return redirect("/blog/")

@app.route("/blog/testing/<string:name>")
def testing(name):
    print("inside testing")
    text = os.environ.get('ADMIN_PASSWORD')
    return f'<h1>text = { text } </h1>'
    # return render_template_string(index_template2)

# This main function is needed to get wsgi to work properly with my deployment method.
# Need confirm this fact.
def main():
    app.run(debug=True, port=5000)

#  Included so we can also run the app using flask run.
if __name__ == "__main__":
    app.run(debug=True, port=5000, use_reloader=True)

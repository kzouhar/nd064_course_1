import sqlite3
import logging
import sys

from flask import Flask, jsonify, json, render_template, request, url_for, redirect, flash

# Define the Flask application
app = Flask(__name__)
app.config['SECRET_KEY'] = 'your secret key'
app.connection_count = 0

stdout_fileno = sys.stdout

# Function to get a database connection.
# This function connects to database with the name `database.db`
def get_db_connection():
    connection = sqlite3.connect('database.db')
    connection.row_factory = sqlite3.Row
    return connection

# Function to get a post using its ID
def get_post(post_id):

    connection = get_db_connection()
    app.connection_count = app.connection_count + 1
    post = connection.execute('SELECT * FROM posts WHERE id = ?',
                        (post_id,)).fetchone()
    connection.close()
    return post

# Define the main route of the web application 
@app.route('/')
def index():
    connection = get_db_connection()
    posts = connection.execute('SELECT * FROM posts').fetchall()
    connection.close()
    return render_template('index.html', posts=posts)

# Define how each individual article is rendered 
# If the post ID is not found a 404 page is shown
@app.route('/<int:post_id>')
def post(post_id):
    post = get_post(post_id)
    if post is None:
      app.logger.info('Article with id {} is non existing in database'.format(post_id))
      return render_template('404.html'), 404
    else:
      app.logger.info('Article {} retrieved!'.format(post['title']))

    return render_template('post.html', post=post)

# Define the About Us page
@app.route('/about')
def about():
    app.logger.info('About Us page is retrieved!')
    return render_template('about.html')

# Define the post creation functionality 
@app.route('/create', methods=('GET', 'POST'))
def create():

    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']

        if not title:
            flash('Title is required!')
        else:
            connection = get_db_connection()
            app.connection_count = app.connection_count + 1
            connection.execute('INSERT INTO posts (title, content) VALUES (?, ?)',
                         (title, content))
            connection.commit()
            connection.close()
            app.logger.info('Article {} created!'.format(title))

            return redirect(url_for('index'))

    return render_template('create.html')

@app.route('/healthz')
def healthz():
    app.logger.info('Health check successful')
    return app.response_class(response=json.dumps({"result":"OK - health"}),
                       status=200,
                       mimetype='application/json'
                       )

@app.route('/metrics')
def metrics():
    connection = get_db_connection()
    total_post = connection.execute('SELECT count(*) c FROM posts').fetchone()
    app.logger.info('Metrics request successfull')
    return app.response_class(response=json.dumps({"db_connection_count" :  app.connection_count,  "post_count": total_post[0]}),
                       status=200,
                       mimetype='application/json'
                       )


class LessThenFilter(logging.Filter):
    def __init__(self, level):
        self._level = level
        logging.Filter.__init__(self)

    def filter(self, rec):
        return rec.levelno < self._level

# start the application on port 3111
if __name__ == "__main__":
   ## stream logs to app.log file
   logging.basicConfig(
       level=logging.DEBUG,
       format='%(levelname)s:%(asctime)s %(message)s',
       datefmt='%m/%d/%Y %I:%M:%S %p',
       handlers=[
           logging.StreamHandler(sys.stdout)
           logging.StreamHandler(sys.stderr)
       ]
   )


   app.run(host='0.0.0.0', port="3111")




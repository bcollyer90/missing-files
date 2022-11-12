from flask import Flask, request, render_template
from queues import make_celery
import os
import glob
from settings import *

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = upload_folder

app.config.update(CELERY_CONFIG={
    'broker_url': f'redis://:{redis_password}4@{redis_host}:6379',
    'result_backend': f'redis://:{redis_password}@{redis_host}:6379',
})

celery = make_celery(app)
app.celery = celery


@app.post('/upload')
def upload():
    files = request.files
    for f in files:
        file = files.get(f)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], file.filename))
    return """Done! <a href="/">Go back</a>?"""


@app.route("/")
def index():
    files = [os.path.basename(x) for x in glob.glob(f"{upload_folder}/*")]
    return render_template("index.html", files_waiting=files)


@app.route("/index/update")
def update():
    celery.send_task('tasks.index_missing_files')
    return """That will be done in the next 15 minutes. <a href="/">Go back</a>?"""


@app.route("/files/move")
def move_files():
    celery.send_task('tasks.move_files')
    return """That will be finished in a few minutes... <a href="/">Go back</a>?"""


if __name__ == "__main__":
    app.run(port=8000)

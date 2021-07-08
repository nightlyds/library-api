from library import app, db


@app.route("/")
def hello_world():
    return "Hello world!"
from flask import Flask, render_template, request
from flask import session as flask_session


app = Flask(__name__)

@app.route("/")
def homepage():
    return "Hellowww Worldy"




if __name__ == "__main__":
    app.run(debug = True)


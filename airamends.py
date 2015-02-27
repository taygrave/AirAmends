from flask import Flask, render_template, request, g, flash, redirect
from flask import session as flask_session
import gmailapiworks
import seed_flights


app = Flask(__name__)
app.secret_key = '\xa7G\x83\xda\x9f\xd3\x9f\xfc\x19\xdd\x08E\x91\x9a\xbd\x9b\x00\xe4o\xe8i?\xb8\x06'

@app.before_request
def before():
    g.user = flask_session.get('user')
    if g.user == None :
        g.status = "Log In"
    else:
        g.status = g.user
    #TODO: Set a session variable the keeps travk of which route we're on and sets that one's class to "active" for the navbar

@app.route("/")
def homepage():
    user_flights = "No flights yet"
    return render_template("index.html", user_flights=user_flights)

@app.route("/getflights", methods=["POST"])
def getflights():
    user_flights = seed_flights.find_andseed_airports()
    print user_flights
    return redirect("/")

@app.route("/login", methods=["GET"])
def show_login():
    return render_template("login.html")

@app.route("/login", methods=["POST"])
def process_login():
    """TODO: Receive the user's login credentials located in the 'request.form'
    dictionary, look up the user, and store them in the session."""
    user_email = gmailapiworks.add_msgs_to_db()
    flask_session['user'] = user_email
    flash("Welcome you frequent flyer, you!")
    return redirect("/")

@app.route("/logout", methods=["GET"])
def log_out():
    flask_session.clear()
    flash("You are successfully logged out!")
    return redirect("/")

@app.route("/aboutcalc")
def aboutcalc():
    return render_template("carboncalcs.html")

@app.route("/getflights", methods=['GET'])
def get_flights():
    var = "HELLLLLO"
    return render_template("index.html", var=var)



if __name__ == "__main__":
    app.run(debug = True)


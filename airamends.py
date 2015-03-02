from flask import Flask, render_template, request, g, flash, redirect, jsonify
from flask import session as flask_session
import gmailapiworks, model, seed_flights



app = Flask(__name__)
app.secret_key = '\xa7G\x83\xda\x9f\xd3\x9f\xfc\x19\xdd\x08E\x91\x9a\xbd\x9b\x00\xe4o\xe8i?\xb8\x06'

@app.before_request
def before():
    g.user = flask_session.get('user')
    if g.user == None :
        g.status = "Log In"
    else:
        g.status = g.user
    #TODO: Set a session variable the keeps track of which route we're on and sets that one's class to "active" for the navbar

@app.route("/")
def homepage():
    return render_template("index.html")

@app.route("/getflights", methods=["POST"])
def getflights():
    s = model.connect()
    emails_in_db = len(list(s.query(model.Email).filter(model.Email.user_id == 1).all()))
    if emails_in_db == 0:
        emails_in_db = gmailapiworks.add_msgs_to_db()

    flights_in_db = s.query(model.Flight).filter(model.Flight.user_id == 1).all()
    if flights_in_db == [] or None:
        user_flights = seed_flights.seed_flights()
        CO2e = seed_flights.CO2e_results(user_flights)
        print CO2e
    else: 
        user_flights = s.query(model.Flight).all()
        CO2e = seed_flights.CO2e_results(user_flights)

    years_list = seed_flights.report_by_year()

    return render_template("/getflights.html", emails_in_db=emails_in_db, user_flights=user_flights, CO2e=CO2e, years_list=years_list)

@app.route("/getflights/<year>")
def yearflights(year):
    year = year
    s = model.connect()
    results_list = []
    sum_CO2e = 0
    user_flights = s.query(model.Flight).filter_by(date = year).all()
    
    for flight in user_flights:
        CO2e = seed_flights.calc_carbon((flight.depart, flight.arrive))
        results_list.append((flight.depart, flight.arrive, CO2e))
        sum_CO2e = sum_CO2e + CO2e

    print results_list

    return render_template("/yearflights.html", year=year, results_list=results_list, sum_CO2e=sum_CO2e)

@app.route("/login", methods=["GET"])
def show_login():
    return render_template("login.html")

@app.route("/login", methods=["POST"])
def process_login():
    """TODO: Receive the user's login credentials located in the 'request.form'
    dictionary, look up the user, and store them in the session."""
    gmailapiworks.authorize()
    user_email = gmailapiworks.get_user()
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


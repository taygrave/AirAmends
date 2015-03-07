from flask import Flask, render_template, request, g, flash, redirect, url_for
from flask import session as flask_session
from flask.ext.login import LoginManager
from flask.ext.login import login_user, logout_user, current_user


from model import *
import gmailapiworks, seed_flights
from apiclient.discovery import build_from_document
import httplib2
from oauth2client.client import OAuth2WebServerFlow, AccessTokenCredentials
import config 

app = Flask(__name__)
app.config.from_pyfile('./config.py')
login_manager = LoginManager()
login_manager.init_app(app)

def get_api(credentials):
    http_auth = credentials.authorize(httplib2.Http())
    doc = open("discovery.json")
    print "credentials authorized"
    gmail_service = build_from_document(doc.read(), http = http_auth)
    print gmail_service
    return gmail_service

def get_auth_flow():
    auth_flow = OAuth2WebServerFlow(
        client_id = config.GMAIL_CLIENT_ID,
        client_secret = config.GMAIL_CLIENT_SECRET,
        scope = config.GMAIL_AUTH_SCOPE,
        redirect_uri = url_for('login_callback', _external = True))
    print "auth_flow retreived"
    return auth_flow

@login_manager.user_loader
def load_user(userid):
    print "at user_loader"
    return User.query.get(int(userid))

@app.before_request
def before_request():
    print flask_session.items()
    if current_user.is_authenticated():
        # print "before request getting credentials"
        credentials = AccessTokenCredentials(current_user.access_token, u'')
        # print "before request, retreived credentials"
        g.gmail_api = get_api(credentials)
        # print "before request, built service"

    if flask_session.get('user_id') == None:
        g.status = "Log In"
        g.link = "/login/"
    else:
        #TODO - directly add email to session once retrieved instead of querying db for it each time
        g.status = current_user.email
        g.link = "/logout/"

@app.route("/")
def homepage():
    return render_template("index.html")

@app.route("/map")
def make_map():
    json_array = seed_flights.flights4map()
    return render_template("map.html", jsonarray=json_array)

@app.route("/getflights", methods=["POST"])
def getflights():
    emails_in_db = len(list(Email.query.filter(Email.user_id == current_user.id).all()))
    if emails_in_db == 0:
        emails_in_db = gmailapiworks.add_msgs_to_db(g.gmail_api, current_user.id)

    flights_in_db = Flight.query.filter(Flight.user_id == current_user.id).all()
    if flights_in_db == [] or None:
        user_flights = seed_flights.seed_flights()
        CO2e = seed_flights.CO2e_results(user_flights)
        print CO2e
    else: 
        user_flights = Flight.query.all()
        CO2e = seed_flights.CO2e_results(user_flights)

    years_list = seed_flights.report_by_year()

    return render_template("/getflights.html", emails_in_db=emails_in_db, user_flights=user_flights, CO2e=CO2e, years_list=years_list)

@app.route("/getflights/<year>")
def yearflights(year):
    year = year
    results_list = []
    sum_CO2e = 0
    user_flights = Flight.query.filter_by(date = year).all()
    
    for flight in user_flights:
        CO2e = seed_flights.calc_carbon((flight.depart, flight.arrive))
        #using a backreference here to name the cities for display instead of using their airport codes, for better user recognition
        #TODO consider returning airport codes as well
        date = str(flight.email.date.month) + "/" + str(flight.email.date.day)
        results_list.append((date, flight.departure.city, flight.arrival.city, CO2e))
        sum_CO2e = sum_CO2e + CO2e

    print results_list

    return render_template("/yearflights.html", year=year, results_list=results_list, sum_CO2e=sum_CO2e)

@app.route("/aboutcalc")
def aboutcalc():
    return render_template("carboncalcs.html")

@app.route('/login/')
def login():
    if current_user.is_authenticated():
        return redirect(url_for('homepage'))
    else:
        auth_flow = get_auth_flow()
        auth_uri = auth_flow.step1_get_authorize_url()
        return redirect(auth_uri)

@app.route('/login/callback/')
def login_callback():
    code = request.args.get('code')
    print "at login/callback"
    print code
    auth_flow = get_auth_flow()
    print "got auth_flow"
    credentials = auth_flow.step2_exchange(code)
    print credentials
    gmail_api = get_api(credentials)
    print gmail_api
    gmail_user = gmail_api.users().getProfile(userId = 'me').execute()
    email = gmail_user['emailAddress']
    print email
    access_token = credentials.access_token

    user = User.query.filter_by(email = email).first()
    if user:
        user.access_token = access_token
        session.commit()

    else:
        user = User(email=email, access_token=access_token)
        user.save()
    
    login_user(user, remember = True)

    return redirect(url_for('homepage'))

@app.route('/logout/')
def logout():
    logout_user()
    return redirect(url_for('homepage'))

if __name__ == "__main__":
    app.run(debug = True)


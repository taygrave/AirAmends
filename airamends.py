from flask import Flask, render_template, request, g, redirect, url_for, jsonify, session as flask_session
from flask.ext.login import LoginManager, login_user, logout_user, current_user
import json, re, httplib2, config
from datetime import datetime
from model import *
import gmailapiworks, seed_flights
from apiclient.discovery import build_from_document
from oauth2client.client import OAuth2WebServerFlow, AccessTokenCredentials

app = Flask(__name__)
app.config.from_pyfile('./config.py')
login_manager = LoginManager()
login_manager.init_app(app)

def get_api(credentials):
    http_auth = credentials.authorize(httplib2.Http())
    doc = open("discovery.json")
    gmail_service = build_from_document(doc.read(), http = http_auth)
    print "built service"
    return gmail_service

def get_auth_flow():
    auth_flow = OAuth2WebServerFlow(
        client_id = config.GMAIL_CLIENT_ID,
        client_secret = config.GMAIL_CLIENT_SECRET,
        scope = config.GMAIL_AUTH_SCOPE,
        redirect_uri = url_for('login_callback', _external = True))
    return auth_flow

def user_setup():
    """Once user is logged-in, this is called to query user's emails and seed db for flights found."""
    #Check if user already has emails & flights in db
    db_user_emails = Email.query.filter(Email.user_id == current_user.id).first()
    db_user_flights = Flight.query.filter(Flight.user_id == current_user.id).first()

    #If so, do not query Gmail API anew - currently this is only good for demo feature, allows for future option of returning users
    if db_user_emails and db_user_flights:
        return None
    
    #Query Gmail API
    else:
        query_result = gmailapiworks.populate_db(g.gmail_api, current_user.id)
        if query_result == "Successfully added emails and flights to the db":
            print query_result
        else:
            print query_result
            return "Error"

@login_manager.user_loader
def load_user(userid):
    return User.query.get(int(userid))

@app.before_request
def before_request():
    g.carbon_price = 37.00 #Official White House SCC as of Nov 2014

    if current_user.is_authenticated() and current_user.id > 0:
        credentials = AccessTokenCredentials(current_user.access_token, u'')
        g.gmail_api = get_api(credentials)

    #Set display in base.html depending on user status
    if flask_session.get('user_id') == None:
        g.status = "Log In"
        g.link = "/login/"
    else:
        g.status = current_user.email
        g.link = "/logout/"

@app.route("/")
def homepage():
    return render_template("base.html")

@app.route("/get_flights", methods=["GET"])
def get_all_flights():
    """Main Homepage: Calls user_setup() and if that returns with found flight emails, produces total summary results report for each year flight emails were found."""
    #Return page explaining what to do in case no matching emails were found
    if user_setup() == "Error":
        return render_template("/noemails.html")
    
    #Return main summary report page
    else:
        #Query email results list from gmail query
        emails_in_db = Email.query.filter(Email.user_id == current_user.id).order_by(asc(Email.date)).all()

        #Stats for email query results list to pass into page
        num_emails = len(list(emails_in_db))
        first_year = emails_in_db[0].date.year
        last_year = emails_in_db[-1].date.year

        #Summary results list for the year, number of flights, and total CO2e to pass into page
        years_list = seed_flights.report_by_year(current_user.id)

        return render_template("/getflights.html", num_emails=num_emails, first_year=first_year, last_year=last_year, years_list=years_list)

@app.route("/get_flights/<year>")
def get_flights_by_year(year):
    """When certain year is selected from get_flights, returns year-specific summary report with flight legs and emissions"""
    year = int(year)
    results_list = []
    user_flights = Flight.query.filter(Flight.user_id == current_user.id).order_by(Flight.date.asc(), Flight.id.asc()).all()
    
    #Ensure returned flights related to year selected (can't query by year only)
    working_list = [obj for obj in user_flights if (obj.date.year == year)]

    #Create summary report stats for this year
    for flight in working_list:
        date = flight.date.strftime('%b-%d')
        depart = "%s (%s)" %(flight.departure.city, flight.depart)
        arrive = "%s (%s)" %(flight.arrival.city, flight.arrive)
        CO2e = seed_flights.calc_carbon((flight.departure.latitude, flight.departure.longitude), (flight.arrival.latitude, flight.arrival.longitude))

        results_list.append((flight.id, date, depart, arrive, CO2e))

    #Data to feed airport names into JavaScript drop-down add flights form
    airports_json = get_airports()

    return render_template("/yearflights.html", year=year, results_list=results_list, airports_json=airports_json)

@app.route("/delete_flight", methods=["POST"])
def delete_flight():
    """Receives ajax data for flight user clicked to delete, deletes flight and sends back 'ok' once completed. (Will post error message on other end if error.)"""
    id = int(request.values['id'])
    flight = Flight.query.filter(Flight.id == id, Flight.user_id == current_user.id).one()
    db_session.delete(flight)
    db_session.commit()
    return "OK"

@app.route("/add_flight", methods=["GET"])
def add_flight():
    """Receives user input for flight details (date, departure, arrival) and makes a new flight entry in the db for user"""
    date = request.args.get('purchase_date')
    depart = request.args.get('depart')
    arrive = request.args.get('arrive')
    
    airport_list = get_airports(format="python")
    #Will ask user to re-input cities if not sent in correct format, if in correct format, will add flight to db for user
    if (arrive in airport_list) and (depart in airport_list):
        user_id = flask_session.get('user_id')
        db_date = datetime.strptime(date, "%Y-%m-%d")
        #Find airport codes in input
        db_depart = re.search((r"([A-Z]{3})"),depart).group()
        db_arrive = re.search((r"([A-Z]{3})"),arrive).group()
        #Adding to db, special email_id code of "0" used to indicate manual user added flight
        entry = Flight(user_id=user_id, email_id=0, date=db_date, depart=db_depart, arrive=db_arrive)
        db_session.add(entry)
        db_session.commit()
        
        #Return info for table addition
        date = db_date.strftime('%b-%d')
        d_airport = Airport.query.filter_by(id = db_depart).one()
        a_airport = Airport.query.filter_by(id = db_arrive).one()
        CO2e = seed_flights.calc_carbon((d_airport.latitude, d_airport.longitude), (a_airport.latitude, a_airport.longitude))
        price = CO2e * g.carbon_price 

        return jsonify(date=date,
            depart=depart,
            arrive=arrive,
            CO2e=CO2e,
            price=price,
            id=entry.id)

    else:
        return "Error"

@app.route("/about_calc")
def about_calc():
    """Renders a methods explanation page"""
    return render_template("carboncalcs.html")

@app.route("/donate")
def donate_page():
    """Directs user with their personal carbon debt to donation page"""
    debt = request.args.get('carbon_debt')
    return render_template("donate.html", debt=debt)

@app.route("/flights.js")
def flights4map():
    """Queries db for all flights and turns into a json for mapbox animation"""
    total_flights = Flight.query.filter(Flight.user_id == current_user.id).all()

    if total_flights != None:
        map_list = []

        for flight in total_flights:
            lat_D = flight.departure.latitude
            long_D = flight.departure.longitude
            lat_A = flight.arrival.latitude
            long_A = flight.arrival.longitude
            
            map_list.append([[lat_D,long_D],[lat_A,long_A]])

        str_coords = json.dumps(map_list)
        return str_coords

    else:
        return

@app.route("/airports.js")
def get_airports(format="json"):
    """Queries db for airport info and turns code and city pairs in json (default) for user flight adding info. If any other argument passed (eg. 'python') will return python list object."""
    airports = Airport.query.order_by(asc(Airport.city)).all()
    airport_list = []

    for obj in airports:
        air_str = '%s (%s)' %(obj.city, obj.id)
        airport_list.append(air_str)

    if format == "json":
        str_airports = json.dumps(airport_list)
        return str_airports

    else:
        return airport_list

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
    auth_flow = get_auth_flow()
    credentials = auth_flow.step2_exchange(code)
    gmail_api = get_api(credentials)
    print "gmail api accessed, getting user profile..."
    gmail_user = gmail_api.users().getProfile(userId = 'me').execute()
    email = gmail_user['emailAddress']
    access_token = credentials.access_token
    print "got user, adding access token to db..."

    user = User.query.filter_by(email = email).first()
    if user:
        user.access_token = access_token
        db_session.commit()

    else:
        user = User(email=email, access_token=access_token)
        user.save()
    
    login_user(user, remember = True)
    print "user logged in, querying gmail messages..."

    return redirect(url_for('homepage'))

@app.route('/logout/')
def logout():
    # Complete reset, not disabling demo data
    if current_user.id > 0:
        Flight.query.filter(Flight.user_id == current_user.id).delete()
        Email.query.filter(Email.user_id == current_user.id).delete()
        User.query.filter(User.id == current_user.id).delete() 
        db_session.commit()

    logout_user()

    return redirect(url_for('homepage'))

@app.route("/demo", methods=["POST"])
def demo_site():
    user = User.query.filter_by(id = 0).one()
    login_user(user, remember = True)
    return redirect(url_for('homepage'))

if __name__ == "__main__":
    app.run(debug = True)


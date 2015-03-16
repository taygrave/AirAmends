

# Incomplete route for airamends.py
@app.route("/new_flights", methods=["POST"])
def new_flights():
    """Allows user to query their gmail from only the point of their most recent email forward, adds those emails and flights to db"""
    # Need something here to ensure access token is valid otherwise will throw oauth2client.client.AccessTokenCredentialsError
    newest_flight = Flight.query.order_by(desc(Flight.date)).limit(1).all()
    recent_date = (newest_flight[0].date).strftime('%Y/%m/%d')
    new_query = gmailapiworks.query + " after:" + recent_date

    gmailapiworks.add_msgs_to_db(g.gmail_api, current_user.id, new_query)

    # INCOMPLETE!!
    #TODO - have seed_flights algorithm run on new emails only, add those flights to the db

    return redirect(url_for('getflights'))

""" Accompanying html for getflights.html to re-query gmail:
<form action="/new_flights" method="POST">
    <button class="btn btn-lg btn-success" type="submit">Query for New Emails Only</button>
</form>
"""

#This used to live in seed_flights when I needed to examine email bodies once they were decoded
def print_to_file():
    """Queries the database for the body of the messages and prints out content into txt files so we can examine them ourselves """
    s = model.connect()
    msg_list = s.query(model.Email).all()

    for msg in msg_list:
        body = msg.body.encode('utf-8')
        filename = "body/" + str(msg.id) + ".txt"
        f = open(filename, 'w')
        print >> f, body
        f.close

#From airamends.py, features that weren't used for final app as of now
## Deprecated: need to be updated to query only for current user if going to use
# @app.route("/flight_reset", methods=["POST"])
# def reset_flights():
#     Flight.query.delete()
#     session.commit()
#     return redirect(url_for('getflights'))

# @app.route("/complete_reset", methods=["POST"])
# def complete_reset():
#     Email.query.delete()
#     Flight.query.delete()
#     session.commit()
#     return redirect(url_for('getflights'))
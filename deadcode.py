

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
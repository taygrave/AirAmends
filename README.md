# AIRAMENDS
######Final Project for Hackbright 2015

AIRAMENDS is a forward-thinking web app that gives air travelers visibility into their carbon footprint. After linking their gmail, an interactive report details the user's personal air travel over the last few years and the associated social cost of the carbon emissions estimated from each flight. The user is also presented with an personal map animating their flights and is given an option to donate away their personal carbon debt to the environmental organization of their choicee.

![Alt text](https://raw.githubusercontent.com/taygrave/AirAmends/3af35167221924019ffbd439f2eb3624c807cbf5/static/ScreenShot.png "Screen Shot")

##Tech Stack
Application Layer: Python, Flask, Regular Expressions

Data Layer: SQLite, SQLAlchemy

APIs: Google OAuth, Gmail, MapBox

Presentation Layer: HTML, CSS, JS, jQuery, AJAX, JSON, and Bootstrap

######Learn more about the developer: www.linkedin.com/in/thesselgrave

##Installation Instrcutions

Clone or fork this repository. Then open a command line interface (terminal, shell, etc.) and type:

`pip install -r requirements.txt`

####Add your API Keys

To run AIRAMENDS, you will need to create your own Google Developer account in order to request the necessary access keys.

#####1. Google OAuth 2.0 credentials
Create a Google Developer account and take note of where to find your Client ID and Client Secret for web applications in the developer console: https://developers.google.com/accounts/docs/OAuth2

#####2. Configure the web app in your Google Developer Console
Edit the web applications section to set the redirect URI to: http://localhost:5000/login/callback/

#####3. Turn on Google's web services
In your Google Developer Console, turn the Gmail API service to "on".

#####4. Create a Flask Secret Key
In order to use sessions in Flask, you will need a secret key. The Flask Sessions documentation shows you how to generate one: http://flask.pocoo.org/docs/quickstart/#sessions

#####5. Store your Secret Keys
My keys are stored in my ~/.bash_profile and pointed to in config.py. You should not need to change config.py, but your .bash_profile should look something like this:

```
## For Google OAuth
export GOOGLE_ID=<put your CLIENT ID here, no quotes>
export GOOGLE_SECRET=<your CLIENT SECRET here, no quotes>

## For Flask Sessions
export SECRET_KEY="your key in quotes"
```

##Run the App

In the AirAmends directory, type this command to start the server:
`python airamends.py`
Open a web browser and navigate to: http://localhost:5050

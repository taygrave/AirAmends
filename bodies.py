import model
from bs4 import BeautifulSoup

s = model.connect()


#get a list of the email objects
msg_list = s.query(model.Email).all()
fnum = 0

for msg in msg_list:
    body = msg.body
    soup = BeautifulSoup(body)
    passenger = soup.find('name')
    date = soup.find('traveldate')
    depart = soup.find('depart')
    arrive = soup.find('arrive')

    print msg.id, passenger, date, depart, arrive
    print '*' * 10


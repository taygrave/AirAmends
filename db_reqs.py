import model, csv
from datetime import datetime

#list of all three letter North American time zone abbreviations and other proven problematic three capital character email instances that do not mean to indicate an airport
list_of_conflict_codes = ['ADT', 'AST', 'CDT', 'CST', 'EDT', 'EGT', 'EST', 'GMT', 'MDT', 'MST', 'NDT', 'NST', 'PDT', 'PST', 'WGT', 'UTC', 'TLS', 'HEL']

def first_db_setup(db_session):
    """Upon the very first intialization of the db, seeds in all necessary airport codes and demo data for base user functionality"""
    seed_airports(db_session)
    seed_demo_data(db_session)

def seed_airports(db_session):
    """Parses the airports.dat file of airport codes and associated information to add 5,000+ airports and their associated information to the db, takes the live db_session connection as a parameter"""
    #source airport data from http://openflights.org/data.html
    with open("data/airports.dat", 'rb') as src_file:
        reader = csv.reader(src_file)

        for col in reader:
            code_to_check = col[4]
            #determines if there are numbers in the aiport code
            numbers_in_code = has_numbers(code_to_check)
            
            #determined to be a legit airport code and saved to db if code_to_check has 3 characters and numberless, as there are codes in the source data that do not meet this requirement
            if len(code_to_check)==3 and numbers_in_code == False:
                #code found legit, set up for saving to db
                id = col[4]
                #Translating some airport names and cities into strict unicode to avoid errors
                name = col[1].decode('utf-8')
                city = col[2].decode('utf-8')
                country = col[3]
                lati = col[6]
                longi = col[7]
                #there is also a timezone attribute to each row that could serve as a regional indicator if need be
                
                entry = model.Airport(name=name, city=city, country=country, latitude=lati, longitude=longi)
                #overwriting auto-increment default to have id be three letter airport code itself
                entry.id = id
                db_session.add(entry)

        db_session.commit()
    
    #A quick fix that removes any airport added to the database that happens to have the same three letter code as a timezone or other email-related codes that do not actually indicate airports when they appear in email messages. 
    #Without this fix, the flight parser will mistakenly view the timezone, for example, as a flight segment.
    #Needs improvement in a more comprehensive version of this app  
    remove_code_conflicts(db_session)

def has_numbers(input_str):
    """Takes a string and returns true if that string has a number in it"""
    return any(char.isdigit() for char in input_str)

def remove_code_conflicts(db_session, list_of_conflict_codes=list_of_conflict_codes):
    """Removes any airport from db that has the same three letter code as a North American time zone or other coincidental offense"""
    
    for code in list_of_conflict_codes:
        conflict = db_session.query(model.Airport).filter(model.Airport.id == code).first()
        if conflict != None:
            db_session.delete(conflict)

    db_session.commit()

def seed_demo_data(db_session):
    """Inserts demo data into newly created db so that users can demo site functionality w/o having to provide their own gmail authorization"""
    with open("data/demouser.csv", 'rb') as src_file1:
        reader1 = csv.reader(src_file1)

        for col in reader1:
            email = col[1]
            token = col[2]

            user = model.User(email=email, access_token=token)
            user.id = 0
            db_session.add(user)

    with open("data/demoemails.csv", 'rb') as src_file2:
        reader2 = csv.reader(src_file2)

        for col in reader2:
            user_id = col[1]
            msg_id = col[2]
            date = col[3]
            sender = col[4]
            subject = col[5]

            converted_date = datetime.strptime(date, "%Y-%m-%d")

            email = model.Email(user_id=user_id, msg_id=msg_id, date=converted_date, sender=sender, subject=subject)
            db_session.add(email)

    with open("data/demoflights.csv", 'rb') as src_file3:
        reader3 = csv.reader(src_file3)

        for col in reader3:
            user_id = col[1]
            email_id = col[2]
            date = col[3]
            depart = col[4]
            arrive = col[5]

            converted_date = datetime.strptime(date, "%Y-%m-%d")

            flight = model.Flight(user_id=user_id, email_id=email_id, date=converted_date, depart=depart, arrive=arrive)
            db_session.add(flight)

    db_session.commit()
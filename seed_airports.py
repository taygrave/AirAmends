import model
import csv 

def load_airports(session):
    """Parses the airports.dat file of airport codes and associated information to add to the db, taking the live session connection as a parameter"""
    with open("data/airports.dat", 'rb') as src_file:
        reader = csv.reader(src_file)

        for row in reader:
            check = row[4]
            #determines if there are numbers in the aiport code
            numberless = has_numbers(check)
            
            #only saving entries with full, numberless airport codes into the db, there are more entries that do not meet this requirement
            if len(check)==3 and numberless == False:
                id = row[4]
                #Translating some airport names and cities into strict unicode to avoid errors
                name = row[1].decode('utf-8')
                city = row[2].decode('utf-8')
                country = row[3]
                lati = row[6]
                longi = row[7]
                #there is also a timezone attribute to each row that could serve as a regional indicator if need be
                
                entry = model.Airport(name=name, city=city, country=country, latitude=lati, longitude=longi)
                entry.id = id

                session.add(entry)

        session.commit()
        print "Successfully added airports to db."
            

def has_numbers(input_str):
    """Takes a string and returns true if that string has a number in it"""
    return any(char.isdigit() for char in input_str)

s = model.connect()
load_airports(s)

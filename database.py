#!/usr/bin/env python3

from modules import pg8000
import configparser


# Define some useful variables
ERROR_CODE = 55929

#####################################################
##  Database Connect
#####################################################

def database_connect():
    # Read the config file
    config = configparser.ConfigParser()
    config.read('config.ini')

    # Create a connection to the database
    connection = None
    try:
        connection = pg8000.connect(database=config['DATABASE']['user'],
            user=config['DATABASE']['user'],
            password=config['DATABASE']['password'],
            host=config['DATABASE']['host'])
    except pg8000.OperationalError as e:
        print("""Error, you haven't updated your config.ini or you have a bad
        connection, please try again. (Update your files first, then check
        internet connection) 
        """)
        print(e)
    #return the connection to use
    return connection

#####################################################
##  Login
#####################################################

def check_login(email, password):
    # checks if user details are correct
    conn = database_connect()   # connect database and configurate cursor
    if(conn is None):
        return ERROR_CODE
    cur = conn.cursor()
    try:
        # try getting information returned from query
        check = """SELECT *
                   FROM CarSharing.Member
                   WHERE email=%s AND password=%s"""
        cur.execute(check, (email, password))
        val = cur.fetchone()
        cur.close()             # close the cursor
        conn.close()            # close the connection to db
        return val
    except:
        # if any error, print error message and return a NULL row
        print("Error. Please check your login details.")
    cur.close()                 # close the cursor
    cur.close()                 # close the connection to db
    return None


#####################################################
##  Homebay
#####################################################
def update_homebay(email, bayname):
    # updates the user's homebay
    conn = database_connect()   # connect database and configurate cursor
    if(conn is None):
        return ERROR_CODE
    cur = conn.cursor()
    try:
        # try getting information returned from query
        update = """UPDATE Member
                    SET homeBay = %s
                    WHERE Member.email = %s
                        AND EXISTS(SELECT name
                                   FROM CarBay
                                   WHERE name = %s)"""
        cur.execute(update, (bayname, email, bayname))
        val = cur.fetchone()
    except:
        # if any error, print error message and return a NULL row
        print("Error with the Database.")
    cur.close()             # close the cursor
    conn.close()            # close the connection to db
    return True
    

#####################################################
##  Booking (make, get all, get details)
#####################################################

def make_booking(email, car_rego, date, hour, duration):
    # TODO
    # Insert a new booking
    # Make sure to check for:
    #       - If the member already has booked at that time
    #       - If there is another booking that overlaps
    #       - Etc.
    # return False if booking was unsuccessful :)
    # We want to make sure we check this thoroughly
    return True


def get_all_bookings(email):
    # Get all the bookings made by this member's email
    conn = database_connect()   # connect database and configurate cursor
    if(conn is None):
        return ERROR_CODE
    cur = conn.cursor()
    val = None
    try:
        # try getting information returned from query
        bookings = """SELECT car as CarRegistration, name as CarName,                                        
                        DATE(starttime) as Date, starttime::time as Time
                      FROM CarSharing.Booking JOIN CarSharing.Member ON (memberNo = madeBy)
                        JOIN CarSharing.Car ON (car = regno)
                      WHERE email=%s
                      ORDER BY whenBooked DESC;
                    """
        cur.execute(bookings, (email,))
        val = cur.fetchall()
    except:
        # if any error, print error message and return a NULL row
        print("Error with the Database.")
    cur.close()             # close the cursor
    conn.close()            # close the connection to db
    return val 


def get_booking(b_date, b_hour, car):
    # Get the information about a certain booking that has specified date, hour, and car
    conn = database_connect()   # connect database and configurate cursor
    if(conn is None):
        return ERROR_CODE
    cur = conn.cursor()
    val = None
    try:
        # try getting information returned from query
        booking = """SELECT Member.nickname as MemberName, Car.regno as CarRegistration,
                        Car.name as CarName, DATE(starttime) as Date, date_part('hour', starttime) as Time,
                        date_part('hour', (endtime - starttime)) as Duration,
                        DATE(whenBooked) as WhenBooked, CarBay.name as CarBay 
                     FROM CarSharing.Booking JOIN CarSharing.Member ON (memberNo = madeBy)
                        JOIN CarSharing.Car ON (car = regno)
                        JOIN CarSharing.CarBay ON (parkedAt = bayID)
                     WHERE DATE(starttime)=%s AND date_part('hour', starttime)=%s AND Car.regno=%s
                     ORDER BY whenBooked DESC;"""
        cur.execute(booking, (b_date, b_hour, car))
        val = cur.fetchone()
    except:
        # if any error, print error message and return a NULL row
        print("Error with the Database.")  
    cur.close()             # close the cursor
    conn.close()            # close the connection to db
    return val 


#####################################################
##  Car (Details and List)
#####################################################

def get_car_details(regno):
    # val = ['66XY99', 'Ice the Cube','Nissan', 'Cube', '2007', 'auto', 'Luxury', '5', 'SIT', '8', 'http://example.com']
    # Get details of the car with this registration number
    # Return the data (NOTE: look at the information, requires more than a simple select. NOTE ALSO: ordering of columns)
    conn = database_connect()   # connect database and configurate cursor
    if(conn is None):
        return ERROR_CODE
    cur = conn.cursor()
    val = None
    try:
        cardetails = """SELECT regno, Car.name, make, model, year, transmission,
                        category, capacity, CarBay.name, walkscore, mapURL
                        FROM CarSharing.Car
                            JOIN CarSharing.CarModel ON (Car.model=CarModel.model AND Car.make=CarModel.make)
                            JOIN CarSharing.CarBay ON (Car.parkedAt=CarBay.bayID)
                        WHERE Car.regno = %s;"""
        cur.execute(cardetails, (regno,))
        val = cur.fetchone()
    except:
        # if any error, print error message and return a NULL row
        print("Error with the Database.")
    cur.close()
    conn.close()
    return val

def get_all_cars():
    #val = [ ['66XY99', 'Ice the Cube', 'Nissan', 'Cube', '2007', 'auto'], ['WR3KD', 'Bob the SmartCar', 'Smart', 'Fortwo', '2015', 'auto']]
    # Get all cars that PeerCar has
    # Return the results
    conn = database_connect()   # connect database and configurate cursor
    if(conn is None):
        return ERROR_CODE
    cur = conn.cursor()
    val = None
    try:
        cars = """SELECT regno, name, make, model, year, transmission
                  FROM CarSharing.Car"""
        cur.execute(cars)
        val = cur.fetchall()
    except:
        # if any error, print error message and return a NULL row
        print("Error with the Database.")
    cur.close()
    conn.close()
    return val


#####################################################
##  Bay (detail, list, finding cars inside bay)
#####################################################

def get_all_bays():
    # Get all the bays that PeerCar has :)
    # And the number of cars
    conn = database_connect()   # connect database and configurate cursor
    if(conn is None):
        return ERROR_CODE
    cur = conn.cursor() 
    val = None

    try:
        bays = """SELECT name, address, bayID
                  FROM CarSharing.CarBay
                  ORDER BY name"""
        cur.execute(bays)
        val = cur.fetchall()
    except:
        # if any error, print error message and return a NULL row
        print("Error with the Database.")
    cur.close()
    conn.close()
    return val


def get_bay(name):
    # Get the information about the bay with this unique name
    # Make sure you're checking ordering ;)
    conn = database_connect()   # connect database and configurate cursor
    if(conn is None):
        return ERROR_CODE
    cur = conn.cursor()
    val = None

    try:
        bay = """SELECT name, description, address, gps_long, gps_lat
                 FROM CarSharing.CarBay
                 WHERE name = %s
                 """
        cur.execute(bay, (name,))
        val = cur.fetchone()
    except:
        # if any error, print error message and return a NULL row
        print("Error with the Database.")
    cur.close()
    conn.close()
    return val

def search_bays(search_term):
    # Select the bays that match (or are similar) to the search term
    conn = database_connect()   # connect database and configurate cursor
    if(conn is None):
        return ERROR_CODE 
    cur = conn.cursor()
    val = None
    try:
        # try getting information returned from query
        bays = """SELECT *
                  FROM CarSharing.CarBay  
                  WHERE LOWER(address) LIKE %s OR LOWER(name) LIKE %s;""" # compare search term with address or name
        search_term = '%' + search_term + '%'
        cur.execute(bays, (search_term, search_term))
        val = cur.fetchall()
    except:
        # if any error, print error message and return a NULL row
        print("Error with the Database.")
    cur.close()             # close the cursor
    conn.close()            # close the connection to db
    if(val is None):
        val = []
    return val 

def get_cars_in_bay(bay_name):
    # Get the cars inside the bay with specified bay name and return regno and name
    conn = database_connect()   # connect database and configurate cursor
    if(conn is None):
        return ERROR_CODE
    cur = conn.cursor()
    val = None
    try:
        carsInBay = """SELECT c.regno, c.name
                       FROM CarSharing.Car c JOIN CarSharing.CarBay ON (parkedAt = bayID)
                       WHERE CarBay.name = %s
                       ORDER BY c.name"""
        cur.execute(carsInBay, (bay_name,))
        val = cur.fetchall()
    except:
        # if any error, print error message and return a NULL row
        print("Error with the Database.")
    cur.close()
    conn.close()
    return val

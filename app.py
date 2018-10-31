from flask import Flask, request, abort, jsonify, Response, make_response, redirect
from math import floor
import json
import sqlite3
import validators

## helper functions
def check_auth_header():
    username, password = request.authorization.get('username', None), request.authorization.get('password', None)
    if not username or not password:
        return False, "Unable to authenticate user. Set auth header as TEST if you are in test mode."
    if username != "urlshortener" or password != "urlshortener":
        return False, "Invalid authentication header"
    return True, "Successfully authenticated"

def response_error(message, error=None, error_code=None):
    response = json.dumps({'status': 'fail', 'message': message, 'error': error, 'error_code': error_code})
    return make_response(response, 400)

def auth_error(message, error=None, error_code=None):
    response = json.dumps({'status': 'fail', 'message': message, 'error': error, 'error_code': error_code})
    return make_response(response, 401)

def response_ok(data):
    response = jsonify({'status': 'success', 'data': data}, 200)
    return make_response(response)



app = Flask(__name__)



## base64 encoder logic

base = '0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ' # base string to be used in base62 encoding

def convert_to_base62(number, b = 62):
    if b <= 0 or b > 62:
        return 0
    print (number)
    r = number % b
    res = base[r]
    q = floor(number/b)
    while q:
        r = q % b
        q = floor(q / b)
        res = base[int(r)] + res  
    return res


## database logic

# create table
if app.config['TESTING'] == True:
    database_name = app.config['DB_NAME']
else:
    database_name = "url_store.db"
def create_database(db_name):

    create_table = """
            CREATE TABLE URLS (
            ID INTEGER PRIMARY KEY AUTOINCREMENT,
            URL TEXT NOT NULL,
            SHORT_NAME TEXT,
            IP_ADDRESS CHARS(50),
            DEVICE_TYPE TEXT ,
            VISITS INT
            );
            """
    with sqlite3.connect(db_name) as conn:
        cursor = conn.cursor()
        try:
            cursor.execute(create_table)
            print(app.config['TESTING'])
            print(db_name)
            

            
        except sqlite3.Error as e:
            print(e)

## API logic
@app.route('/', methods=['POST'])
def encode_url():
    
    validate_auth_header = check_auth_header()
    if not validate_auth_header[0]:
       return auth_error(validate_auth_header[1],error= validate_auth_header[1], error_code=401)
    
    # create_database("url_store")
    data = json.loads(request.data)
    if "url" not in data.keys():
        return response_error("Please enter a URL",error="No URL given", error_code=400)
    
    url = data['url']
        
    if 'suggested_short_name' in data.keys():
        suggested_short_name = data['suggested_short_name']
    else:
        suggested_short_name = None
    
    if validators.url(url):
        with sqlite3.connect(database_name) as conn:
            cursor = conn.cursor()
            short_name = None
            try:
                res = cursor.execute(
                "INSERT INTO URLS (URL,VISITS) VALUES (?,?);",
                [url,0]
                )
                url_id = res.lastrowid
                if not(suggested_short_name == None):
                    cursor.execute(
                        "SELECT URL FROM URLS WHERE SHORT_NAME=?;",
                        [suggested_short_name]
                    )                       
                    result = cursor.fetchone()
                    if result == None:
                        cursor.execute(
                            " UPDATE URLS SET SHORT_NAME = (?) WHERE ID = (?) ;", [suggested_short_name, url_id]
                    )
                    else:
                        short_name = convert_to_base62(url_id)
                        cursor.execute(
                        " UPDATE URLS SET SHORT_NAME = (?) WHERE ID = (?) ;", [short_name, url_id]
                        )
                else:
                    print (url_id)
                    short_name = convert_to_base62(url_id)
                    print (short_name)
                    cursor.execute(
                        " UPDATE URLS SET SHORT_NAME = (?) WHERE ID = (?) ;", [short_name, url_id]
                    )
                             
            except sqlite3.Error as e:
                print (e)
            if suggested_short_name is not None:
                short_name = suggested_short_name  
            data = {"short_url":"http://0.0.0.0:5000/{}".format(short_name),"auth_status":validate_auth_header}
            return response_ok(data)
    else:
        print("TEST_FAILED")
        return response_error("Please enter a valid URL!",error="Invalid URL", error_code=400)

@app.route('/<short_name>')
def redirect_short_name(short_name):
    url_redirect = None
    validate_auth_header = check_auth_header()
    if not validate_auth_header[0]:
       return validate_auth_header[1]
    
    # decoded = convert_to_base10(short_name)
    with sqlite3.connect(database_name) as conn:
        cursor = conn.cursor()
        res = cursor.execute('SELECT URL, VISITS FROM URLS WHERE SHORT_NAME=?', [short_name])   
        try:
            short = res.fetchone()
            if short is not None:
                url_redirect = short[0]
                visits = short[1]
                visits +=1
                cursor.execute(
                "UPDATE URLS SET IP_ADDRESS = (?), DEVICE_TYPE = (?), VISITS  = (?) WHERE SHORT_NAME = (?);", 
                [request.remote_addr, request.user_agent.string,visits, short_name]
                    )
        except Exception as e:
            print(e)
    return redirect(url_redirect)

if __name__ == '__main__':
    pass
    # app.run(debug=False)
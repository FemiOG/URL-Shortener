from flask import Flask, request, abort, jsonify, Response, make_response, redirect
from math import floor
import json
import sqlite3
import validators

def response_error(message, error=None, error_code=None):
    response = json.dumps({'status': 'fail', 'message': message, 'error': error, 'error_code': error_code})
    return make_response(response, 400)

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
def create_database():
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
    with sqlite3.connect('url_store.db') as conn:
        cursor = conn.cursor()
        try:
            print ("success")
            cursor.execute(create_table)
            
        except sqlite3.Error as e:
            print(e)


## API logic
@app.route('/', methods=['POST'])
def encode_url():
    create_database()
    url = request.form.get('url')
    suggested_short_name = request.form.get('suggested_short_name')
    print (validators.url(url))

    if validators.url(url):
        with sqlite3.connect('url_store.db') as conn:
            cursor = conn.cursor()
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
                        short_name = suggested_short_name
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
            
            return (jsonify({"short_url":"http://127.0.0.1:5000/{}".format(short_name)}))
    else:
        return response_error("Please enter a valid URL!",error="Invalid URL", error_code=400)

@app.route('/<short_name>')
def redirect_short_name(short_name):
    # decoded = convert_to_base10(short_name)
    with sqlite3.connect('url_store.db') as conn:
        cursor = conn.cursor()
        res = cursor.execute('SELECT URL, VISITS FROM URLS WHERE SHORT_NAME=?', [short_name])   
        try:
            short = res.fetchone()
            if short is not None:
                print(short)
                url = short[0]
                visits = short[1]
                print (visits)
                visits +=1
                cursor.execute(
                "UPDATE URLS SET IP_ADDRESS = (?), DEVICE_TYPE = (?), VISITS  = (?) WHERE SHORT_NAME = (?);", 
                [request.remote_addr, request.user_agent.string,visits, short_name]
                    )
                print (url)
        except Exception as e:
            print(e)
    return redirect(url)




    
    







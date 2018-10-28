from flask import Flask, request, abort, jsonify, Response, make_response
from math import floor
import sqlite3

app = Flask(__name__)


## base64 encoder-decoder logic

base = '0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ' # base string to be used in base62 encoding

def convert_to_base62(number, b = 62):
    if b <= 0 or b > 62:
        return 0

    r = number % b
    res = base[r]
    q = floor(number/b)

    while q:
        r = q % b
        q = floor(q / b)
        res = base[int(r)] + res
    
    return res

def convert_to_base10(number, b = 62):
    limit = len(number)
    res = 0

    for i in range(limit):
        res = b * res + base.find(number[i])
    
    return res

## database logic

# create table
create_table = """
        CREATE TABLE URLS(
        ID INT PRIMARY KEY ,
        URL TEXT NOT NULL
        );
        """

with sqlite3.connect('url_store.db') as conn:
    cursor = conn.cursor()
    try:
        cursor.execute(create_table)
    except sqlite3.Error as e:
        print(e)
    
            








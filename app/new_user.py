import argparse
import os
import psycopg2
import hashlib

DATABASE_URL = os.environ['DATABASE_URL']
conn = psycopg2.connect(DATABASE_URL, sslmode='require')
cursor = conn.cursor()

parser = argparse.ArgumentParser()
parser.add_argument('--username', required=True)
parser.add_argument('--password', required=True)
args = parser.parse_args()

username = args.username
password = args.password

hsh = hashlib.sha256(password.encode('utf-8')).hexdigest()

q = "INSERT INTO users VALUES(%s, %s)"
cursor.execute(q, (username, hsh))
conn.commit()
conn.close()

print("success")
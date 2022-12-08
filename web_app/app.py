# importing modules
from flask import Flask, render_template, request
from pymysql import connections
import os
import random
import argparse
import boto3

app = Flask(__name__)

DBHOST = os.environ.get("DBHOST") or "localhost"
DBUSER = os.environ.get("DBUSER") or "root"
DBPWD = os.environ.get("DBPWD") or "password"
DATABASE = os.environ.get("DATABASE") or "employees"
DBPORT = int(os.environ.get("DBPORT"))
BACK_ENV = os.environ.get("APP_bg") or "set1"
AWS_ACCESS_KEY=os.environ.get("AWS_ACCESS_KEY")
AWS_SECRET_KEY=os.environ.get("AWS_SECRET_KEY")
AWS_SESSION_TOKEN=os.environ.get("AWS_SESSION_TOKEN")


# Create a connection to the MySQL database
db_conn = connections.Connection(
    host= DBHOST,
    port=DBPORT,
    user= DBUSER,
    password= DBPWD, 
    db= DATABASE
)

s3 = boto3.client('s3',
aws_access_key_id = AWS_ACCESS_KEY, aws_secret_access_key= AWS_SECRET_KEY ,aws_session_token= AWS_SESSION_TOKEN ,region_name="us-east-1")

output = {}
table = 'employee';

# Define the supported color codes
bg_codes = {
    "set1": "https://background-storage.s3.amazonaws.com/download.jfif",
    "set2": "https://background-storage.s3.amazonaws.com/images+(1).jfif",
    "set3": "https://background-storage.s3.amazonaws.com/images+(2).jfif",
    "set4": "https://background-storage.s3.amazonaws.com/images.jfif",

}

# Create a string of supported colors
SUPPORTED_BG = ",".join(bg_codes.keys())

# Generate a random color
bg = random.choice(["set1", "set2", "set3", "set4"])


@app.route("/", methods=['GET', 'POST'])
def home():
    return render_template('addemp.html', background=bg_codes[bg])

@app.route("/about", methods=['GET','POST'])
def about():
    return render_template('about.html', background=bg_codes[bg])
    
@app.route("/addemp", methods=['POST'])
def AddEmp():
    emp_id = request.form['emp_id']
    first_name = request.form['first_name']
    last_name = request.form['last_name']
    primary_skill = request.form['primary_skill']
    location = request.form['location']

  
    insert_sql = "INSERT INTO employee VALUES (%s, %s, %s, %s, %s)"
    cursor = db_conn.cursor()

    try:
        
        cursor.execute(insert_sql,(emp_id, first_name, last_name, primary_skill, location))
        db_conn.commit()
        emp_name = "" + first_name + " " + last_name

    finally:
        cursor.close()

    print("all modification done...")
    return render_template('addempoutput.html', name=emp_name, background=bg_codes[bg])

@app.route("/getemp", methods=['GET', 'POST'])
def GetEmp():
    return render_template("getemp.html", background=bg_codes[bg])


@app.route("/fetchdata", methods=['GET','POST'])
def FetchData():
    emp_id = request.form['emp_id']

    output = {}
    select_sql = "SELECT emp_id, first_name, last_name, primary_skill, location from employee where emp_id=%s"
    cursor = db_conn.cursor()

    try:
        cursor.execute(select_sql,(emp_id))
        result = cursor.fetchone()
        
        # Add No Employee found form
        output["emp_id"] = result[0]
        output["first_name"] = result[1]
        output["last_name"] = result[2]
        output["primary_skills"] = result[3]
        output["location"] = result[4]
        
    except Exception as e:
        print(e)

    finally:
        cursor.close()

    return render_template("getempoutput.html", id=output["emp_id"], fname=output["first_name"],
                           lname=output["last_name"], interest=output["primary_skills"], location=output["location"], background=bg_codes[bg])

if __name__ == '__main__':
    
    # Check for Command Line Parameters for bg
    parser = argparse.ArgumentParser()
    parser.add_argument('--bg', required=False)
    args = parser.parse_args()

    if args.bg:
        print("bg from command line argument =" + args.bg)
        bg = args.bg
        if BACK_ENV:
            print("A bg was set through environment variable -" + BACK_ENV + ". However, bg from command line argument takes precendence.")
    elif BACK_ENV:
        print("No Command line argument. bg from environment variable =" + BACK_ENV)
        bg = BACK_ENV
    else:
        print("No command line argument or environment variable. Picking a Random bg =" + bg)

    # Check if input color is a supported one
    if bg not in bg_codes:
        print("bg not supported. Received '" + bg + "' expected one of " + SUPPORTED_BG)
        exit(1)

    app.run(host='0.0.0.0',port=81,debug=True)

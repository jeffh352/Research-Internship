import email
from flask import Flask, render_template, url_for, request, session, redirect, flash
import mysql.connector
import spacy

nlp=spacy.load("en_core_web_sm")
db=mysql.connector.connect(host="localhost", user="root", passwd="root", database="accounts")

mycursor=db.cursor()
app=Flask(__name__)
app.secret_key="super secret key"

@app.route('/', methods=['GET', 'POST'])
def login():
    ms=''
    if request.method=='POST':
        email=request.form.get('email')
        password=request.form.get('password')
        mycursor.execute("Select * FROM user WHERE email=%s AND password=%s", (email, password))
        record=mycursor.fetchone()
        if record:
            flash('Welcome!', category='success')
            session["email"]=record[1]
            return redirect(url_for ('home'))
        else:
            flash('Incorrect email/password. Please try again', category='error')
            
    return render_template("login.html", ms=ms)
  
@app.route('/sign_up', methods=['GET','POST'])
def sign_up():
    if request.method== 'POST':
        email=request.form.get('email')
        firstName=request.form.get('firstName')
        lastName=request.form.get('lastName')
        password=request.form.get('password')
        password2=request.form.get('password2')
        biography=request.form.get('biography')

        if len(email)<4:
            flash('Email must be longer than 4 characters', category='error')
        elif len(password)<7:
            flash('Password must be at least 7 characters', category='error')
        elif password!=password2:
            flash('Passwords do not match', category='error')
        elif len (biography)<1:
            flash('Please enter biography', category='error')
        else:
            mycursor.execute("INSERT INTO User(email, firstName, lastName, password, biography) VALUES (%s, %s, %s, %s, %s)", (email, firstName, lastName, password, biography))
            db.commit()
            flash("Account Created", category='success')
            return redirect(url_for ('login'))
    return render_template("sign_up.html")

@app.route("/home", methods=['GET', 'POST'])
def home():
    #email= session['email']
    #if request.method== 'POST':
    #    biography=request.form.get('biography')
    #    mycursor.execute("UPDATE User SET biography=%s WHERE email=%s", (biography, email))
    #    db.session.commit()
    return render_template('home.html', email= session['email'])

def show_ents(doc):
    if doc.ents:
        for ent in doc.ents:
            print(ent.text+' - ' +str(ent.start_char) +' - '+ str(ent.end_char) + ' - '+ent.label_+ ' - '+str(spacy.explain(ent.label_)))
    else:
        print("No named entities found.")
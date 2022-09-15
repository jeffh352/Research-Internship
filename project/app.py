import email
from pickle import NONE
import pickle
import string
from flask import Flask, render_template, url_for, request, session, redirect, flash
import mysql.connector
import spacy
from datetime import timedelta
from neo4j import GraphDatabase, basic_auth
import urllib.request, urllib.error, urllib.parse
import json
import os
from pprint import pprint

execute_commands=[]
#driver=GraphDatabase.driver(uri="bolt://localhost:7687/neo4j", auth=("neo4j", "1234"))
nlp=spacy.load("en_core_web_lg")
db=mysql.connector.connect(host="localhost", user="root", passwd="root", database="accounts")

REST_URL = "http://data.bioontology.org"
API_KEY = "e82ead30-cdb2-4455-a5cf-bf866935f094"
mycursor=db.cursor(buffered=True)
app=Flask(__name__)
app.secret_key="apikey"
app.permanent_session_lifetime=timedelta(minutes=30)

@app.route('/', methods=['GET', 'POST'])
def login():
    ms=''
    if request.method=='POST':
        session.permanent=True
        email=request.form.get('email')
        password=request.form.get('password')
        mycursor.execute("Select * FROM user WHERE email=%s AND password=%s", (email, password))
        record=mycursor.fetchone()
        if record:
            flash('Welcome!', category='success')
            session['biography']=record[5]
            session["firstName"]=record[1]
            session['email']=record[0]
            session["sessionID"]=record[4]
            return redirect(url_for ('home'))
        else:
            flash('Incorrect email/password. Please try again', category='error')
    else:
        if "email" in session:
            return redirect(url_for("home"))
    return render_template("login.html", ms=ms)
  
@app.route('/logout', methods=['GET', 'POST'])
def logout():
    session.pop('email', NONE)
    return render_template("login.html")

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
    if "email" in session:
        biography=session['biography']
        name=session['firstName']
        sessionID=session['sessionID']
        return render_template('home.html', firstName= session['firstName'], name=name)
    else:
        return redirect(url_for("login"))

@app.route("/spacyBio", methods=['GET', 'POST'])
def spacyBio():
    biography=session['biography']
    name=session['firstName']
    sessionID=session['sessionID']
    doc1=nlp(biography)
    ents=show_ents(doc1)
    mycursor.execute("INSERT INTO profile(userID, profile_info) VALUES (%s, %s)", (sessionID,) + (ents,))
    db.commit()
    return render_template('spacyBio.html', firstName= session['firstName'], name=name, biography=biography, ents=ents)

@app.route("/similarityCheck", methods=['GET', 'POST'])
def similarityCheck():
    name=session['firstName']
    similarAccounts=similarityChecker()
    return render_template('similarityCheck.html', name=name, dic=similarAccounts)

@app.route("/question", methods=['GET', 'POST'])
def question():
    questions=["Which Ontology should I use?", "What is the suitable ontology vocabulary?", "Does this Ontology best describe this terminology?"]
    if request.method== 'POST':
        sessionID=session['sessionID']
        question=request.form.get("ques")
        explanation=request.form.get("explanation")
        mycursor.execute("INSERT INTO post(user_id, question, explanation) VALUES (%s, %s, %s)", (sessionID,)+ (question,) + (explanation,))
        db.commit()
    return render_template('question.html', questions=questions)

@app.route("/forums", methods=['GET', 'POST'])
def forums():
    posts=forumPosts()
    return render_template('forums.html', post=posts)

@app.route("/response", methods=['GET', 'POST'])
def response():
    return render_template('response.html')

@app.route("/annotator?text", methods=['GET', 'POST'])
def annotator():
    #text_to_annotate = "Melanoma is a malignant tumor of melanocytes which are found predominantly in skin but also in the bowel and the eye."
    #annotations = get_json(REST_URL + "/annotator?text=" + urllib.parse.quote(text_to_annotate))

    #print_annotations(annotations)

    #annotations = get_json(REST_URL + "/annotator?max_level=3&text=" + urllib.parse.quote(text_to_annotate))
    #print_annotations(annotations)

    #annotations = get_json(REST_URL + "/annotator?include=prefLabel,synonym,definition&text=" + urllib.parse.quote(text_to_annotate))
    #print_annotations(annotations, False)
    return render_template('api.html')

@app.route("/api", methods=['GET', 'POST'])
def api():
    if request.method=='POST':
        print("hi")
        text_to_annotate=request.form.get('explanation')
        annotations = get_json(REST_URL + "/annotator?text=" + urllib.parse.quote(text_to_annotate))
        print("hi")
        print(annotations)
        annotations = get_json(REST_URL + "/annotator?max_level=3&text=" + urllib.parse.quote(text_to_annotate))
        print_annotations(annotations)
        annotations = get_json(REST_URL + "/annotator?include=prefLabel,synonym,definition&text=" + urllib.parse.quote(text_to_annotate))
        print_annotations(annotations, False)
        return redirect(url_for ('home'))
    return render_template('api.html')

def dict_organizer(organized_dict):
    stri=()
    for key, value in organized_dict.items():
        stri+=(key, ' : ', value)
    return stri

def show_ents(doc):
    entities=""
    if doc.ents:
        for ent in doc.ents:
            entities+=ent.text+", "
    else:
        print("No named entities found.")
    return entities

def similarityChecker():
    dic={}
    biography=session['biography']
    name=session['firstName']
    sessionID=session['sessionID']
    mycursor.execute("SELECT * FROM profile WHERE userID=%s", (sessionID,))
    iterator=mycursor.fetchone()
    if iterator:
        sim1=session['profile_info']=iterator[1]
    else:
        print("nada")
    doc1=nlp(sim1)
    mycursor.execute("SELECT * FROM profile CROSS JOIN user ON profile.userID=user.userID")
    Q1="SELECT * FROM user"
    Q2="SELECT * FROM profile"
    for iterator in mycursor:
        sim2=''.join(iterator[1])
        doc2=nlp(sim2)
        similar=doc1.similarity(doc2)
        similar = "{:.2f}".format(similar)
        sessionID2=iterator[2]
        email=iterator[3]
        fName=iterator[4]
        lName=iterator[5]
        dic[sessionID2]=similar, fName, lName, email

    mycursor.execute(Q1)
    sorted_values = sorted(dic.values(), reverse=True)
    sorted_dict = {}

    for i in sorted_values:
        for k in dic.keys():
            if dic[k] == i:
                sorted_dict[k] = dic[k]
                break
    d=list(sorted_dict.values())
    return(d)

def forumPosts():
    dic={}
    mycursor.execute("SELECT * FROM post CROSS JOIN user ON post.userID=user.userID")
    iterator=mycursor.fetchone()
    for iterator in mycursor:
        postID=iterator[0]
        name=iterator[5]
        question=iterator[2]
        explanation=iterator[3]
        dic[postID]=name, question, explanation

    sorted_values = sorted(dic.values(), reverse=True)
    sorted_dict = {}

    for i in sorted_values:
        for k in dic.keys():
            if dic[k] == i:
                sorted_dict[k] = dic[k]
                break
    dic=list(sorted_dict.values())
    return(dic)

def get_json(url):
    opener = urllib.request.build_opener()
    opener.addheaders = [('Authorization', 'apikey token=' + API_KEY)]
    return json.loads(opener.open(url).read())

def print_annotations(annotations, get_class=True):
    for result in annotations:
        class_details = result["annotatedClass"]
        if get_class:
            try:
                class_details = get_json(result["annotatedClass"]["links"]["self"])
            except urllib.error.HTTPError:
                print(f"Error retrieving {result['annotatedClass']['@id']}")
                continue
        print("Class details")
        print("\tid: " + class_details["@id"])
        print("\tprefLabel: " + class_details["prefLabel"])
        print("\tontology: " + class_details["links"]["ontology"])

        print("Annotation details")
        for annotation in result["annotations"]:
            print("\tfrom: " + str(annotation["from"]))
            print("\tto: " + str(annotation["to"]))
            print("\tmatch type: " + annotation["matchType"])

        if result["hierarchy"]:
            print("\n\tHierarchy annotations")
            for annotation in result["hierarchy"]:
                try:
                    class_details = get_json(annotation["annotatedClass"]["links"]["self"])
                except urllib.error.HTTPError:
                    print(f"Error retrieving {annotation['annotatedClass']['@id']}")
                    continue
                pref_label = class_details["prefLabel"] or "no label"
                print("\t\tClass details")
                print("\t\t\tid: " + class_details["@id"])
                print("\t\t\tprefLabel: " + class_details["prefLabel"])
                print("\t\t\tontology: " + class_details["links"]["ontology"])
                print("\t\t\tdistance from originally annotated class: " + str(annotation["distance"]))

        print("\n\n")
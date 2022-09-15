from cgitb import text
import urllib.request, urllib.error, urllib.parse
import json
import os
from pprint import pprint
from typing import Counter
from neo4j import GraphDatabase

driver=GraphDatabase.driver(uri="bolt://localhost:7687", auth=("neo4j", "1234"))
session=driver.session()

REST_URL = "http://data.bioontology.org"
API_KEY = "e82ead30-cdb2-4455-a5cf-bf866935f094"

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
        return(class_details["@id"])

print("Hello would you like to search a word? yes/no")
x=input()
ontologyDetails={}
if x=="yes":
    print("What word would you like to search up?")
    text_to_annotate=input()
    i=0
    while i<1:
        annotations = get_json(REST_URL + "/annotator?include=prefLabel,synonym,definition&text=" + urllib.parse.quote(text_to_annotate))
        stre=print_annotations(annotations, False)
        #print(stre)
        print(annotations[4])
        ontologyDetails[text_to_annotate]=stre
        #print(ontologyDetails)
        i+=1
    print("Would you like to add to database? yes/no")
    data=input()
    if data=="yes":
        keys, values = zip(*ontologyDetails.items())
        ontologyDetailsKey=str(keys[0])
        ontologyDetailsValue=str(values[0])
        #print(ontologyDetailsKey)
        #print(ontologyDetailsValue)
        #session.run("create(n:term{name:'"+ontologyDetailsKey+"'})")
        #session.run("create(n:details{name:'"+ontologyDetailsKey+"', annotation:'"+ontologyDetailsValue+"'})")
        #session.run("match(s:term), (p:details) where s.name='"+ontologyDetailsKey+"' AND p.name='"+ontologyDetailsKey+"' create(s)-[stu:details]->(p)")
else:
    print("Goodbye!!")
    #match(s:term), (p:details)
#where s.name='Term' AND p.name='Details'
#create(s)-[stu:details]->(p)

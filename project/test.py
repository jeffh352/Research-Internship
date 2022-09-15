from typing import Counter
from neo4j import GraphDatabase

driver=GraphDatabase.driver(uri="bolt://localhost:7687", auth=("neo4j", "1234"))
session=driver.session()

print("What query would you like to see?")
x=input()

if(x=="cancer"):
    canc=session.run("match(n{questionID:'1'}) return(n)")
    for node in canc:
        print(node)

elif(x=="all"):
    nodesA=session.run("match(n) return(n.answer)")
    counter=0
    seenAnswer=set()
    seenQuestion=set()

    for node in nodesA:
        if node in seenAnswer:
            counter+=1
            print(node)
        else:
            seenAnswer.add(node)

    nodesQ=session.run("match(n) return(n.question)")
    for node in nodesQ:
        if node in seenQuestion:
            print(node)
        else:
            seenQuestion.add(node)

    print(counter)

print("Would you like to answer a question? Yes/No")
ans=input()
if ans=="Yes":
    qa="match(n:request) return(n)"
    qas=session.run(qa)
    for node in qas:
        print(node)
    print("Which question would you like to answer? Type in the ID")
    pro=input()
    if pro=="1":
        print("What is your answer to this quesiton")
        answ=input()
    elif pro=="2":
        print("What is your answer to this quesiton")
        answ1=input()

print("Would you like to ask a question? Yes/No")
v=input()
if v=="Yes":
    userID="U3"
    questionID="3"
    val=input("What question would you like to ask: ")
    q2="create(n:user_request{name:'User Request', user:'"+userID+"', questionID:'"+questionID+"'})"
    q3="create(n:request{question:'"+val+"', questionID:'"+questionID+"'})"
    q4="match(p:user_request), (s:request) where p.questionID='"+questionID+"' and s.questionID='"+questionID+"' create(p)-[stu:Question]->(s)"
    session.run(q2)
    session.run(q3)
    session.run(q4)
else:
    print("Would you like to see Expert stats? Yes/No")
    y=input()
    if y=="Yes":
        exp=session.run("match(e:expert)-[b:Answer]->(a:request) return(e)")
        for node in exp:
            print(node)
        print("Which expert?")
        expertName=input()
        if expertName=="Expert1":
            exp1=session.run("match(e:expert{name:'Expert1'})-[b:Answer]->(a:request) return e, b, a")
            for node in exp1:
                print(node)

print("Which question would you like to see")

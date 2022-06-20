import mysql.connector

db=mysql.connector.connect(host="localhost", user="root", passwd="root", database="Accounts")

mycursor=db.cursor()
#mycursor.execute("DROP TABLE profile")
mycursor.execute("ALTER TABLE User ADD COLUMN FOREIGN KEY(userID) REFERENCES user(userID)")
#mycursor.execute("CREATE DATABASE accounts")
#mycursor.execute("CREATE TABLE profile (profile_ID int PRIMARY KEY, userID int FOREIGN KEY(userID) REFERENCES user(userID), profile_info VARCHAR(500))")
#mycursor.execute("DESCRIBE User")
#for x in mycursor:
#    print(x)
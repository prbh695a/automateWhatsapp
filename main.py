from datetime import datetime

from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
from pymongo import MongoClient

cluster = MongoClient("URI")
db = cluster["bakery"]
users = db["users"]
orders = db["orders"]

app = Flask(__name__)


@app.route("/", methods=["get", "post"])
def reply():
    text = request.form.get("Body")
    number = request.form.get("From")
    number = number.replace("whatsapp:", "")
    response = MessagingResponse()

    user = users.find_one({"number": number})
    if bool(user) == False:
        response.message("Hi There! My name is Peter, I will get you started!!!")
        response.message("You are not an existing user")
        response.message("Enter your name (your name only):")
        users.insert_one({"number":number,"status": "name", "messages": []})

    else:
        if user['status'] == 'name':
            orders.insert_one({"number": number, "name": text})
            users.update_one({"number": number},{"$set":{"status": "exist"}})
            response.message("Thank you, we have registered you")
        elif user['status'] == 'exist':
            name = orders.find_one({"number":number})['name']
            response.message(f"Thank you, welcome back {name}")
        else:
            response.message("You made a wrong choice")


    #users.update_one({"number":number}, {"$push": {"messages": {"text": text, "date": datetime.now()}}})
    return str(response)


if __name__ == "__main__":
    app.run(port=5000)

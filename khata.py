from flask import Flask, render_template, request, redirect
import pymongo
from datetime import date, timedelta, datetime
import os


myClient = pymongo.MongoClient(os.environ['MONGO_CLIENT'])

# create database
myDb = myClient['SGGoalsDB']

#create collection
myCollection = myDb['goals']
myOtherCollection = myDb['report']
myGoal = myDb['finalgoal']

app = Flask(__name__)


@app.route('/home')
def home():
    finGoal = myGoal.find()
    data = myCollection.find()
    return render_template('/khata.html', data=data, goal=finGoal)


@app.route('/add-goal', methods=['POST'])
def add_goal():
    forgoal = request.form['forGoal']
    amount = float(request.form['newGoal'])
    data = myCollection.find_one({'for': forgoal}, {'_id': 0, 'amount': 1})
    print(data)
    if data is not None:
        print(data)
        new_amount = amount + float(data['amount'])
        myquery = {'for': forgoal}
        newvalues = {"$set": {"amount": new_amount}}
        myCollection.update_one(myquery, newvalues)

        report_data = {
            'for': forgoal,
            'amount': amount,
            'date': datetime.today()
        }
        insert_report = myOtherCollection.insert_one(report_data)

        newach_goal = {"$set": {"acheivedgoal": new_amount}}

        myGoal.update_one({}, newach_goal)

        return redirect("/home")

    else:
        new_data = {
            'for': forgoal,
            'amount': amount,
        }
        insert_data = myCollection.insert_one(new_data)

        if insert_data.inserted_id:
            report_data = {
                'for': forgoal,
                'amount': amount,
                'date': datetime.today()
            }
            insert_report = myOtherCollection.insert_one(report_data)

            data = myGoal.find_one({}, {'_id': 0})
            new_amount = float(data['acheivedgoal']) + amount
            newvalues = {"$set": {"acheivedgoal": new_amount}}

            myGoal.update_one({}, newvalues)

        return redirect('/home')


@app.route('/goal-report', methods=['GET','POST'])
def report():
    data = myOtherCollection.find()
    return render_template('/goalReport.html', data=data)


if __name__ == "__main__":
    app.run(debug=True)
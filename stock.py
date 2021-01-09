from flask import Flask, render_template, request, redirect
import pymongo
import os
from datetime import date, timedelta, datetime


myClient = pymongo.MongoClient(os.environ['MONGO_CLIENT'])

# create database
myDb = myClient['stocksDB']

# create collection
myCollection = myDb['subscriptions']

# create database
my_Db = myClient['SGGoalsDB']

#create collection
my_Collection = my_Db['goals']
myOtherCollection = my_Db['report']
myGoal = my_Db['finalgoal']

app = Flask(__name__)

def send_stock_sms(stk_name, company_name, email, mobile, message):
    STOCK_NAME = stk_name
    COMPANY_NAME = company_name

    data = myCollection.find_one({'symbol': STOCK_NAME, 'mobileNo': '+91'+mobile}, {'_id': 0})
    print(data)
    if data is not None:
        message.append("You have already subscribed for stock "+STOCK_NAME+", "+COMPANY_NAME)
        return
    else:
        new_data = {
            'symbol': STOCK_NAME,
            'company': COMPANY_NAME,
            'email': email,
            'mobileNo': '+91'+mobile,
        }

        insert_data = myCollection.insert_one(new_data)
        if insert_data.inserted_id:
            message.append('Thank you for registering, We will send you notification via SMS for '+ STOCK_NAME +' stock daily at 8 AM.')
            return
        else:
            message.append('Failed to Register! please try again!')
            return


@app.route("/", methods=['GET', 'POST'])
def index():
    return render_template("stocks.html", message="")


@app.route("/submit", methods=['GET', 'POST'])
def submit():
    if request.method == "POST":
        stock_symbol = request.form['symbol']
        stock_name = request.form['stk_name']
        email = request.form['email']
        mobile = request.form['mobile']
        mess = []
        send_stock_sms(stock_symbol.upper(), stock_name.upper(), email, mobile, mess)
        return render_template("stocks.html", message=mess)
    else:
        return render_template("stocks.html", message="")

    
@app.route('/home', methods=['GET','POST'])
def home():
    finGoal = myGoal.find()
    data = my_Collection.find()
    return render_template('/khata.html', data=data, goal=finGoal)


@app.route('/add-goal', methods=['POST'])
def add_goal():
    forgoal = request.form['forGoal']
    amount = float(request.form['newGoal'])
    data = my_Collection.find_one({'for': forgoal}, {'_id': 0, 'amount': 1})
    print(data)
    if data is not None:
        print(data)
        new_amount = amount + float(data['amount'])
        myquery = {'for': forgoal}
        newvalues = {"$set": {"amount": new_amount}}
        my_Collection.update_one(myquery, newvalues)

        report_data = {
            'for': forgoal,
            'amount': amount,
            'date': datetime.today()
        }
        insert_report = myOtherCollection.insert_one(report_data)

        data = myGoal.find_one({}, {'_id': 0})
        amount_new = float(data['acheivedgoal']) + amount
        newach_goal = {"$set": {"acheivedgoal": amount_new}}

        myGoal.update_one({}, newach_goal)

        return redirect("/home")

    else:
        new_data = {
            'for': forgoal,
            'amount': amount,
        }
        insert_data = my_Collection.insert_one(new_data)

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


@app.route('/new-goal/<float:amt>', methods=['GET','POST'])
def new_goal(amt):
    newvalues = {"$set": {"finalgoal": amt}}
    myGoal.update_one({}, newvalues)
    return redirect("/home")


if __name__ == "__main__":
    app.run()

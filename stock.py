from flask import Flask, render_template, request
import pymongo


myClient = pymongo.MongoClient("mongodb+srv://admin-steve:steve123@steve.ko2up.mongodb.net/")

# create database
myDb = myClient['stocksDB']

# create collection
myCollection = myDb['subscriptions']

app = Flask(__name__)


def send_stock_sms(stk_name, company_name, email, mobile, message):
    STOCK_NAME = stk_name
    COMPANY_NAME = company_name

    data = myCollection.find_one({'symbol': STOCK_NAME, 'mobileNo': '+91'+mobile}, {'_id': 0})
    print(data)
    if data is not None:
        message.append("You have already subscribed for stock - "+STOCK_NAME+", "+COMPANY_NAME)
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
            message.append('Thank you for registering, We will send you notification via SMS for '+ STOCK_NAME +' stock daily @8:00 AM.')
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


if __name__ == "__main__":
    app.run(debug=True)
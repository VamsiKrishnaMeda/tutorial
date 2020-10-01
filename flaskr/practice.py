import time
from pymongo import MongoClient
from datetime import date, datetime
from pprint import pprint

from flask import Flask
from flask import Blueprint
from flask import flash
from flask import g
from flask import redirect
from flask import render_template
from flask import request
from flask import url_for
from werkzeug.exceptions import abort
from werkzeug.utils import secure_filename

from flaskr.auth import login_required
from flaskr.db import get_db


bp = Blueprint('practice', __name__)


@bp.route('/practice', methods=['GET', 'POST'])
@login_required
def practice():
    if request.method == 'POST':
        date_practice = request.form['date_practice']
        if date_practice != '' and datetime.fromisoformat(date_practice).date() < datetime.now().date():
            flash('Enter a valid date')
        time.sleep(100)

    return render_template('twitter/practice.html')          

        # client = MongoClient(port=27017)
        # db = client['Coronavirus']
        # collection = db['practice']
        # data = collection.aggregate([
        #     {
        #         '$match': { 'filter_words': 'coronavirus' }
        #     },
        #     {
        #         '$group': {
        #             '_id': {
        #                 'hour': { '$hour': '$time' },
        #                 'month': { '$month': '$time' },
        #                 'day': { '$dayOfMonth': '$time' },
        #                 'year': { '$year': '$time' }
        #             },
        #             'count': { '$sum': 1 }
        #         }
        #     }
        # ])
        # coronavirus_data = list(data)

        # data = collection.aggregate([
        #     {
        #         '$match': { 'filter_words': 'covid-19' }
        #     },
        #     {
        #         '$group': {
        #             '_id': {
        #                 'hour': { '$hour': '$time' },
        #                 'month': { '$month': '$time' },
        #                 'day': { '$dayOfMonth': '$time' },
        #                 'year': { '$year': '$time' }
        #             },
        #             'count': { '$sum': 1 }
        #         }
        #     }
        # ])
        # covid_data = list(data)

        # data = collection.aggregate([
        #     {
        #         '$match': { 'filter_words': 'covid19' }
        #     },
        #     {
        #         '$group': {
        #             '_id': {
        #                 'hour': { '$hour': '$time' },
        #                 'month': { '$month': '$time' },
        #                 'day': { '$dayOfMonth': '$time' },
        #                 'year': { '$year': '$time' }
        #             },
        #             'count': { '$sum': 1 }
        #         }
        #     }
        # ])
        # cov_data = list(data)


        # formatted_data = []
        # formatted_data.append(['Time', 'Coronavirus', 'Covid-19', 'Covid19'])
        # for index in range(0, len(coronavirus_data)):
        #     corona = coronavirus_data[index]
        #     covid = covid_data[index]
        #     cov = cov_data[index]
        #     date = corona['_id']
        #     time = str(date['year']) + '/' + str(date['month']) + '/' + str(date['day']) + ' '  + str(date['hour']) + ':00'
        #     formatted_data.append([time, corona['count'], covid['count'], cov['count']])

        # data = [
        #     ['Time', 'Coronavirus', 'Covid-19', 'Covid19'],
        #     ['2020/9/17 12:00', 2193, 1576, 1071],
        #     ['2020/9/17 13:00', 3346, 2754, 1739],
        #     ['2020/9/15 23:00', 1951, 1876, 2086]
        # ]

        # return render_template('twitter/practice.html', data = data)
        # pprint(formatted_data)


# client = MongoClient(port=27017)
# db = client['Coronavirus']
# collection = db['test']

# total_tweets = collection.count()
# tweet_counter = 0

# # ADDING TIME TO THE COLLECTION
# for doc in collection.find():
#     if 'time' not in doc:
#         if 'timestamp_ms' in doc:
#             timestamp_ms = int(doc['timestamp_ms'])
#         else:
#             timestamp_ms = int(doc['limit']['timestamp_ms'])
#         time = datetime.utcfromtimestamp(timestamp_ms / 1000)
#         collection.update_one(
#             { '_id': doc['_id'] },
#             { '$set': { 'time': time } }
#         )
#     tweet_counter += 1
#     print("\r", end="")
#     print("Current # of MongoDB tweet documents read out of", total_tweets, ":", tweet_counter, end="")
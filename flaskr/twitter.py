import functools
import time
import itertools
import re
import threading
import subprocess

from pymongo import MongoClient

from flask import Blueprint
from flask import flash
from flask import g
from flask import redirect
from flask import render_template
from flask import request
from flask import session
from flask import url_for
from flask import Markup
from flask import jsonify
from werkzeug.security import check_password_hash
from werkzeug.security import generate_password_hash

from flaskr.db import get_db
from flaskr.auth import login_required


bp = Blueprint("twitter", __name__, url_prefix="/twitter")


def run_tweet_collect(keywords, start_time, duration, file_name, summary_file_name):
    """Starts a twitter collection with the given parameters and
    restarts the collection if it's not running
    """
    import time
    from datetime import datetime, timedelta

    is_running = False
    pid = 0
    search_pid = ''

    # When you want to end the collection
    start_time = datetime(datetime.now().year, datetime.now().month, datetime.now().day, int(start_time.split(':')[0]), int(start_time.split(':')[1]))
    end_time = start_time + timedelta(minutes=int(duration))

    while (datetime.now() <= end_time):

        # Start Tweet Collection if not running
        if not is_running:
            with open('C:/Users/bncmo/Downloads/FailLog.txt', 'a+') as error_file:
                error_file.write(str(datetime.now()) + '\n')
            pid = subprocess.Popen(['python', 'flaskr/static/collect/RevisedTweetCollect.py', keywords, file_name + '.txt', summary_file_name + '.txt', 'flaskr\static\KeySet1.txt', duration, str(start_time.hour), str(start_time.minute)]).pid
            search_pid = 'pid eq ' + str(pid)

        # Check if the Tweet Collection is running
        process = subprocess.Popen(['tasklist', '/fi', search_pid, '/nh'], shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        stdout, stderr = process.communicate()
        is_running = str(pid) in str(stdout)
        
        time.sleep(10)


def run_query(collection_name, process_name):
    location_reference = {
        'US': 'United States',
        'MX': 'Mexico',
        'AR': 'Argentina',
        'BR': 'Brazil',
        'CA': 'Canada',
        'DO': 'Dominican Republic',
        'EC': 'Ecuador',
        'ES': 'Spain',
        'FR': 'France',
        'GB': 'Great Britain',
        'IN': 'India',
        'IT': 'Italy',
        'CO': 'Columbia',
        'AU': 'Australia',
        'JP': 'Japan',
        'ID': 'Indonesia'
    }
    language_reference = {
        'en': 'English',
        'es': 'Spanish',
        'fr': 'French',
        'it': 'Italian',
        'ja': 'Japanese',
        'pt': 'Portugese',
        'th': 'Thai',
        'und': 'Undefined',
        'tr': 'Turkish',
        'ca': 'Catalan',
        'in': 'Indonesian'
    }
    client = MongoClient(port=27017)
    db = client['Coronavirus']
    collection = db[collection_name]

    if process_name == 'Language':
        data = collection.aggregate([
            {
                '$group': {
                    '_id': "$lang",
                    "count": { '$sum': 1 }
                }
            },
            {
                '$sort': { "count": -1 }
            }
        ])
        language_data = list(data)
        data = {}
        data['Language'] = 'Count'
        for datum in language_data:
            if datum['_id'] in language_reference:
                data[language_reference[datum['_id']]] = datum['count']
            else:
                data[datum['_id']] = datum['count']
    else:
        data = collection.aggregate([
            {
                '$group': {
                    '_id': "$place.country_code",
                    "count": { '$sum': 1 }
                }
            },
            {
                '$sort': { 'count': -1 }
            }
        ])
        location_data = list(data)
        data = {}
        data['Country'] = 'Count'
        for datum in location_data:
            if datum['_id'] is not None:
                if datum['_id'] in location_reference:
                    data[location_reference[datum['_id']]] = datum['count']
                else:
                    data[datum['_id']] = datum['count']

    return data


def keyword_analysis(collection_name):
    client = MongoClient(port=27017)
    db = client['Coronavirus']
    collection = db[collection_name]

    data = collection.aggregate([
        {
            '$match': { 'filter_words': 'coronavirus' }
        },
        {
            '$group': {
                '_id': {
                    'hour': { '$hour': '$time' },
                    'month': { '$month': '$time' },
                    'day': { '$dayOfMonth': '$time' },
                    'year': { '$year': '$time' }
                },
                'count': { '$sum': 1 }
            }
        }
    ])
    coronavirus_data = list(data)

    data = collection.aggregate([
        {
            '$match': { 'filter_words': 'covid-19' }
        },
        {
            '$group': {
                '_id': {
                    'hour': { '$hour': '$time' },
                    'month': { '$month': '$time' },
                    'day': { '$dayOfMonth': '$time' },
                    'year': { '$year': '$time' }
                },
                'count': { '$sum': 1 }
            }
        }
    ])
    covid_data = list(data)

    data = collection.aggregate([
        {
            '$match': { 'filter_words': 'covid-19' }
        },
        {
            '$group': {
                '_id': {
                    'hour': { '$hour': '$time' },
                    'month': { '$month': '$time' },
                    'day': { '$dayOfMonth': '$time' },
                    'year': { '$year': '$time' }
                },
                'count': { '$sum': 1 }
            }
        }
    ])
    cov_data = list(data)

    formatted_data = []
    formatted_data.append(['Time', 'Coronavirus', 'Covid-19'])
    for index in range(0, len(coronavirus_data)):
        corona = coronavirus_data[index]
        covid = covid_data[index]
        cov = cov_data[index]
        date = corona['_id']
        time = str(date['year']) + '/' + str(date['month']) + '/' + str(date['day']) + ' '  + str(date['hour']) + ':00'
        formatted_data.append([time, corona['count'], covid['count'], cov['count']])

    return formatted_data


@bp.before_app_request
def load_logged_in_user():
    """If a user id is stored in the session, load the user object from
    the database into ``g.user``"""    
    user_id = session.get('user_id')

    if user_id is None:
        g.user = None
    else:
        g.user = (
            get_db().execute('SELECT * FROM user WHERE id = ?', (user_id,)).fetchone()
        )


@bp.route('/collect', methods=['GET', 'POST'])
@login_required
def collect():
    """Start a New Collection

    Get input from user and start the twitter collection
    """
    if request.method == 'POST':
        keywords = request.form['keywords']
        start_time = request.form['start_time']
        duration = request.form['duration']
        file_name = request.form['file_name']
        summary_file_name = request.form['summary_file_name']
        error = None

        if start_time in [None, '', ' ']:
            error = 'Enter a valid start time'
        elif duration in [None, '', ' ']:
            error = 'Enter a valid duration'
        
        if error is None:
            start_collection = threading.Thread(name='start_collection', target=run_tweet_collect, args=(keywords, start_time, duration, file_name, summary_file_name), daemon=True)
            start_collection.start()
            flash('Collection Started')
            # run_tweet_collect(keywords, start_time, duration, file_name, summary_file_name)    
        else:
            flash(error)

    return render_template('twitter/collect.html')


@bp.route('/process', methods=['GET', 'POST'])
@login_required
def process():
    """Run analysis on tweets

    Get input from user to process tweets
    """
    if request.method == 'POST':
        collection_name = request.form['collection_name']
        process_name = request.form['analysis']
        title = collection_name + ' ' + process_name + ' Analysis'
        if 'Location' in title:
            title += ' (Ignoring tweets without location data)'
        if process_name == 'Keyword':
            line_data = keyword_analysis(collection_name)
            return render_template('twitter/process.html', collection_list = ['practice', 'Mar_01', 'test'], process_list = ['Language', 'Location', 'Keyword'], title = title, line_data = line_data)
        data = run_query(collection_name, process_name)
        # data = {'Task' : 'Hours per Day', 'Work' : 11, 'Eat' : 2, 'Commute' : 2, 'Watching TV' : 2, 'Sleeping' : 7}
        return render_template('twitter/process.html', collection_list = ['practice', 'Mar_01', 'test'], process_list = ['Language', 'Location', 'Keyword'], title = title, data = data)
    
    return render_template('twitter/process.html', collection_list = ['practice', 'Mar_01', 'test'], process_list = ['Language', 'Location', 'Keyword'])


@bp.route('/mongo', methods=['GET', 'POST'])
@login_required
def mongo():
    """Mongo operations

    Get input from user to run MongoDb operations
    """
    if request.method == 'POST':
        username = request.form['username']
    
    return render_template('twitter/mongo.html')
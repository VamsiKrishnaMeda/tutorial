import threading
import subprocess
from datetime import datetime
import json
from os import listdir
from os.path import isfile, join

from pymongo import MongoClient

from flask import jsonify
from flask import Blueprint
from flask import flash
from flask import g
from flask import render_template
from flask import request
from flask import session

from flaskr.db import get_db
from flaskr.auth import login_required


bp = Blueprint("twitter", __name__, url_prefix="/twitter")


def run_tweet_collect(keywords: str, start_date: str, start_time: str, duration: str, directory: str, data_filename: str, summary_filename: str) -> None:
    """
    Starts a twitter collection with the given parameters 
    and restarts the collection if it gets interrupted

    Parameters:
    -----------
    keywords: List of keywords on which tweets are be collected seperated by ' OR '
    start_date: The start date for the collection
    start_time: The start time for the collection
    duration: Duration in minutes for for which tweets are to be collected
    directory: Full path to store the data and summary files
    data_filename: Filename for the Data file
    summary_filename: Filename for the Summary file

    """
    # MODIFIED ON 09/30/2020
    # Coverting start_date into a datetime object
    if start_date == '':
        start_date = datetime.fromisoformat(str(datetime.now().date()))
    else:
        start_date = datetime.fromisoformat(start_date)
    
    # Setting start_time, faillog and exit_code
    start_time = datetime(start_date.year, start_date.month, start_date.day, int(start_time.split(':')[0]), int(start_time.split(':')[1]))
    faillog_filename = directory + 'FailLog.txt'
    exit_code = None

    while exit_code != 0:
        with open(faillog_filename, 'a+') as faillog:
            if exit_code is None:
                # Starting the collection for the first time
                faillog.write('Collection with Keywords: ' + keywords + ' started on: ' + str(start_time.date()) + '\n')
                faillog.write('Start: ' + str(start_time.time()) + '\n')
            else:
                # Restarting the collection after an interruption
                faillog.write('Restart: ' + str(datetime.now().time()))

        # Calling RevisedTweetCollect.py as a subprocess
        process = subprocess.Popen(['python', 'flaskr/static/collect/RevisedTweetCollect.py', keywords, directory + data_filename, directory + summary_filename, 'flaskr/static/KeySet1.txt', duration, str(start_time.hour), str(start_time.minute), '--date', str(start_time.month), str(start_time.day), str(start_time.year)])
        # Wait for the subprocess to finish
        process.wait()
        exit_code = process.returncode

        with open(faillog_filename, 'a+') as faillog:
            if exit_code == 0:
                # Completed collection
                faillog.write('End: ' + str(datetime.now().time()) + '\n\n')
            else:
                # Collection failed
                faillog.write('Fail: ' + str(datetime.now().time()) + '\n')

    """
    OLDER CODE
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
    """


def run_query(collection_name, process_name):
    """
    Runs the requested Analysis query on MongoDb

    Parameters:
    -----------
    collection_name: name of the collection in MongoDb database
    process_name: name of the analysis to be run
    """
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
    # Mongo Connection
    client = MongoClient(port=27017)
    db = client['Coronavirus']
    collection = db[collection_name]

    # Language analysis query
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
        # Transforming the query result into a 2D array as required by Google Charts
        data = []
        data.append(['Language', 'Count'])
        for datum in language_data:
            if datum['_id'] in language_reference:
                data.append([language_reference[datum['_id']], datum['count']])
                # data[language_reference[datum['_id']]] = datum['count']
            else:
                data.append([datum['_id'], datum['count']])
                # data[datum['_id']] = datum['count']
    # Location analysis query
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
        # Transforming the query result from list to dict
        data = []
        data.append(['Country', 'Count'])
        for datum in location_data:
            if datum['_id'] is not None:
                if datum['_id'] in location_reference:
                    data.append([location_reference[datum['_id']], datum['count']])
                    # data[location_reference[datum['_id']]] = datum['count']
                else:
                    data.append([datum['_id'], datum['count']])
                    # data[datum['_id']] = datum['count']

    return data


def keyword_analysis(collection_name):
    """
    Runs the Keyword analysis query on MongoDb

    Parameters
    -----------------
    collection_name: name of the collection in MongoDb database
    """
    # Mongo connection
    client = MongoClient(port=27017)
    db = client['Coronavirus']
    collection = db[collection_name]

    # Keywords analysis query for 'Coronavirus'
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

    # Keywords analysis query for 'covid-19'
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

    # Keywords analysis query for 'covid19'
    data = collection.aggregate([
        {
            '$match': { 'filter_words': 'covid19' }
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

    # Transforming the query results into a 2D array as required by Google Charts
    formatted_data = []
    formatted_data.append(['Time', 'Coronavirus', 'Covid-19', 'Covid19'])
    for index in range(0, len(coronavirus_data)):
        corona = coronavirus_data[index]
        covid = covid_data[index]
        cov = cov_data[index]
        date = corona['_id']
        time = str(date['year']) + '/' + str(date['month']) + '/' + str(date['day']) + ' '  + str(date['hour']) + ':00'
        formatted_data.append([time, corona['count'], covid['count'], cov['count']])

    return formatted_data


def mongo_import(directory, database_name, collection_name):
    """
    Imports all the files from the given directory to the specified
    MongoDb database and collection

    Parameters
    ----------
    directory: full directory path to the data files
    database: name of the MongoDb database to import data to
    collection: name of the MongoDb collection to import data to
    """
    files = [join(directory, filename) for filename in listdir(directory) if isfile(join(directory, filename))]
    for file in files:
        import_process = subprocess.Popen(['mongoimport', '--db', database_name, '--collection', collection_name, '--file', file])
        import_process.wait()


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
# @login_required
def collect():
    """Start a New Collection

    Get input from user and start the twitter collection
    """
    if request.method == 'POST':
        request_data = json.loads(request.data)
        keywords = request_data['keywords']
        start_date = request_data['startDate']
        start_time = request_data['startTime']
        duration = request_data['duration']
        directory = request_data['directory']
        file_name = request_data['filename']
        summary_file_name = request_data['summaryFilename']
        error = None

        if start_time in [None, '', ' ']:
            error = 'Enter a valid start time'
        elif duration in [None, '', ' ']:
            error = 'Enter a valid duration'
        elif start_date != '' and datetime.fromisoformat(start_date).date() < datetime.now().date():
            error = 'Enter a valid date'
        
        if error is None:
            start_collection = threading.Thread(name='start_collection', target=run_tweet_collect, args=(keywords, start_date, start_time, duration, directory, file_name, summary_file_name), daemon=True)
            start_collection.start()
            return 'Success'
            # run_tweet_collect(keywords, start_time, duration, file_name, summary_file_name)    
        else:
            return error

    return render_template('twitter/collect.html')


@bp.route('/process', methods=['GET', 'POST'])
# @login_required
def process():
    """Run analysis on tweets

    Get input from user to process tweets
    """
    if request.method == 'POST':
        request_data = json.loads(request.data)
        collection_name = request_data['analyticsCollection']
        process_name = request_data['analysis']
        title = collection_name + ' ' + process_name + ' Analysis'
        if 'Location' in title:
            title += ' (Ignoring tweets without location data)'    
        if process_name == 'Keyword':
            data = keyword_analysis(collection_name)
            column_names = ['Time', 'Coronavirus', 'Covid-19', 'Covid19']
            options = {'width': 950, 'height': 500}
            type = 'LineChart'
            # return render_template('twitter/process.html', collection_list = ['practice', 'Mar_01', 'test'], process_list = ['Language', 'Location', 'Keyword'], title = title, line_data = line_data)
        else:
            data = run_query(collection_name, process_name)
            if process_name == 'Location':
                column_names = ['Location', 'Count']
            else:
                column_names = ['Language', 'Count']
            options = {'pieHole': 0.4, 'sliceVisibilityThreshold': 0.02, 'width': 950, 'height': 500}
            type = 'PieChart'

        return jsonify({'title': title, 'type': type, 'data': data, 'columnNames': column_names, 'options': options})
        # return render_template('twitter/process.html', collection_list = ['practice', 'Mar_01', 'test'], process_list = ['Language', 'Location', 'Keyword'], title = title, data = data)
    
    return render_template('twitter/process.html', collection_list = ['practice', 'Mar_01', 'test'], process_list = ['Language', 'Location', 'Keyword'])


@bp.route('/mongo', methods=['GET', 'POST'])
# @login_required
def mongo():
    """Mongo operations

    Get input from user to run MongoDb operations
    """
    if request.method == 'POST':
        request_data = json.loads(request.data)
        if request_data['process'] == 'import':
            directory = request_data['directory']
            database_name = request_data['database']
            collection_name = request_data['collection']
            mongo_import(directory, database_name, collection_name)
        elif request_data['process'] == 'adder':
            database = request.form['database']
            collection = request.form['collection']
            keywords = request.form['keywords']
            subprocess.Popen(['python', 'flaskr/static/mongo/KeywordAdder.py', database, collection, keywords])
    
    return render_template('twitter/mongo.html')
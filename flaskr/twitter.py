import threading
import subprocess
from datetime import datetime

from pymongo import MongoClient

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
        # Transforming the query result from list to dict
        data = {}
        data['Language'] = 'Count'
        for datum in language_data:
            if datum['_id'] in language_reference:
                data[language_reference[datum['_id']]] = datum['count']
            else:
                data[datum['_id']] = datum['count']
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
        start_date = request.form['start_date']
        start_time = request.form['start_time']
        duration = request.form['duration']
        directory = request.form['directory']
        file_name = request.form['file_name']
        summary_file_name = request.form['summary_file_name']
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
        if request.form.post['mongo'] == 'Import':
            import_directory = request.form['import_directory']
            import_database = request.form['import_database']
            import_collection = request.form['import_collection']
            print('Import Request with {}, {}, {}'.format(import_directory, import_database, import_collection))
            flash('Import Request with {}, {}, {}'.format(import_directory, import_database, import_collection))
        elif request.form.post['mongo'] == 'Add Keywords':
            keyword_database = request.form['keyword_database']
            keyword_collection = request.form['keyword_collection']
            keyword_keywords = request.form['keyword_keywords']
            print('Add Keywords Request with {}, {}, {}'.format(keyword_database, keyword_collection, keyword_keywords))
            flash('Add Keywords Request with {}, {}, {}'.format(keyword_database, keyword_collection, keyword_keywords))
    
    return render_template('twitter/mongo.html')
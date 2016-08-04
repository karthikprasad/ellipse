#! /usr/bin/python2.7

### Backend and business logic of Ellipse
### @author: karthik prasad
### @date: 17 Mar 2016

import calendar as cal
import collections as coll
import html2text
import json
import math
import pymongo
import requests
import time
import urllib
from nltk import wordnet as wn

MONGODB_URI  = 'mongodb://<user_name>:<password>.mlab.com:11449/<account_name>'
MONGODB_DB   = '<mongodb_name>'
MONGODB_USER = '<user_name>'
MONGODB_PASS = '<password>'
COLL_NAME    = '<coll_name>'
EVENTFUL_KEY = '<eventful_api_authentication_key>'
MEETUP_KEY   = '<meetup_api_authentication_key>'

EMOTION_MAP = {}
EMOTION_MAP['Food'] = {'Dislike' : -1, 'Neutral' : 1, 'Yum' : 2}
EMOTION_MAP['Entertainment'] = {'Yawn' : -1, 'Neutral' : 1, 'Happy' : 2, 'Love' : 3}
EMOTION_MAP['Sports'] = {'Upset' : -1, 'Happy' : 1, 'Celebrate' : 2}

FREQ_WEIGHT  = 0.15
DECAY_WEIGHT = 0.85

INITIAL_SCORE = 10
DECAY_RATE = {}
DECAY_RATE['Food'] = 0.693/45  # 45 days is the half life
DECAY_RATE['Entertainment'] = 0.693/90
DECAY_RATE['Sports'] = 0.693/180

STOPWORDS = ['a', 'able', 'about', 'above', 'abst', 'accordance', 'according', 'accordingly', 'across', 'act', 'actually', 'added', 'adj', 'affected', 'affecting', 'affects', 'after', 'afterwards', 'again', 'against', 'ah', 'all', 'almost', 'alone', 'along', 'already', 'also', 'although', 'always', 'am', 'among', 'amongst', 'an', 'and', 'announce', 'another', 'any', 'anybody', 'anyhow', 'anymore', 'anyone', 'anything', 'anyway', 'anyways', 'anywhere', 'apparently', 'approximately', 'are', 'aren', 'arent', 'arise', 'around', 'as', 'aside', 'ask', 'asking', 'at', 'auth', 'available', 'away', 'awfully', 'b', 'back', 'be', 'became', 'because', 'become', 'becomes', 'becoming', 'been', 'before', 'beforehand', 'begin', 'beginning', 'beginnings', 'begins', 'behind', 'being', 'believe', 'below', 'beside', 'besides', 'between', 'beyond', 'biol', 'both', 'brief', 'briefly', 'but', 'by', 'c', 'ca', 'came', 'can', 'cannot', 'cant', 'cause', 'causes', 'certain', 'certainly', 'co', 'com', 'come', 'comes', 'contain', 'containing', 'contains', 'could', 'couldnt', 'd', 'date', 'did', 'didnt', 'different', 'do', 'does', 'doesnt', 'doing', 'done', 'dont', 'down', 'downwards', 'due', 'during', 'e', 'each', 'ed', 'edu', 'effect', 'eg', 'eight', 'eighty', 'either', 'else', 'elsewhere', 'end', 'ending', 'enough', 'especially', 'et', 'et-al', 'etc', 'even', 'ever', 'every', 'everybody', 'everyone', 'everything', 'everywhere', 'ex', 'except', 'f', 'far', 'few', 'ff', 'fifth', 'first', 'five', 'fix', 'followed', 'following', 'follows', 'for', 'former', 'formerly', 'forth', 'found', 'four', 'from', 'further', 'furthermore', 'g', 'gave', 'get', 'gets', 'getting', 'give', 'given', 'gives', 'giving', 'go', 'goes', 'gone', 'got', 'gotten', 'h', 'had', 'happens', 'hardly', 'has', 'hasnt', 'have', 'havent', 'having', 'he', 'hed', 'hence', 'her', 'here', 'hereafter', 'hereby', 'herein', 'heres', 'hereupon', 'hers', 'herself', 'hes', 'hi', 'hid', 'him', 'himself', 'his', 'hither', 'home', 'how', 'howbeit', 'however', 'hundred', 'i', 'id', 'ie', 'if', 'ill', 'im', 'immediate', 'immediately', 'importance', 'important', 'in', 'inc', 'indeed', 'index', 'information', 'instead', 'into', 'invention', 'inward', 'is', 'isnt', 'it', 'itd', 'itll', 'its', 'itself', 'ive', 'j', 'just', 'k', 'keep  keeps', 'kept', 'kg', 'km', 'know', 'known', 'knows', 'l', 'largely', 'last', 'lately', 'later', 'latter', 'latterly', 'least', 'less', 'lest', 'let', 'lets', 'like', 'liked', 'likely', 'line', 'little', 'll', 'look', 'looking', 'looks', 'ltd', 'm', 'made', 'mainly', 'make', 'makes', 'many', 'may', 'maybe', 'me', 'mean', 'means', 'meantime', 'meanwhile', 'merely', 'mg', 'might', 'million', 'miss', 'ml', 'more', 'moreover', 'most', 'mostly', 'mr', 'mrs', 'much', 'mug', 'must', 'my', 'myself', 'n', 'na', 'name', 'namely', 'nay', 'nd', 'near', 'nearly', 'necessarily', 'necessary', 'need', 'needs', 'neither', 'never', 'nevertheless', 'new', 'next', 'nine', 'ninety', 'no', 'nobody', 'non', 'none', 'nonetheless', 'noone', 'nor', 'normally', 'nos', 'not', 'noted', 'nothing', 'now', 'nowhere', 'o', 'obtain', 'obtained', 'obviously', 'of', 'off', 'often', 'oh', 'ok', 'okay', 'old', 'omitted', 'on', 'once', 'one', 'ones', 'only', 'onto', 'or', 'ord', 'other', 'others', 'otherwise', 'ought', 'our', 'ours', 'ourselves', 'out', 'outside', 'over', 'overall', 'owing', 'own', 'p', 'page', 'pages', 'part', 'particular', 'particularly', 'past', 'per', 'perhaps', 'placed', 'please', 'plus', 'poorly', 'possible', 'possibly', 'potentially', 'pp', 'predominantly', 'present', 'previously', 'primarily', 'probably', 'promptly', 'proud', 'provides', 'put', 'q', 'que', 'quickly', 'quite', 'qv', 'r', 'ran', 'rather', 'rd', 're', 'readily', 'really', 'recent', 'recently', 'ref', 'refs', 'regarding', 'regardless', 'regards', 'related', 'relatively', 'research', 'respectively', 'resulted', 'resulting', 'results', 'right', 'run', 's', 'said', 'same', 'saw', 'say', 'saying', 'says', 'sec', 'section', 'see', 'seeing', 'seem', 'seemed', 'seeming', 'seems', 'seen', 'self', 'selves', 'sent', 'seven', 'several', 'shall', 'she', 'shed', 'shell', 'shes', 'should', 'shouldnt', 'show', 'showed', 'shown', 'showns', 'shows', 'significant', 'significantly', 'similar', 'similarly', 'since', 'six', 'slightly', 'so', 'some', 'somebody', 'somehow', 'someone', 'somethan', 'something', 'sometime', 'sometimes', 'somewhat', 'somewhere', 'soon', 'sorry', 'specifically', 'specified', 'specify', 'specifying', 'still', 'stop', 'strongly', 'sub', 'substantially', 'successfully', 'such', 'sufficiently', 'suggest', 'sup', 'sure   t', 'take', 'taken', 'taking', 'tell', 'tends', 'th', 'than', 'thank', 'thanks', 'thanx', 'that', 'thatll', 'thats', 'thatve', 'the', 'their', 'theirs', 'them', 'themselves', 'then', 'thence', 'there', 'thereafter', 'thereby', 'thered', 'therefore', 'therein', 'therell', 'thereof', 'therere', 'theres', 'thereto', 'thereupon', 'thereve', 'these', 'they', 'theyd', 'theyll', 'theyre', 'theyve', 'think', 'this', 'those', 'thou', 'though', 'thoughh', 'thousand', 'throug', 'through', 'throughout', 'thru', 'thus', 'til', 'tip', 'to', 'together', 'too', 'took', 'toward', 'towards', 'tried', 'tries', 'truly', 'try', 'trying', 'ts', 'twice', 'two', 'u', 'un', 'under', 'unfortunately', 'unless', 'unlike', 'unlikely', 'until', 'unto', 'up', 'upon', 'ups', 'us', 'use', 'used', 'useful', 'usefully', 'usefulness', 'uses', 'using', 'usually', 'v', 'value', 'various', 've', 'very', 'via', 'viz', 'vol', 'vols', 'vs', 'w', 'want', 'wants', 'was', 'wasnt', 'way', 'we', 'wed', 'welcome', 'well', 'went', 'were', 'werent', 'weve', 'what', 'whatever', 'whatll', 'whats', 'when', 'whence', 'whenever', 'where', 'whereafter', 'whereas', 'whereby', 'wherein', 'wheres', 'whereupon', 'wherever', 'whether', 'which', 'while', 'whim', 'whither', 'who', 'whod', 'whoever', 'whole', 'wholl', 'whom', 'whomever', 'whos', 'whose', 'why', 'widely', 'willing', 'wish', 'with', 'within', 'without', 'wont', 'words', 'world', 'would', 'wouldnt', 'www', 'x', 'y', 'yes', 'yet', 'you', 'youd', 'youll', 'your', 'youre', 'yours', 'yourself', 'yourselves', 'youve', 'z', 'zero']

################################### SCHEMAS #########################################
'''
CHECKIN POST SCHEMA:
{"uid":<uid>, "krumbs":<krumbs URI>, "loc_tags":<list of tags obtained from foursquare>}
'''

'''
POST PROCESS OF CHECKIN LOG:
{"uid":<uid>, "timestamp":timestamp, "loc":<lat,long string>, "category":<category> , "activity_tags":activity_tags, "emotion":emotion, "loc_tags":<list of tags obtained from foursquare>}
'''

'''
DB SCHEMA
{"_id":<mongodb_id>, "uid":<uid>, "tag":<tag>, "checkin_info":[info_1, info_2, ..., info_n]}
info_i = {'timestamp':checkin_log['timestamp'], 'loc':<lat,long string>, 'category':<category>, 'emotion':<emotion_score>, 'tag_type':<'a'|'l'>}
'''
####################################################################################

from flask import Flask, request, render_template
app = Flask(__name__)


@app.route('/checkin', methods=['POST'])
def checkin():
    checkin_log = json.loads(request.data)
    krumbs_json = parse_krumbs(checkin_log['krumbs'])
    checkin_log.update(krumbs_json)  # expand krumbs to fill in checkin_log
    if not load_to_db(checkin_log):
        return 'Internal Server Error', 500
    return 'OK', 200


@app.route('/recommend')
def recommend():
    uid = request.args.get('uid', None)
    loc = request.args.get('loc', None)
    if uid is None or loc is None:
        return 'Required args missing', 400
    loc = tuple(loc.split(','))
    keywords = get_top_k_tags_scores(uid)
    print 'Got top keywords ' + str(keywords[:5]) + ' ...'
    keywords = [t[0] for t in keywords]
    print 'Got related keywords'
    keywords.extend(get_related_keywords(keywords))
    eventful_results = get_eventful_results(keywords, loc)
    print 'Got recommendations from eventful'
    meetup_results = get_meetup_results(keywords, loc)
    print 'Got recommendations from meetup'
    trending_results = get_trending_results(loc, 10)
    print 'Got trending events'
    ordered_results = order_results(eventful_results, meetup_results, keywords)
    print 'Ordered events based on relevance'
    return json.dumps(ordered_results + trending_results)


def connect_db(database=MONGODB_DB):
    try:
        conn = pymongo.MongoClient(MONGODB_URI)
    except pymongo.errors.ConnectionFailure, e:
        print "Could not connect to MongoDB: %s" % e
    db = conn[database]
    db.authenticate(MONGODB_USER, MONGODB_PASS)
    return db

##################################################################################################################
###############################                  CHECK-IN                   ######################################
##################################################################################################################


def parse_krumbs(krumbs_url):
    # get krums json
    krumbs_response = urllib.urlopen(krumbs_url)
    krumbs_json = json.loads(krumbs_response.read())
    krumbs_json = krumbs_json['media'][0]  # assume that there is only one obj per call
    # when
    timestamp = krumbs_json['when']['end_time']
    timestamp = time.strptime(timestamp, '%Y-%m-%dT%H:%M:%S.%fZ')
    timestamp = cal.timegm(timestamp)  # get time epoch
    # where
    lat = str(krumbs_json['where']['geo_location']['latitude'])
    lon = str(krumbs_json['where']['geo_location']['longitude'])
    loc = ','.join([lat, lon])
    # what
    activity_tags = krumbs_json['caption'].lower().split()
    # category
    category = krumbs_json['why'][0]['intent_category_name']
    # emotion (tweaked why)
    reaction = krumbs_json['why'][0]['intent_name']
    emotion = EMOTION_MAP[category][reaction]
    # return a dict
    return {'timestamp':timestamp, 'loc':loc, 'activity_tags':activity_tags, 'category':category, 'emotion':emotion}


def load_to_db(checkin_log):
    checkin_info = build_checkin_info(checkin_log)
    # connect to db
    db = connect_db()
    table = db[COLL_NAME]

    # get all rows for this user
    uid = checkin_log['uid']
    rows = list(table.find({'uid': uid}))

    # if user not already present
    insert_docs = []
    update_docs = []
    if len(rows) == 0:
        insert_docs = create_new_user_docs(uid, checkin_info)
    else:
        # get list of docs for this user
        docs = list(table.find({'uid': uid}))
        # iterate over
        for tag in checkin_info.keys():
            existing_row = filter(lambda doc: doc['tag'] == tag, docs)
            # if tag not already present,
            if len(existing_row) == 0:
                insert_docs.append(create_new_doc(uid, tag, checkin_info))
            else:
                doc = existing_row[0]
                doc['checkin_info'].extend(checkin_info[tag])
                update_docs.append(doc)
    # ensure we have something to insert
    if len(insert_docs) == 0 and len(update_docs) == 0:
        print 'Error while loading to DB'
        return False
    # insert the newly created docs
    if len(insert_docs) > 0:
        table.insert_many(insert_docs)
    # update the existing docs
    if len(update_docs) > 0:
        bulk = table.initialize_unordered_bulk_op()
        for doc in update_docs:
            bulk.find({'_id':doc['_id']}).update({'$set':{'checkin_info':doc['checkin_info']}})
        bulk.execute()
    return True


def build_checkin_info(checkin_log):
    checkin_info = coll.defaultdict(list)
    d = {'timestamp':checkin_log['timestamp'], 'loc':checkin_log['loc'], 'category':checkin_log['category'], 'emotion':checkin_log['emotion']}
    for tag in checkin_log['activity_tags']:
        if tag.lower() in STOPWORDS:
            continue
        d_copy = d.copy()
        d_copy['tag_type'] = 'a'
        checkin_info[tag.lower()].append(d_copy)
    for tag in checkin_log['loc_tags']:
        tag = tag.lower().split()[0]
        if tag in STOPWORDS:
            continue
        d_copy = d.copy()
        d_copy['tag_type'] = 'l'
        checkin_info[tag].append(d_copy)
    return checkin_info


def create_new_user_docs(uid, checkin_info):
    return [create_new_doc(uid, tag, checkin_info) for tag in checkin_info]


def create_new_doc(uid, tag, checkin_info):
    return {'uid': uid, 'tag': tag, 'checkin_info': checkin_info[tag]}

##################################################################################################################
###############################                 RECOMMEND                   ######################################
##################################################################################################################


def get_top_k_tags_scores(uid):
    tag_scores = []
    # get all the docs for this user id
    db = connect_db()
    table = db[COLL_NAME]
    docs = table.find({'uid': uid})
    # iterate over each doc and calculate a score for the tag
    # create a list of tag,score pairs
    tag_scores = [ (doc['tag'], compute_score(doc['checkin_info'])) for doc in docs]
    # sort the list based on scores
    tag_scores = sorted(tag_scores, key=lambda pair: pair[1], reverse=True)
    return tag_scores


def compute_score(checkin_info):
    num_checkins = len(checkin_info)
    freq = 0
    decay_score = 0
    for checkin in checkin_info:
        freq += checkin['emotion']  # capture freq
        decay_score += compute_decay_score(checkin)  # capture decay score
    return INITIAL_SCORE * (FREQ_WEIGHT*freq + DECAY_WEIGHT*decay_score) / num_checkins


def compute_decay_score(checkin):
    # get delta T
    dt = (time.time()-checkin['timestamp'])/86400
    dt = dt if dt > 0.25 else 0  # ignore dt if less than quarter of a day
    # get the decay rate for category type
    l = DECAY_RATE[checkin['category']]
    return checkin['emotion'] * math.e ** (-l*dt)


def get_related_keywords(keywords):
    related_keywords = [lemma for keyword in keywords
                            for synset in wn.wordnet.synsets(keyword)
                            for hypernym in synset.hypernyms()
                            for lemma in hypernym.lemma_names()]
    return set(related_keywords)


def get_eventful_results(keywords, loc):
    keywords = '+%7C%7C+'.join(keywords)
    loc = ','.join(loc)
    get_req = 'http://api.eventful.com/json/events/search?date=Today&within=25' + \
                '&keywords=' + keywords + '&where=' + loc + \
                '&app_key=' + EVENTFUL_KEY
    resp = requests.get(get_req).json()
    if int(resp['total_items']) == 0:
        return []
    events = resp['events']['event']
    if int(resp['total_items']) == 1:
        events = [events]
    ret = [ {'title' : e['title'], 'desc' : html2text.html2text(e['description'] or 'There is no description for this event'), 'url' : e['url'] } for e in events ]
    return ret


def get_meetup_results(keywords, loc):
    keywords = ','.join(keywords)
    lat, lon = loc
    get_req = 'https://api.meetup.com/2/open_events?&sign=true&photo-host=public' + \
                '&time=,1w&radius=25&page=20' + \
                '&text='+ keywords + '&lat=' + lat + '&lon=' + lon + \
                '&key=' + MEETUP_KEY
    resp = requests.get(get_req).json()
    events = resp['results']
    ret = [ {'title' : e['name'], 'desc' : html2text.html2text(e['description'] or 'There is no description for this event'), 'url' : e['event_url'] } for e in events ]
    return ret

def get_trending_results(loc, num):
    lat,lon = loc
    get_req = 'https://api.meetup.com/2/open_events?&sign=true&photo-host=public' + \
                '&time=,1w&radius=50&page=' + str(num) + \
                '&order=trending' + '&lat=' + lat + '&lon=' + lon + \
                '&key=' + MEETUP_KEY
    resp = requests.get(get_req).json()
    events = resp['results']
    ret = [ {'title' : e['name'], 'desc' : html2text.html2text(e['description'] or 'There is no description for this event'), 'url' : e['event_url'] } for e in events ]
    return ret

def order_results(eventful_results, meetup_results, keywords):
    bucket1, bucket2, bucket3, bucket4 = [], [], [], []
    for keyword in keywords:
        for res in eventful_results:
            if keyword in res['title'].lower():
                bucket1.append(res)
            else:
                bucket3.append(res)
    for keyword in keywords:
        for res in meetup_results:
            if keyword in res['title'].lower():
                bucket2.append(res)
            else:
                bucket4.append(res)
    return bucket1 + bucket2 + bucket3 + bucket4

if __name__ == '__main__':
    app.run(debug=True)

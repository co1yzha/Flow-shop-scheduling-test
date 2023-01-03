import logging
import pandas as pd
import json
from pymongo import MongoClient, errors
import configparser

config = configparser.ConfigParser()
config.read('./config.ini')
db_config = config['MongoDB']
# config.options('MongoDB')

def connectDB(dbName):
    '''
    db = connect(dbName)
    :param dbName: Database Name
    :return: db
    https://www.mongodb.com/docs/drivers/pymongo/
    '''

    atlas = db_config.getboolean('atlas')
    url = db_config.get('url')
    username = db_config.get('username')
    password = db_config.get('password')
    if not atlas:
        # username = 'databaseUser'
        # password = 'V3C1234!'
        # url = "vec-sim-005"
        port = db_config.get('port')
        # client = MongoClient(url, port, username='databaseUser', password='V3C1234!', maxPoolSize=50)
        client = MongoClient(url, port, username=username, password=password, maxPoolSize=50)
    else:
        # username = 'user'
        # password = 'ecosystem2'
        # url = 'cluster0.up4hqgc.mongodb.net'
        conn_str = f"mongodb+srv://{username}:{password}@{url}/test?retryWrites=true&w=majority"
        client = MongoClient(conn_str, serverSelectionTimeoutMS=5000)

    db = client[dbName]
    return db


# test

def getCollection(collectionName, dbName):
    """
    df = getCollection(collectionName, dbName)
    :param collectionName: collectionName
    :param dbName: database Name
    :return: df
    """
    db = connectDB(dbName)
    collection = db[collectionName]
    cursor = collection.find({})
    df = pd.DataFrame(list(cursor))
    if 'no_id' and '_id' in df:
        del df['_id']
    return df


def getQuery(myquery, collectionName, dbName, **kwargs):
    """
    df = getQuery(myquery, collectionName, dbName)
    :param myquery: query (i.e. myquery = {"collected_at": {"$lt": 20220722}})
    :param (str) collectionName: collectionName
    :param (str) dbName: database Name

    :return: df
    """
    db = connectDB(dbName)
    collection = db[collectionName]
    if len(kwargs) == 0:
        cursor = collection.find(myquery)
        df = pd.DataFrame(list(cursor))
    else:
        fields = kwargs['fields']
        cursor = collection.find(myquery, {i:1 for i in fields})
        df = pd.DataFrame(list(cursor))
    if 'no_id' and '_id' in df:
        del df['_id']
    return df



def insertCollection(mylist, collectionName, dbName):
    """
    createCollection(mylist = df.to_dict('records'), collectionName, dbName):
    mylist -> dictionary
    mylist = [{ "name": "Amy", "address": "Apple st 652"},
            { "name": "Hannah", "address": "Mountain 21"},
            { "name": "Michael", "address": "Valley 345"}]
        -> mylist = df.to_dict('records')
    check up more at https://www.w3schools.com/python/python_mongodb_getstarted.asp
    """
    db = connectDB(dbName)
    collection = db[collectionName]
    x = collection.insert_many(mylist)
    print(f'Collection [{collectionName}] created/Insert')



def dropCollection(collectionName, dbName):
    db = connectDB(dbName)
    collection = db[collectionName]
    collection.drop()
    print(f'Collection [{collectionName}] dropped')



def dropDocument(myquery, collectionName, dbName):
    db = connectDB(dbName)
    collection = db[collectionName]
    x = collection.delete_many(myquery)
    print(x.deleted_count, "documents deleted")


#
# def watchCollection(collectionName, dbName):
#     db = connectDB(dbName)
#     collection = db[collectionName]
#
#     option = {'full_document': 'updateLookup'}
#
#     change_stream = collection.watch([{"$match": {"operationType": "update"}}], **option)
#     for change in change_stream:
#         print(json.dumps(change))
#         print('')
#
#     try:
#         resume_token = None
#         pipeline = [{'$match': {'operationType': 'update'}}]
#         with collection.watch(pipeline) as stream:
#             for update_change in stream:
#                 print(update_change)
#                 resume_token = stream.resume_token
#     except errors.PyMongoError:
#         if resume_token is None:
#             logging.error('resume_token is missing')
#         else:
#             with collection.watch(pipeline, resume_after=resume_token) as stream:
#                 for update_change in stream:
#                     print(update_change)
#
#
#
#
# def getToken(keyType):
#     # token = getToken(keyType = 'mapbox'/'googleMap'
#     with open('../assets/token.json', 'r') as f:
#         data = json.loads(f.read())
#     return data[keyType]
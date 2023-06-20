from datetime import datetime, timedelta

import pendulum
import pymongo

from app_configs.mongo import ALLOW_DISK_USE, CREDENTIAL_MONGO, DB_PORT_MONGO, DB_HOST_MONGO, DBNAME_MONGO, \
    COLLECTION_NAME_SCRAPED_DATA


class MongoDBConnector():

    def __init__(self, credential, host, port):
        self.credential = credential
        self.host = host
        self.port = port

    def connect(self, dbname):
        self.dbname=dbname
        self.client = pymongo.MongoClient(
            f'mongodb://{self.credential["username"]}:{self.credential["password"]}@{self.host}:{self.port}/admin?authSource=admin')
        self.connection = self.client[self.dbname]
        return self.connection

    def save_data(self, collection_name, data):
        x = self.connection[collection_name].insert_one(data)
        return x.inserted_id
    def update_multiple_data(self, collection_name, query, data):
        x = self.connection[collection_name].update_many(query, data, upsert=True)
        return {
            'acknowledged' : x.acknowledged,
            'matchedCount' : x.matched_count,
            'modifiedCount' : x.modified_count}

    def update_single_data(self, collection_name, query, data):
        x = self.connection[collection_name].update_one(query, data, upsert=True)
        return x.upserted_id

    def remove_single_data(self, collection_name, where):
        x = self.connection[collection_name].delete_one(where)
        return x.raw_result

    def remove_multiple_data(self, collection_name, where):
        x = self.connection[collection_name].delete_many(where)
        return x.raw_result

    def remove_collection(self, collection_name):
        mycol = self.connection[collection_name]
        return mycol.drop()

    def get_count(self, collection_name, query=None):
        mycol = self.connection[collection_name]
        query = {**{'$count': 'count'}, **query}

        if query:
            data = list(
                mycol.aggregate(
                    [query], allowDiskUse=ALLOW_DISK_USE
                )
            )
            return data
        else:
            data = list(
                mycol.aggregate(
                    [{'$count': 'count'}], allowDiskUse=ALLOW_DISK_USE
                )
            )
            return data

    def get_data_count(self, collection_name, query=None, limit=None):
        mycol = self.connection[collection_name]

        if query:
            if limit:
                limit = int(limit)
                data = list(
                    mycol.aggregate(
                        query, allowDiskUse=ALLOW_DISK_USE
                    ).limit(limit)
                )
            else:
                data = list(
                    mycol.aggregate(
                        query, allowDiskUse=ALLOW_DISK_USE
                    )
                )
        else:
            if limit:
                limit = int(limit)
                data = list(
                    mycol.aggregate(
                        allowDiskUse=ALLOW_DISK_USE
                    ).limit(limit)
                )
            else:
                data = list(
                    mycol.aggregate(
                        [{ '$count': 'count' }] , allowDiskUse=ALLOW_DISK_USE
                    )
                )

        return data

    def get_unique_values_of_column(self, collection_name, column):
        mycol = self.connection[collection_name]
        values = mycol.find({}).distinct(column)
        return values

    def get_aggregated_data(self, collection_name, pipeline):
        mycol = self.connection[collection_name]
        data = list(mycol.aggregate(pipeline , allowDiskUse=ALLOW_DISK_USE))
        return data

    def get_single_data(self, collection_name, where):
        mycol = self.connection[collection_name]
        data = list(mycol.find(where, {}))
        return data

    def get_data(self, collection_name, columns=None, query=None, limit=None, skip=0, sort_by={}):
        if sort_by:
            sorted_for = []
            for key in sort_by:
                sorted_for.append((key, sort_by[key]))
        else:
            sorted_for = [('posted_at',-1)]
        mycol = self.connection[collection_name]
        if columns:
            if query:
                if limit:
                    limit = int(limit)
                    data = list(
                        mycol.find(
                            query, columns).limit(limit).sort(sorted_for).allow_disk_use(ALLOW_DISK_USE)
                    )
                else:
                    data = list(
                        mycol.find(
                            query, columns).sort(sorted_for).allow_disk_use(ALLOW_DISK_USE)
                    )
            else:
                if limit:
                    limit = int(limit)
                    data = list(mycol.find(
                        query, columns).limit(limit).sort(sorted_for).allow_disk_use(ALLOW_DISK_USE)
                                )
                else:
                    data = list(
                        mycol.find({}, columns).sort(sorted_for).allow_disk_use(ALLOW_DISK_USE)
                    )
        else:
            if query:
                if limit:
                    limit = int(limit)
                    data = list(
                        mycol.find(query).limit(limit).sort(sorted_for).allow_disk_use(ALLOW_DISK_USE)
                    )
                else:
                    data = list(
                        mycol.find(query).sort(sorted_for).allow_disk_use(ALLOW_DISK_USE)
                    )
            else:
                if limit:
                    limit = int(limit)
                    data = list(
                        mycol.find().limit(limit).skip(skip).sort(sorted_for).allow_disk_use(ALLOW_DISK_USE)
                    )
                else:
                    data = list(
                        mycol.find().sort(sorted_for).allow_disk_use(ALLOW_DISK_USE)
                    )

        return data

class DataRemover():
    db_connector = MongoDBConnector(CREDENTIAL_MONGO, DB_HOST_MONGO, DB_PORT_MONGO)
    db_connector.connect(DBNAME_MONGO)

    def remove_single_data(self,collection_name, where):
        return self.db_connector.remove_single_data(collection_name, where)

    def remove_multiple_data(self,collection_name, where):
        return self.db_connector.remove_multiple_data(collection_name, where)

    def remove_collection(self, collection_name):
        return self.db_connector.remove_collection(collection_name)

class DataWriter():

    db_connector = MongoDBConnector(CREDENTIAL_MONGO, DB_HOST_MONGO, DB_PORT_MONGO)
    db_connector.connect(DBNAME_MONGO)

    def update_data_to_collection(self, collection, query, data):
        return self.db_connector.update_single_data(collection, query, data)

    def save_data_to_collection(self, collection, data):
        return self.db_connector.save_data(collection, data)

class DataReader():

    db_connector = MongoDBConnector(CREDENTIAL_MONGO, DB_HOST_MONGO, DB_PORT_MONGO)
    db_connector.connect(DBNAME_MONGO)
    def get_scraped_url(self,day):

        query = {}
        now = pendulum.now().in_timezone('UTC')
        query['scraped_at'] = {'$lte': now,
                              '$gte': now.subtract(days=day)}
        existing_posts_url = self.db_connector.get_data(COLLECTION_NAME_SCRAPED_DATA, query=query,columns=['post_url'])
        existing_posts_url = [i['post_url'] for i in existing_posts_url]
        return existing_posts_url
    def get_unique_values_of_column(self, column):
        return self.db_connector.get_unique_values_of_column(COLLECTION_NAME_SCRAPED_DATA, column)

    def get_recent_post_count_from_date(self,date, recent_days):
        query_list = []
        date = datetime.strptime(date, '%Y-%m-%d')
        recent = (date - timedelta(days=int(recent_days))).date()
        query_list.append(
            {'$match': {'posted_at': {'$lte': datetime.strptime(f'{recent} 23:59:59', '%Y-%m-%d %H:%M:%S'),
                                      '$gte': datetime.strptime(f'{recent} 00:00:00', '%Y-%m-%d %H:%M:%S')}}}
        )
        query_list.append(
            {'$group': {'_id': None,
                        'count': {'$sum': 1}}}
        )
        counts = self.db_connector.get_data_count(COLLECTION_NAME_SCRAPED_DATA, query=query_list)
        return counts

import pymongo


class DataBase() :
    def __init__(self, DB_url, DB_name, DB_col):
        self.DB_url = DB_url
        self.DB_name = DB_name
        self.DB_col = DB_col
        self.DB = None


    def connect(self):
        mongo = pymongo.MongoClient(self.DB_url)

        DB_list = mongo.list_database_names()
        if not self.DB_name in DB_list:
            print('DataBase not exists, create new one')

        dataBase = mongo[self.DB_name]
        self.DB = dataBase[self.DB_col]
        return True


    def find(self, query):
        resData = self.DB.find_one(query)

        if resData == None:
            return False
        else:
            return resData


    def insertOne(self, data):
        self.DB.insert_one(data)
        return True
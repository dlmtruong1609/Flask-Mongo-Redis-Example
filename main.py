from flask import Flask, request
from flask_pymongo import PyMongo
from flask_redis import Redis
import json
app = Flask(__name__)
app.config["MONGO_URI"] = "mongodb://my_mongo:27017/demo"
app.config['REDIS_URL'] = 'redis://my_redis:6379/1'

mongo = PyMongo(app)
redis = Redis(app, 'REDIS')

@app.route('/')
def hello_world():
    return 'Hello, World! aloalo 123'
 
@app.route('/init_db')
def ini_db():
    for i in range(10):
        mongo.db.sample.insert({'name': f'value with index {i + 1} | 👍'})
    return {"msg": "init data success"}

@app.route('/sample')
def get_sample():
    res = []
    for r in mongo.db.sample.find({}):
        res.append({
            "id": str(r['_id']),
            "name": r["name"]
        })
    return {
        "err_code": 0,
        "msg": "success",
        "mongo": res
    }
        

def set_redis(list_data):
    redis.set('list', json.dumps(list_data))
    print("Redis is saved")

def get_redis():
    # redis.delete('list')
    # print(redis.get("list") is None, flush=True)

    if redis.get("list") is None:
        res = redis.get('list') #key redis khong ton tai
    else:
        res = json.loads(redis.get("list")) #key co ton tai va value convert sang json
    return {
        "err_code": 0,
        "msg": "success",
        "redis": res
    }


@app.route('/data')
def get_data():
    if get_redis()['redis'] is None :
        set_redis(get_sample()["mongo"])
        print("get data from mongo", flush=True)
        return get_sample()
    else:
        print("get data from redis", flush=True)
        return get_redis()

if __name__ == '__main__':
    app.run(port=5000, host="0.0.0.0", debug=True)
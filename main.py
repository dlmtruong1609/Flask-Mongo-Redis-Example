from flask import Flask, request
from flask_pymongo import PyMongo
from flask_redis import Redis
import json
from flask_caching import Cache


config = {
    "DEBUG": True,          # some Flask specific configs
    "CACHE_TYPE": "simple", # Flask-Caching related configs
    "CACHE_DEFAULT_TIMEOUT": 300
}
app = Flask(__name__)
app.config.from_mapping(config)
app.config["MONGO_URI"] = "mongodb://my_mongo:27017/demo"
app.config['REDIS_URL'] = 'redis://my_redis:6379/1'
cache = Cache(app)


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
    set_data_from_cache(list_data) #set data khi cache ko co data
    print("Redis is saved", flush=True)

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

def get_data_from_cache():
    # cache.clear()
    # print(cache.get("list"), flush=True)
    res = cache.get("list")
    return {
        "err_code": 0,
        "msg": "success",
        "cache": res
    }

def set_data_from_cache(list_data):
    cache.set("list", list_data)

@app.route('/data')
def get_data():
    if get_data_from_cache()['cache'] is not None:
        print("get data from cache", flush=True)
        return get_data_from_cache()
    elif get_redis()['redis'] is None :
        set_redis(get_sample()["mongo"]) #set data khi redis ko co data
        print("get data from mongo", flush=True)
        return get_sample()
    else:
        print("get data from redis", flush=True)
        set_data_from_cache(get_redis()["redis"]) #set data khi cache ko co data
        return get_redis()

if __name__ == '__main__':
    app.run(port=5000, host="0.0.0.0", debug=True)
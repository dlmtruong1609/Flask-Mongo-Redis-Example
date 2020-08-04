from flask import Flask, request
from flask_pymongo import PyMongo
from flask_redis import Redis
import json
from flask_caching import Cache
from functools import wraps


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

def response(msg):     
    def response_decorator(func):
        @wraps(func)
        def response_wrap():
            return {
                "msg": msg,
                "data": func()
            }
        return response_wrap
    return response_decorator
 
@app.route('/init_db')
def ini_db():
    for i in range(10):
        mongo.db.sample.insert({'name': f'value with index {i + 1} | 👍'})
    return {"msg": "init data success"}

@app.route('/sample')
@response(msg = "Get data from mongo")
def get_sample():
    res = []
    for r in mongo.db.sample.find({}):
        r['_id'] = str(r['_id'])
        res.append(r)
    return res


def set_data(db, data):
    db.set("list", json.dumps(data))

@response(msg = "Get data from redis")
def get_data_from_redis():
    # redis.delete('list')
    # print(json.loads(redis.get('list')), flush=True)

    try:
        res = json.loads(redis.get('list'))
    except:
        res = redis.get('list')
    return res

@response(msg = "Get data from cache")
def get_data_from_cache():
    # cache.clear()
    # print(cache.get("list"), flush=True)
    # res = cache.get("list")
    try:
        res = json.loads(cache.get("list"))
    except:
        res = cache.get("list")
    return res

@app.route('/data')
def get_data():
    if get_data_from_cache()['data'] is not None:
        return get_data_from_cache()

    if get_data_from_redis()['data'] is not None:
        set_data(cache, get_sample()["data"]) #set data khi cache ko co data
        return get_data_from_redis()
    
    if get_data_from_redis()['data'] is None :
        set_data(redis, get_sample()["data"]) #set data khi redis ko co data
        return get_sample()

if __name__ == '__main__':
    app.run(port=5000, host="0.0.0.0", debug=True)
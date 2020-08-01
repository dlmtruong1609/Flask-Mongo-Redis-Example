from flask import Flask, request
from flask_pymongo import PyMongo
from flask_redis import Redis
from flask import jsonify

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
        "msg": "success", 
        "res": res
    }
        
@app.route('/redis', methods=['POST'])
def set_redis_api():
    """
    TODO: Set key:value to redis with TTL
    @payload: json:
        - key (string): key for set
        - val (string): value for set
        - ttl ? int: 
    """
    payload = request.json
    print(payload, flush=True)
    redis.setex(
        payload['key'], 
        payload['ttl'], 
        payload['val']
    )

    print(payload, flush=True)

    return payload

def set_redis(list_data):
    redis.setex(list_data)
    print("Redis is saved")

@app.route('/redis/<key>')
def get_redis(key):
    val = redis.get(key)
    print(val, flush=True)
    # print(val)
    return {"key": key, "val": val}
@app.route('/data')
def get_data():
    args = request.args
    if get_redis(args["key"])["val"] is None :
        set_redis(get_sample()["res"])
        print("get data from mongo", flush=True)
        return get_sample()
    else:
        print("get data from redis", flush=True)
        return get_redis(args["key"])

if __name__ == '__main__':
    app.run(port=5000, host="0.0.0.0", debug=True)
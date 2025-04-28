from fastapi import FastAPI, HTTPException
import redis
import time

app = FastAPI()

redis_client = redis.Redis(host='localhost', port=6379, db=0)

def get_expensive_data_from_db():
    time.sleep(3)
    return {'data': 'Это очень тяжелые данные из базы'}


@app.get('/get_data')
def get_data():
    cached_data = redis_client.get('expensive_data')

    if cached_data:
        return{
            'data': cached_data.decode('utf-8'),
            'source': 'кеш (Redis)'
        }

    db_data = get_expensive_data_from_db()
    redis_client.setex('expensive_data', 30, db_data['data'])

    return {
        'data': db_data['data'],
        'source': 'база данных'
    }
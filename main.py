import os

from flask import Flask, jsonify  # make_response, request, url_for

from redis import Redis

from rq import Queue

from utils import create_task_id


app = Flask(__name__)
app.config["DEBUG"] = True
app.config["REDIS_URL"] = os.environ.get('REDIS_URL') or 'redis://'
app.redis = Redis.from_url(app.config['REDIS_URL'])
app.task_queue = Queue('parsing-tasks', connection=app.redis)
tasks = {}


@app.route('/api/<string:url>', methods=['POST'])
def create_task(url: str) -> str:
    tid = create_task_id(url)
    job = app.task_queue.enqueue('tasks.parse', tid, url)
    tasks[tid] = job
    return jsonify({"id": tid})


@app.route('/api/<string:tid>', methods=['GET'])
def get_task_status(tid: str) -> str:
    if tid not in tasks:
        return jsonify({"status": "Not started"})
    job = tasks[tid]
    job.refresh()
    return jsonify(job.meta)


app.run(host='0.0.0.0', port=15555)

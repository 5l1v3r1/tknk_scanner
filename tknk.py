#!/usr/bin/env python3
from rq import Queue
import json, subprocess, requests, time, shutil, magic, os, uuid, math, redis
from pathlib import Path
from pymongo import MongoClient
from flask import Flask, jsonify, request, url_for, abort, Response, make_response
from redis import Redis
from xmlrpc_client import analyze

with open("tknk.conf", 'r') as f:
    tknk_conf = json.load(f)

VM_NAME=tknk_conf['vm_name']
UPLOAD_FOLDER="target/" 

app = Flask(__name__)

@app.route('/analyze', methods=['POST'])
def start_analyze():
    if 'application/json' not in request.headers['Content-Type']:
        print(request.headers['Content-Type'])
        return jsonify(status_code=2, message="Content-Type Error.")

    json_data = request.json

    uid = str(uuid.uuid4())
    post = {"UUID":uid}

    collection.insert_one(post)

    json_data['target_file']=json_data['path'].split("/")[1]
    print(json.dumps(json_data, indent=4))
    r.set(uid, json_data)

    job = q.enqueue(analyze, uid, job_id=uid, timeout=json_data['time']+600)

    return jsonify(status_code=0, UUID=uid, message="Submission Success!")

@app.route('/upload', methods=['POST'])
def file_upload():
    f = request.files['file']
    filename = (f.filename)
    f.save(os.path.join(UPLOAD_FOLDER, filename))

    file_type = magic.from_file("target/"+filename)

    if ("DLL" in file_type) or (("PE32" or"PE32+") not in file_type):
            print("Invalid File Format!! Only PE Format File(none dll).")
            return make_response(jsonify(status_code=2, message="Invalid File Format!! Only PE Format File(none dll)."), 400)

    if (("PE32" or "PE32+") in file_type):
        path = Path("target/"+filename)
        if path.suffix != "exe":
            os.rename("target/"+path.name, "target/"+path.stem+".exe")
            filename=path.stem+".exe"

    return jsonify(status_code=0, path=UPLOAD_FOLDER+filename)

@app.route('/results/<uuid>')
def show_result(uuid=None):

    result = list(collection.find({u"UUID":uuid}))[0]
    result.pop('_id')
    
    if "scans" in result:
        return jsonify(status_code=0, result=result)
    else:
        return make_response(jsonify(status_code=1, message='Analysing.'), 206)
        
@app.route('/yara/<rule_name>')
def get_yara_file(rule_name=None):

    rule_name_check = rule_name.replace("_", "")
    if rule_name_check.isalnum() == False:
        return make_response(jsonify(status_code=2, message="Invalid rule_name"), 400)
 
    cmd=[("find yara/ -type f | xargs grep -l -x -E -e " + "\"rule "+ rule_name +" .*{\" -e \"rule "+ rule_name +"{\" -e \"rule " + rule_name + "\"")]
    p = (subprocess.Popen(cmd, shell=True, stdin=None, stdout=subprocess.PIPE, close_fds=True))
    output = p.stdout.read().decode('utf-8')

    with open(output.strip(), 'r') as f:
        yara_file=f.read()

    return jsonify(status_code=0, result=yara_file)

@app.route('/page/<page_num>')
def page(page_num=None):
    page=[]
    page_num = int(page_num)
    page_size= math.floor(len(list(collection.find()))/50)+1
    page_item = collection.find().sort('timestamp',-1).limit(50).skip((page_num-1)*50)
    for p in page_item:
        p.pop('_id')
        page.append(p)
    return jsonify(status_code=0, page=page, page_size=page_size)

@app.route('/jobs')
def job_ids():
    redis_conn = Redis()
    q = Queue(connection=redis_conn)# Getting the number of jobs in the queue
    print(len(q))# Retrieving jobs
    queued_job_ids = q.job_ids # Gets a list of job IDs from the queue
    return jsonify(status_code=0, job_ids=queued_job_ids)

@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify(status_code=2, message='Not found.'), 404)

if __name__ == '__main__':
    client = MongoClient('localhost', 27017)
    db = client.scan_database
    collection = db.scan_collection

    pool =  redis.ConnectionPool(host='localhost', port=6379, db=0)
    r = redis.StrictRedis(connection_pool=pool)

    # Tell RQ what Redis connection to use
    redis_conn = Redis(host='localhost', port=6379)
    q = Queue(connection=redis_conn)  # no args implies the default queue

    app.run(host='0.0.0.0', port=8000)
    

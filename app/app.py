from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_pymongo import PyMongo
from bson.objectid import ObjectId
from prometheus_client import Counter, Histogram, Gauge, generate_latest
import os
import logging
from time import time

app = Flask(__name__)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app.config['MONGO_URI'] = os.getenv("MONGO_URI")
app.secret_key = 'e9c7e5c4b3a2f7d1e9a8c1b4f5d6e7f8'
logger.info(f"MONGO_URI: {app.config['MONGO_URI']}")
mongo = PyMongo(app)


# Prometheus metrics
events_created = Counter('events_created_total', 'Total number of events created')
events_updated = Counter('events_updated_total', 'Total number of events updated')
events_deleted = Counter('events_deleted_total', 'Total number of events deleted')
http_request_duration_seconds = Histogram('http_request_duration_seconds', 'HTTP request duration in seconds', ['method', 'endpoint'])
http_requests_total = Counter('http_requests_total', 'Total HTTP Requests', ['method', 'endpoint', 'status'])
active_requests = Gauge('active_requests', 'Number of active requests')
event_count = Gauge('event_count', 'Total number of events in the database')

@app.before_request
def before_request():
    request.start_time = time()
    active_requests.inc()

@app.after_request
def after_request(response):
    request_duration = time() - request.start_time
    http_request_duration_seconds.labels(method=request.method, endpoint=request.path).observe(request_duration)
    http_requests_total.labels(method=request.method, endpoint=request.path, status=response.status_code).inc()
    active_requests.dec()
    logger.info(f"Request to {request.path} took {request_duration:.2f} seconds")
    return response

@app.route('/')
def index():
    logger.info("Accessing index page")
    events = mongo.db.events.find()
    event_count.set(mongo.db.events.count_documents({}))
    return render_template('index.html', events=events)

@app.route('/event/create', methods=['GET', 'POST'])
def create_event():
    if request.method == 'POST':
        name = request.form['name']
        date = request.form['date']
        location = request.form['location']
        description = request.form['description']

        new_event = {
            'name': name,
            'date': date,
            'location': location,
            'description': description
        }
        result = mongo.db.events.insert_one(new_event)
        events_created.inc()
        event_count.inc()
        logger.info(f"Event created: {name}")

        if request.headers.get('Accept') == 'application/json':
            return jsonify({
                "message": "Event created successfully!",
                "id": str(result.inserted_id)
            }), 200
        else:
            flash('Event created successfully!', 'success')
            return redirect(url_for('view_events'))

    logger.info("Accessing create event page")
    return render_template('create_event.html')

@app.route('/events')
def view_events():
    logger.info("Viewing all events")
    events = mongo.db.events.find()
    return render_template('view_events.html', events=events)

@app.route('/event/edit/<id>', methods=['GET', 'POST'])
def edit_event(id):
    event = mongo.db.events.find_one_or_404({'_id': ObjectId(id)})

    if request.method == 'POST':
        updated_data = {
            'name': request.form['name'],
            'date': request.form['date'],
            'location': request.form['location'],
            'description': request.form['description']
        }

        mongo.db.events.update_one({'_id': ObjectId(id)}, {'$set': updated_data})
        events_updated.inc()
        logger.info(f"Event updated: {updated_data['name']}")

        if request.headers.get('Accept') == 'application/json':
            return jsonify({
                "message": "Event updated successfully!",
                "event": {**updated_data, "id": str(id)}
            }), 200
        else:
            flash('Event updated successfully!', 'success')
            return redirect(url_for('view_events'))

    logger.info(f"Accessing edit page for event: {event['name']}")
    if request.headers.get('Accept') == 'application/json':
        return jsonify({
            "id": str(event['_id']),
            "name": event['name'],
            "date": event['date'],
            "location": event['location'],
            "description": event.get('description', '')
        }), 200
    else:
        return render_template('edit_event.html', event=event)

@app.route('/event/<id>', methods=['GET'])
def get_event(id):
    event = mongo.db.events.find_one_or_404({'_id': ObjectId(id)})
    logger.info(f"Retrieved event: {event['name']}")
    return jsonify({
        'id': str(event['_id']),
        'name': event['name'],
        'date': event['date'],
        'location': event['location'],
        'description': event['description']
    })

@app.route('/event/<id>', methods=['PUT'])
def update_event(id):
    data = request.json
    mongo.db.events.update_one(
        {'_id': ObjectId(id)},
        {'$set': {
            'name': data['name'],
            'date': data['date'],
            'location': data['location'],
            'description': data.get('description', "")
        }}
    )
    events_updated.inc()
    logger.info(f"Event updated via API: {data['name']}")
    return jsonify({"message": "Event updated successfully!"}), 200

@app.route('/event/delete/<id>', methods=['POST'])
def delete_event(id):
    event = mongo.db.events.find_one_or_404({'_id': ObjectId(id)})
    mongo.db.events.delete_one({'_id': ObjectId(id)})
    events_deleted.inc()
    event_count.dec()
    logger.info(f"Event deleted: {event['name']}")

    if request.headers.get('Accept') == 'application/json':
        return jsonify({"message": "Event deleted successfully!"}), 200
    else:
        flash('Event deleted successfully!', 'success')
        return redirect(url_for('view_events'))

@app.route('/metrics')
def metrics():
    logger.info("Metrics endpoint accessed")
    return generate_latest()

if __name__ == '__main__':
    app.run(host='0.0.0.0')
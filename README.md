# Event Planner Application

This is a web-based Event Planner application built with Flask and MongoDB. It allows users to create, view, edit, and delete events.

## Features

- Create new events with name, date, location, and description
- View a list of all events
- View details of a specific event
- Edit existing events
- Delete events
- RESTful API endpoints for programmatic access
- Prometheus metrics for monitoring

## Tech Stack

- Backend: Python with Flask
- Database: MongoDB
- Frontend: HTML templates with Jinja2
- Containerization: Docker
- Orchestration: Docker Compose
- Monitoring: Prometheus metrics

## Prerequisites

- Docker and Docker Compose
- Python 3.8 or higher (for local development)

## Setup and Running

1. Clone the repository:
   ```
   git clone <repository-url>
   cd <repository-directory>
   ```

2. Build and run the application using Docker Compose:
   ```
   docker-compose up --build
   ```

3. Access the application:
   - Web Interface: Open a browser and navigate to `http://localhost`
   - API: Send requests to `http://localhost:5000`

## API Endpoints

- `GET /`: Home page
- `GET /events`: List all events
- `POST /event/create`: Create a new event
- `GET /event/<id>`: Get details of a specific event
- `PUT /event/<id>`: Update an event
- `POST /event/delete/<id>`: Delete an event
- `GET /metrics`: Prometheus metrics

## Development

To run the application locally for development:

1. Create a virtual environment:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   ```

2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

3. Set up environment variables:
   ```
   export FLASK_APP=app/app.py
   export FLASK_ENV=development
   export MONGO_URI=mongodb://localhost:27017/event_db
   ```

4. Run the Flask application:
   ```
   flask run
   ```

## Testing

To run the end-to-end tests:

```
./e2e_test.sh localhost
```

Ensure that the application is running before executing the tests.

## Deployment

This application is designed to be deployed using Docker and can be easily integrated into various container orchestration platforms like Kubernetes or Amazon ECS.

## Monitoring

The application exposes Prometheus metrics at the `/metrics` endpoint. You can configure a Prometheus server to scrape these metrics for monitoring.

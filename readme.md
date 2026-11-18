## Task Tracker API v1 ##

This project is my backend project for BE 106 where a user can track commissions that they can create, edit and delete.

## Setup ##

1. How to clone it:

The repo can be cloned through github under the url: https://github.com/FoodofPluto/task_tracker_API.git

The repo clone commands are:

git clone https://github.com/FoodofPluto/task_tracker_API.git
cd task_tracker_API

2. How to create/activate a virtualenv

For Windows: create and activate a virtualenv through Powershell. The command for creating a virtual environment in Powershell is "python -m venv venv". Once the virtual environment is created, input into powershell ".\venv\Scripts\Activate" to activate the virtual environment, symbolized by seeing (venv) in green as the first section of powershell input.

3. How to install dependencies from requirements.txt

To install all dependencies listed in a requirements.txt file, open your terminal or command prompt and run pip install -r requirements.txt. Make sure your terminal is currently pointing to the project folder where the file is saved.


4. How to run the app 

To run the app from Powershell, input "flask run" while the virtual environment is activated.

## Environment Variables ##

1. Create a .env file based on .env.example

Use the following .env variables: 

DATABASE_URL – points to the dev SQLite database.
JWT_SECRET – secret key for signing JWTs

For example:

DATABASE_URL=sqlite:///dev.db
JWT_SECRET=some-dev-secret

**REMEMBER**: Do not commit your .env file; it’s ignored by Git.

## Migration ##

This project uses Flask-Migrate / Alembic.

Here are commands to initiate and update migrations for the app:

flask db init (only first time, if not already initialized)
flask db migrate -m "message"
flask db upgrade






Path	Method	Purpose	Visibility	Success	Errors (400/401/403/404)
/auth/register	POST		public	201 Created	400
/auth/login	POST		public	200 OK	400, 401
/profile	GET		logged-in only	200 OK	401, 403, 404
/profile	PUT		logged-in only	200 OK	400, 401, 403
/commissions	POST		logged-in only	201 Created	400, 401, 403
/profile/commissions	GET		logged-in only	200 OK	401, 403
/commissions/int:id	GET		logged-in only	200 OK	401, 403, 404
/commissions/int:id	PATCH		logged-in only	200 OK	400, 401, 403, 404
/commissions/int:id	DELETE		logged-in only	204 No Content	400, 401, 403, 404


Task Tracker API – backend project in progress (branching lesson)









GET /events: return a filtered list of all available events.	200 OK (Returns a list of event objects)	400 Bad Request (Invalid filter or pagination query parameters)
POST /events:	create a new event with capacity, date, and location details.	201 Created (Returns the newly created event and Location header)	400 Bad Request (Malformed JSON or missing fields), 401 Unauthorized (Not logged in), 403 Forbidden (Lacks organizer permissions), 422 Unprocessable Entity (Validation errors, such as a past event date or negative capacity)
GET /events/<id>:	retrieve the details and remaining capacity for a single event.	200 OK (Returns the matching event object)	400 Bad Request (Invalid ID format, if strict typing is enforced), 404 Not Found (No event exists with <id>)
PATCH /events/<id>:	partially update an existing event's details, such as title or capacity.	200 OK (Returns the updated event object)	400 Bad Request (Malformed payload), 401 Unauthorized, 403 Forbidden (Caller does not own the event), 404 Not Found, 422 Unprocessable Entity (Invalid field values)

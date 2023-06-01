#!/usr/bin/env python3

import os
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.environ.get("DB_URI", f"sqlite:///{os.path.join(BASE_DIR, 'instance/app.db')}")

from flask import Flask, make_response, jsonify, request
from flask_migrate import Migrate
from flask_restful import Api, Resource

from models import db, Activity, Camper, Signup

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

migrate = Migrate(app, db)

db.init_app(app)

@app.route('/')
def home():
    return ''

@app.route('/campers', methods = ["GET","POST"])
def campers():
    if request.method == "GET":
        campers = [campers_to_dict(c) for c in Camper.query.all()]
        return make_response(jsonify(campers), 200)
    elif request.method == "POST":
        try:
            data = request.get_json()
            new_camper = Camper (
                name = data["name"],
                age = data["age"]
            )
            db.session.add(new_camper)
            db.session.commit()
            return make_response(jsonify(campers_to_dict(new_camper)), 201)
        except ValueError:
            return {"error": "400: Validation error"}, 400

@app.route('/campers/<int:id>', methods = ["GET"])
def campers_by_id(id):
    camper = Camper.query.filter(Camper.id == id).first()
    if camper:
        camper_dict = campers_to_dict(camper)
        camper_dict["activities"] = [activities_to_dict(a) for a in camper.activities]
        return make_response(jsonify(camper_dict), 200)
    return {"error": "404: Camper not found"}
@app.route("/activities")
def activities():
    activities = [activities_to_dict(a) for a in Activity.query.all()]
    return make_response(jsonify(activities), 200)
@app.route("/activities/<int:id>", methods = ["DELETE"])
def activities_by_id(id):
    activity = Activity.query.filter(Activity.id == id).first()
    if activity:
        db.session.delete(activity)
        db.session.commit()
        return {}, 204
    return {"error": "404: Activity not found"}, 404
@app.route("/signups", methods = ["POST"])
def sign_ups():
    data = request.get_json()
    try:
        new_signup = Signup(
            time = data["time"],
            camper_id = data["camper_id"],
            activity_id = data["activity_id"]
        )
        db.session.add(new_signup)
        db.session.commit()
        activity_to_dict = activities_to_dict(new_signup.activity)
        return make_response(jsonify(activity_to_dict), 200)
    except ValueError:
        return {"error": "400: Validation error"}, 400
def campers_to_dict(c):
    return {
        "id": c.id,
        "name": c.name,
        "age": c.age
    }
def activities_to_dict(a):
    return {
        "id": a.id,
        "name": a.name,
        "difficulty": a.difficulty
    }

if __name__ == '__main__':
    app.run(port=5555, debug=True)

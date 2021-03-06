from flask import flash, jsonify, request, session
import requests

from app import NOT_LOGGED_IN, app
from database import connect
from forms import LoginForm, RegistrationForm
from maps import deleteMap, getCurrentMap, getMap, updateCurrentMap, updateMap
from user import getUser

import json


@app.after_request
def api_after(f):
    f.headers.add('Access-Control-Allow-Origin', '*')
    return f


@app.route("/api/logout")
def api_logout():
    uId = session.get("userId", None)
    if uId is None:
        pass
    else:
        session["userId"] = None
    flash("Logged out | You were logged out.", category="success")
    return jsonify(
        {
            "status": "success",
            "message": "Successfully loged out."
        }
    )


@app.route("/api/updateCurrentMap", methods=["POST", "DELETE"])
def api_updateCurrentMap():
    user = getUser(session.get("userId"))
    if user is None:
        return NOT_LOGGED_IN()
    if request.method == "POST":
        data = request.get_json()
        id_ = data["id"]
        mapData = getCurrentMap(user.id)
        mapData[id_] = data
        updateCurrentMap(user.id, mapData)
        # print(json.dumps(getCurrentMap(user.id), indent=4))
        return jsonify(
            {
                "status": "success",
                "message": (
                    f"Object with id = {id_} "
                    "successfully added."
                )
            }
        )
    elif request.method == "DELETE":
        id_ = request.args["id"]
        if id_ == "all":
            mapData = {}
        else:
            mapData = getCurrentMap(user.id)
            mapData.pop(id_, None)
        updateCurrentMap(user.id, mapData)
        return jsonify(
            {
                "status": "success",
                "message": (
                    f"Object with id = {request.args['id']} "
                    "successfully removed."
                )
            }
        )


@app.route("/api/getMap")
def api_getMap():
    user = getUser(request.args.get("userId", session.get("userId")))
    name = request.args.get("name", None)
    if user is None:
        return NOT_LOGGED_IN()
    if name is None:
        return jsonify(
            {
                "status": "failed",
                "message": "No name supplied"
            }
        ), 400
    # print(json.dumps(getMap(user.id, name), indent=4))
    return jsonify(
        {
            "status": "success",
            "message": "Here is your map.",
            "data": getMap(user.id, name)
        }
    )


@app.route("/api/saveMap", methods=["POST"])
def api_saveMap():
    user = getUser(session.get("userId"))
    if user is None:
        return NOT_LOGGED_IN()
    data = request.get_json()
    name = data["name"]
    mapData = data["map"]

    updateMap(user.id, name, mapData)
    return jsonify(
        {
            "status": "success",
            "message": (
                f"Map with {name = } "
                "successfully saved."
            )
        }
    )


@app.route("/api/deleteMap", methods=["DELETE"])
def api_deleteMap():
    user = getUser(session.get("userId", None))
    if user is None:
        return NOT_LOGGED_IN()
    deleteMap(user.id, request.args.get("name", None))
    return jsonify(
        {
            "status": "success",
            "message": f"Map was successfully deleted."
        }
    )


@app.route("/api/searchObject")
def api_searchObject():
    query = request.args.get("query", None)
    print(request.args)
    print(request.headers)
    if query is None:
        return jsonify(
            {
                "status": "failed",
                "message": "No query was provided"
            }
        ), 400
    r = requests.get(
        "https://nominatim.openstreetmap.org/search",
        params=dict(q=query, format="geojson", polygon_geojson=1)
    )
    return jsonify(
        {
            "status": "success",
            "message": "Here is your data",
            "data": r.json()["features"]
        }
    )

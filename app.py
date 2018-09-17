from typing import Tuple

from flask import Flask, jsonify, request, Response
import mockdb.mockdb_interface as db

app = Flask(__name__)


def create_response(
    data: dict = None, status: int = 200, message: str = ""
) -> Tuple[Response, int]:
    """Wraps response in a consistent format throughout the API.

    Format inspired by https://medium.com/@shazow/how-i-design-json-api-responses-71900f00f2db
    Modifications included:
    - make success a boolean since there's only 2 values
    - make message a single string since we will only use one message per response
    IMPORTANT: data must be a dictionary where:
    - the key is the name of the type of data
    - the value is the data itself
    :param data <str> optional data
    :param status <int> optional status code, defaults to 200
    :param message <str> optional message
    :returns tuple of Flask Response and int, which is what flask expects for a response
    """
    if type(data) is not dict and data is not None:
        raise TypeError("Data should be a dictionary 😞")

    response = {
        "code": status,
        "success": 200 <= status < 300,
        "message": message,
        "result": data,
    }
    return jsonify(response), status


"""
~~~~~~~~~~~~ API ~~~~~~~~~~~~
"""


@app.route("/")
def hello_world():
    return create_response({"content": "hello world!"})


@app.route("/mirror/<name>")
def mirror(name):
    data = {"name": name}
    return create_response(data)

@app.route("/users/<target_id>", methods=["GET", "PUT", "DELETE"])
def user(target_id):
    if request.method == "GET":
        all_users = db.get("users")
        ret_user = next((u for u in all_users if str(u["id"]) == target_id), None)

        if ret_user is None:
            return create_response({}, 404, "User could not be found in database")

        return create_response({"user": ret_user})

    elif request.method == "PUT":
        team = request.form["team"]
        name = request.form["name"]
        age = request.form["age"]

        existing_user = db.getById("users", int(target_id))
        if existing_user is None:
            return create_response({}, 404, "User could not be found in database")

        if team:
            existing_user["team"] = team

        if name:
            existing_user["name"] = name

        if age:
            existing_user["age"] = age

        return create_response({"user": existing_user}, 201, "Sucessfully updated user!")

    elif request.method == "DELETE":
        existing_user = db.getById("users", int(target_id))
        if existing_user is None:
            return create_response({}, 404, "User could not be found in database")
        db.deleteById("users", int(target_id))

# part 1 and 3
@app.route("/users", methods=["GET", "POST"])
def users():
    if request.method == "GET":
        team = request.args.get("team")
        if not team:
            data = {"users": db.get("users")}
            return create_response(data)
        users = db.get("users")
        team_users = [u for u in users if u["team"] == team]
        data = {"users": team_users}
        return create_response(data)
    else:
        team = request.form["team"]
        name = request.form["name"]
        age = request.form["age"]
        if not team or not name or not age:
            return create_response({}, 422, "Missing necesary info to create users!")

        new_user = {"team": team, "name": name, "age": age}
        db.create("users", new_user)
        return create_response({"user": new_user}, 201, "Sucessfully created new user!")

"""
~~~~~~~~~~~~ END API ~~~~~~~~~~~~
"""
if __name__ == "__main__":
    app.run(debug=True)

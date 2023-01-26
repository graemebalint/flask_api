import sqlalchemy.orm.exc
from flask import Flask, jsonify, request, make_response
from flask_sqlalchemy import SQLAlchemy
import random

db = SQLAlchemy()
app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///cafes.db"
db.init_app(app)

class Cafe(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50),nullable=False)
    map_url = db.Column(db.String(100),nullable=False)
    img_url = db.Column(db.String(100),nullable=False)
    location = db.Column(db.String(50),nullable=False)
    has_sockets = db.Column(db.Boolean,nullable=False)
    has_toilet = db.Column(db.Boolean,nullable=False)
    has_wifi = db.Column(db.Boolean,nullable=False)
    can_take_calls = db.Column(db.Boolean,nullable=False)
    seats = db.Column(db.Integer,nullable=False)
    coffee_price = db.Column(db.String(25),nullable=False)

    def to_dict(self):
        return {column.name: getattr(self, column.name) for column in self.__table__.columns}

with app.app_context():
    db.create_all()

@app.route("/")
def home():
    return "Home page"

@app.route("/getrandom",methods=["GET"])
def get_random():
    data = db.session.query(Cafe).all()
    try:
        random_cafe = data[random.randint(0,len(data)-1)]

    except ValueError:
        return make_response({"message": "There are currently no cafes in this database, so this API is unable to return "
                                         "a random cafe.", "code": 404}, 404)
    else:
        rand_cafe_dict = random_cafe.to_dict()
        return jsonify(rand_cafe_dict)

@app.route("/getall",methods=["GET"])
def get_all():
    data = db.session.query(Cafe).all()
    data_dict = [item.to_dict() for item in data]
    if data_dict == []:
        return make_response({"message": "There are currently no cafes in this database.", "code": 404},404)
    else:
        return jsonify(data_dict)

@app.route("/searchbylocation",methods=["GET"])
def searchbylocation():
    location = request.args.get("location")
    data = db.session.query(Cafe).filter_by(location = location)
    data_dict = [item.to_dict() for item in data]
    if data_dict == []:
        return make_response({"message": "No cafes in that location.", "code": 404},404)
    else:
        return jsonify(data_dict)

@app.route("/searchbyid",methods=["GET"])
def searchbyid():
    id = request.args.get("id")
    data = db.session.query(Cafe).get(id)
    if data is None:
        return make_response({"message": "That ID does not exist.", "code": 404},404)
    else:
        data_dict = data.to_dict()
        return jsonify(data_dict)

@app.route("/add",methods=["POST"])
def add():
    id = int(request.args.get("id"))
    name = request.args.get("name")
    map_url = request.args.get("map_url")
    img_url = request.args.get("img_url")
    location = request.args.get("location")
    has_sockets = bool(request.args.get("has_sockets"))
    has_toilet = bool(request.args.get("has_toilet"))
    has_wifi = bool(request.args.get("has_wifi"))
    can_take_calls = bool(request.args.get("can_take_calls"))
    seats  = request.args.get("seats")
    coffee_price = request.args.get("coffee_price")

    cafe = Cafe(id=id,name=name,map_url=map_url,img_url=img_url,location=location,has_sockets=has_sockets,
                has_toilet=has_toilet,has_wifi=has_wifi,can_take_calls=can_take_calls,seats=seats,
                coffee_price=coffee_price)

    db.session.add(cafe)
    db.session.commit()

    data = db.session.query(Cafe).get(id)
    if data is None:
        return make_response("That ID does not exist",404)
    else:
        data_dict = data.to_dict()
        return make_response("Success",200)

@app.route("/updateprice/<cafe_id>",methods=["GET","PATCH"])
def updateprice(cafe_id):
    new_price = request.args.get("new_price")
    try:
        cafe_update = db.session.query(Cafe).get(cafe_id)
        cafe_update.coffee_price = new_price
    except AttributeError:
        return make_response({"message": "That coffee ID does not exist. Cannot update the price of a "
                                         "non-existant cafe.", "code": 404}, 404)
    else:
        db.session.commit()
        return jsonify(cafe_update.to_dict())

@app.route("/deletebyid",methods=["GET","DELETE"])
def delete_by_id():
    try:
        id = request.args.get("id")
        cafe_to_delete = db.session.query(Cafe).get(id)
        db.session.delete(cafe_to_delete)
    except sqlalchemy.orm.exc.UnmappedInstanceError:
        return make_response({"message": "Delete failed. That ID does not exist.", "code": 404}, 404)
    else:
        db.session.commit()
        return make_response({"code": 200, "message":f"Successfully deleted: {id}"})

@app.route("/deleteall",methods=["GET","DELETE"])
def delete_all():
    db.session.query(Cafe).delete()
    db.session.commit()
    return make_response({"code": 200, "message":f"Successfully deleted: {id}"})

if __name__ == "__main__":
    app.run(debug=True)
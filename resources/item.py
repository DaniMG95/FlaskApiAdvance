from flask_restful import Resource
from flask import request
from flask_jwt_extended import jwt_required
from schemas.item import ItemSchema
from models.item import ItemModel

BLANK_ERROR = "'{}' cannot be blank"
ITEM_NOT_FOUND = "Item not found."
ERROR_INSERT_ITEM =  "An error occurred while inserting the item."
NAME_ALREADY_EXISTS = "An item with name '{}' already exists."
ITEM_DELETED = "Item deleted."

item_schema = ItemSchema()
item_list_schema = ItemSchema(many=True)

class Item(Resource):

    @classmethod
    def get(cls, name: str):
        item = ItemModel.find_by_name(name)
        if item:
            return item_schema.dumps(item), 200
        return {"message": ITEM_NOT_FOUND}, 404

    @classmethod
    @jwt_required(fresh=True)
    def post(cls, name: str):
        if ItemModel.find_by_name(name):
            return {"message": NAME_ALREADY_EXISTS.format(name)}, 400

        data = request.get_json()
        data["name"] = name
        item = item_schema.load(data)

        try:
            item.save_to_db()
        except:
            return {"message":ERROR_INSERT_ITEM}, 500

        return item_schema.dumps(item), 201

    @classmethod
    @jwt_required
    def delete(cls, name: str):
        item = ItemModel.find_by_name(name)
        if item:
            item.delete_from_db()
            return {"message": ITEM_DELETED}, 200
        return {"message": ITEM_NOT_FOUND}, 404

    @classmethod
    def put(cls, name: str):
        data = request.get_json()

        item = ItemModel.find_by_name(name)

        if item:
            item.price = data["price"]
        else:
            data["name"] = name
            item = item_schema.load(data)

        item.save_to_db()

        return item_schema.dumps(item), 200


class ItemList(Resource):
    @classmethod
    def get(cls):
        items = item_list_schema.dump(ItemModel.find_all())
        return {"items": items}, 200

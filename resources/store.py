from flask_restful import Resource
from models.store import StoreModel
from schemas.store import StoreSchema

store_schema = StoreSchema()
stores_schema = StoreSchema(many=True)



class Store(Resource):
    @classmethod
    def get(cls, name: str):
        store = StoreModel.find_by_name(name)
        if store:
            return StoreSchema.dumps(store)
        return {"message": "Store not found."}, 404

    @classmethod
    def post(cls, name: str):
        if StoreModel.find_by_name(name):
            return {"message": "A store with name '{}' already exists.".format(name)},400,
            
        store = StoreModel(name=name)
        try:
            store.save_to_db()
        except:
            return {"message": "An error occurred while creating the store."}, 500

        return store.json(), 201

    @classmethod
    def delete(cls, name: str):
        store = StoreModel.find_by_name(name)
        if store:
            store.delete_from_db()

        return {"message": "Store deleted."}


class StoreList(Resource):

    @classmethod
    def get(cls):
        return {"stores": stores_schema.dumps(StoreModel.find_all())}

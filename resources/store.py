from flask_restful import Resource
from models.store import StoreModel
from flask_jwt_extended import jwt_required

class Store(Resource):
    def get(self, name):
        store = StoreModel.find_by_name(name)
        if store:
            return store.json()
        return {'message': 'Store Not Found'}, 404

    @jwt_required()
    def post(self, name):
        if StoreModel.find_by_name(name):
            return {'message': "A Store with name '{}' already exists.".format(name)}, 400

        store = StoreModel(name)
        try:
            store.save_to_db()
            return store.json()
        except:
            return {'message' : "An error has occurred while creating the store."}, 500


    @jwt_required(fresh=True)
    def delete(self, name):
        store = StoreModel.find_by_name(name)
        if store:
            store.delete_from_db()

        return{'message': 'Store deleted.'}

class StoreList(Resource):
    def get(self):
        return {'stores': [store.json() for store in StoreModel.find_all()]}
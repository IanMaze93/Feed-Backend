def update_one(collection, query, update):
    return collection.update_one(query, update)


def update_many(collection, query, update):
    return collection.update_many(query, update)


def upsert_one(collection, query, update):
    return collection.update_one(query, update, upsert=True)


def upsert_many(collection, query, update):
    return collection.update_many(query, update, upsert=True)


def push_to_array(collection, query, array_field, value):
    update = {"$push": {array_field: value}}
    return collection.update_one(query, update)

import mongoengine

# Needed to talk to MongoDB
def global_init():
    mongoengine.register_connection(alias='core', name='snake_bnb') # name is the name of the database


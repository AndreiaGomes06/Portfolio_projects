import datetime
import mongoengine


class Owner(mongoengine.Document):
    resgistered_date = mongoengine.DateTimeField(default=datetime.datetime.now)
    name = mongoengine.StringField(required=True)
    email = mongoengine.StringField(required=True)

    # To refer the object ids that refer to the snakes and to the cages
    snake_ids = mongoengine.ListField()
    cage_ids = mongoengine.ListField()

    # which database connection to use and what to call the collection when it goes into the database
    meta = {
        'db_alias': 'core',
        'collections': 'owners'
    }
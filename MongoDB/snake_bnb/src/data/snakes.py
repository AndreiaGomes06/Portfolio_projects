import datetime
import mongoengine

# This model is going to be mapped in one or more of those databases
class Snake(mongoengine.Document):
    resgistered_date = mongoengine.DateTimeField(default=datetime.datetime.now)
    species = mongoengine.StringField(required=True)

    length = mongoengine.FloatField(required=True, min_value=0.004)
    name = mongoengine.StringField(required=True)
    is_venomous = mongoengine.BooleanField(required=True)

    meta = {
        'db_alias': 'core',
        'collections': 'snakes'
    }
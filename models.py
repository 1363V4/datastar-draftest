from peewee import Model, AutoField, SmallIntegerField, UUIDField, DateTimeField
from datetime import datetime

class Draft(Model):
    id = AutoField(primary_key=True)
    created = DateTimeField(default=datetime.now)
    blue = UUIDField()
    red = UUIDField(null=True)
    
    current_move = SmallIntegerField(default=0)
    r1b = SmallIntegerField(null=True)
    b1b = SmallIntegerField(null=True)
    b2b = SmallIntegerField(null=True)
    r2b = SmallIntegerField(null=True)
    r3b = SmallIntegerField(null=True)
    b3b = SmallIntegerField(null=True)
    b1p = SmallIntegerField(null=True)
    r1p = SmallIntegerField(null=True)
    r2p = SmallIntegerField(null=True)
    b2p = SmallIntegerField(null=True)
    b3p = SmallIntegerField(null=True)
    r3p = SmallIntegerField(null=True)
    r4b = SmallIntegerField(null=True)
    b4b = SmallIntegerField(null=True)
    b5b = SmallIntegerField(null=True)
    r5b = SmallIntegerField(null=True)
    r4p = SmallIntegerField(null=True)
    b4p = SmallIntegerField(null=True)
    b5p = SmallIntegerField(null=True)
    r5p = SmallIntegerField(null=True)

    votes_blue = SmallIntegerField(default=1)
    votes_red = SmallIntegerField(default=1)

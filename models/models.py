#from sqlalchemy import Column, String, Integer, Boolean, DateTime, ARRAY, ForeignKey
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import backref
from sqlalchemy.sql import func
from datetime import datetime

db = SQLAlchemy()

#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#

class Venue(db.Model):
    __tablename__ = 'Venue'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    address = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))


    # TODO: implement any missing fields, as a database migration using Flask-Migrate

class Artist(db.Model):
    __tablename__ = 'Artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    genres = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))

    # TODO: implement any missing fields, as a database migration using Flask-Migrate

# TODO Implement Show and Artist models, and complete all model relationships and properties, as a database migration.
class Show(db.Model):
    __tablename__  = 'shows'
    id = db.Column(db.Integer, primary_key=True)
    start_time = db.Column(db.DateTime, nullable=False)
    venue_id = db.Column(db.Integer, db.ForeignKey('Venue.id'))
    artist_id = db.Column(db.Integer, db.ForeignKey('Artist.id'))

def __init__(self, venue_id, artist_id, start_time):
    self.venue_id =  venue_id
    self.artist_id = artist_id
    self.start_time =start_time

def set(self):
    db.session.add(self)
    db.sesion.commit()

def getShowDetails(self):
    return {
        'venue_id': self.venue_id,
        'venue_name': self.Venue.name,
        'artist_id': self.artist_id,
        'artist_name': self.Artist.name,
        'artist_image_link': self.Artist.image_link,
        'start_time': self.start_time
    }

def venue_details(self):
    return {
        'venue_id': self.venue_id,
        'venue_name': self.Venue.name,
        'venue_image_link': self.Venue.image_link,
        'start_time': self.start_time.strftime('%Y-%m-%d %H:%M:%S')
        }

def getArtistDetails(self):
    return {
        'artist_id': self.artist_id,
        'start_time': self.start_time.strftime('%Y-%m-%d %H:%M:%S'),
        'artist_name': self.Artist.name,
        'artist_image_link': self.Artist.image_link
        }



    # ----------------------------------------------------------------------------#
# End - - Models.
# ----------------------------------------------------------------------------#
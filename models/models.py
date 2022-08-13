from datetime import datetime

from flask_sqlalchemy import SQLAlchemy

# ----------------------------------------------------------------------------#
# Models and db object imported by app
# ----------------------------------------------------------------------------#
db = SQLAlchemy()

# Venue Model
#----------------------------------------------------------------------------
class Venue(db.Model):
    __tablename__ = "venues"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    genres = db.Column(db.ARRAY(db.String), server_default="{}")
    address = db.Column(db.String(128))
    city = db.Column(db.String(128))
    state = db.Column(db.String(128))
    phone = db.Column(db.String(128))
    website = db.Column(db.String)
    facebook_link = db.Column(db.String(128))
    seeking_talent = db.Column(db.Boolean, default=False)
    seeking_description = db.Column(db.String)
    image_link = db.Column(db.String(512))

    shows = db.relationship("Show", backref="venues", lazy=True)

    def __repr__(self):
        return f"<Venue id: {self.id}; name: {self.name}>"

# Artist Model
#----------------------------------------------------------------------------
class Artist(db.Model):
    __tablename__ = "artists"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    genres = db.Column(db.ARRAY(db.String), server_default="{}")
    city = db.Column(db.String(128))
    state = db.Column(db.String(128))
    phone = db.Column(db.String(128))
    facebook_link = db.Column(db.String(128))
    seeking_venue = db.Column(db.Boolean, default=False)
    image_link = db.Column(db.String(512))
    website = db.Column(db.String(128))
    seeking_description = db.Column(db.String)

    shows = db.relationship("Show", backref="artists", lazy=True)

    def __repr__(self):
        return f"<Artist id: {self.id}; name: {self.name}>"

# Show Model
#----------------------------------------------------------------------------
class Show(db.Model):
    __tablename__ = "shows"

    id = db.Column(db.Integer, primary_key=True)
    venue_id = db.Column(db.Integer, db.ForeignKey("venues.id"), nullable=False)
    start_time = db.Column(db.DateTime, default=datetime.utcnow)
    artist_id = db.Column(db.Integer, db.ForeignKey("artists.id"), nullable=False)

    def __repr__(self):
        return f"<Show id: {self.id}; start_time: {self.start_time}>"

#----------------------------------------------------------------------------
# End
#----------------------------------------------------------------------------
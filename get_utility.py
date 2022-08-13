import sys
from datetime import datetime

from flask import flash, request
from sqlalchemy import func

from forms import *
from models.models import *


class getUtility:
    def get_shows(self, interval="all", entity="show", entity_id=None):
        all_shows = db.session.query(Show)
        if interval == "all" or entity in [None, "show"] or not entity_id:
            return all_shows.all()
        time_expr = Show.start_time < datetime.now() if interval == "past" else Show.start_time > datetime.now()
        entity_filter = Show.artist_id if entity == "artist" else Show.venue_id
        return all_shows \
            .join(Venue) \
            .filter(entity_filter == entity_id) \
            .filter(time_expr).all()

    def get_shows_for_artist(self, artist_id, interval="all"):
        return self.get_shows(interval=interval, entity="artist", entity_id=artist_id)

    def get_shows_for_venue(self, venue_id, interval="all"):
        return self.get_shows(interval=interval, entity="venue", entity_id=venue_id)

    def max_value(self, db, entity):
        max_values = {
            "artists": db.session.query(func.max(Artist.id)).scalar(),
            "shows": db.session.query(func.max(Show.id)).scalar(),
            "venues": db.session.query(func.max(Venue.id)).scalar()
        }
        return max_values[entity]

    @staticmethod
    def search(entity, pattern):
        results = {
            "artists": Artist.query.filter(Artist.name.ilike(f"%{pattern}%")).all(),
            "venues": Venue.query.filter(Venue.name.ilike(f"%{pattern}%")).all(),
        }
        return results[entity]

    def handle_submission(self, obj, operation="insert", entity_id=None):
        cls_name = obj.__class__.__name__
        entity = obj.__tablename__
        verb = "updated" if operation == "update" else "listed"
        entity_form = {
            "artists": ArtistForm(request.form),
            "shows": ShowForm(request.form),
            "venues": VenueForm(request.form),
        }
        form = entity_form[entity]
        obj_max_id = self.max_value(db, entity)
        if obj_max_id:
            obj.id = obj_max_id + 1
        if entity == "artists":
            data = {
                "name": form.name.data,
                "genres": form.genres.data,
                "city": form.city.data,
                "state": form.state.data,
                "phone": form.phone.data,
                "facebook_link": form.facebook_link.data,
                "seeking_venue": form.seeking_venue.data,
                "image_link": form.image_link.data,
                "website": form.website_link.data,
                "seeking_description": form.seeking_description.data
            }
        elif entity == "shows":
            data = {
                "venue_id": form.venue_id.data,
                "artist_id": form.artist_id.data,
                "start_time": form.start_time.data
            }
        else:
            data = {
                "name": form.name.data,
                "genres": form.genres.data,
                "address": form.address.data,
                "city": form.city.data,
                "state": form.state.data,
                "phone": form.phone.data,
                "website": form.website_link.data,
                "facebook_link": form.facebook_link.data,
                "seeking_talent": form.seeking_talent.data,
                "seeking_description": form.seeking_description.data,
                "image_link": form.image_link.data}

        if operation == "update":
            old_obj = obj.__class__().query.get(entity_id)
            obj = old_obj
        for key, value in data.items():
            if value != "":
                setattr(obj, key, value)
        try:
            db.session.add(obj)
            db.session.commit()
            flash(f"{cls_name} was successfully {verb}!")
        except Exception as e:
            flash(f"An error occurred. {cls_name} could not be {verb}.")
            print(e, file=sys.stderr)
            db.session.rollback()
        finally:
            db.session.close()
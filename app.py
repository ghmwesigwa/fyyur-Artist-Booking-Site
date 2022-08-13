# ----------------------------------------------------------------------------#
# Imports
# ----------------------------------------------------------------------------#
import logging
import os
import sys
from datetime import datetime
from logging import FileHandler, Formatter

import dateutil.parser
from babel import dates
from flask import (Flask, abort, flash, redirect, render_template, request,
                   url_for)
from flask_migrate import Migrate
from flask_moment import Moment
from sqlalchemy import func

from config import SQLALCHEMY_DATABASE_URI
from forms import ArtistForm, ShowForm, VenueForm
from get_utility import getUtility
from models.models import *

# ----------------------------------------------------------------------------#
# App Config.
# ----------------------------------------------------------------------------#
app = Flask(__name__, template_folder="./templates")
app.config.from_object("config")
app.config["SQLALCHEMY_DATABASE_URI"] = SQLALCHEMY_DATABASE_URI
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db.init_app(app)
migrate = Migrate(app, db)
moment = Moment(app)
get_utility = getUtility()


# ----------------------------------------------------------------------------#
# Filters.
# ----------------------------------------------------------------------------#

def format_datetime(value, date_format="medium"):
    date = dateutil.parser.parse(value)
    if date_format == "full":
        date_format = "EEEE MMMM, d, y 'at' h:mma"
    elif date_format == "medium":
        date_format = "EE MM, dd, y h:mma"
    return dates.format_datetime(date, date_format, locale="en")


app.jinja_env.filters["datetime"] = format_datetime


# ----------------------------------------------------------------------------#
# Controllers.
# ----------------------------------------------------------------------------#

@app.route("/")
def index():
    return render_template("pages/home.html")


# ----------------------------------------------------------------------------#
#  Venues
# ----------------------------------------------------------------------------#

@app.route("/venues")
def venues():
    upcoming_shows = get_utility.get_shows("future")
    data = [{
        "city": venue.city,
        "state": venue.state,
        "venues": [{
            "id": venue.id,
            "name": venue.name,
            "num_upcoming_shows": [show.venue_id for show in upcoming_shows].count(venue.id)
        } for venue in Venue.query.filter(Venue.city == venue.city)
        ]
    }
        for venue in Venue.query.distinct(Venue.city).order_by(Venue.city).all()
    ]
    return render_template("pages/venues.html", areas=data)

@app.route("/venues/search", methods=["POST"])
def search_venues():
    pattern = request.form.get("search_term", default="")
    results = get_utility.search(entity="venues", pattern=pattern)

    response = {
        "count": len(results),
        "data": [{
            "id": venue.id,
            "name": venue.name,
            "num_upcoming_shows": len(get_utility.get_shows_for_venue(venue.id, "future"))
        } for venue in results]
    }
    return render_template("pages/search_venues.html", results=response, search_term=pattern)


@app.route("/venues/<int:venue_id>")
def show_venue(venue_id):
    venue = Venue.query.get(venue_id)
    if not venue:
        abort(404)
    past_venue_shows = get_utility.get_shows_for_venue(venue_id, "past")
    upcoming_venue_shows = get_utility.get_shows_for_venue(venue_id, "future")

    past_shows = [{
        "artist_id": show.artist_id,
        "artist_name": show.artists.name,
        "artist_image_link": show.artists.image_link,
        "start_time": str(show.start_time)
    } for show in past_venue_shows]

    upcoming_shows = [{
        "artist_id": show.artist_id,
        "artist_name": show.artists.name,
        "artist_image_link": show.artists.image_link,
        "start_time": str(show.start_time)
    } for show in upcoming_venue_shows]

    data = {
        "id": venue.id,
        'name': venue.name,
        'genres': venue.genres,
        'address': venue.address,
        'city': venue.city,
        'state': venue.state,
        'phone': venue.phone,
        'website': venue.website,
        'facebook_link': venue.facebook_link,
        'seeking_talent': venue.seeking_talent,
        'seeking_description': venue.seeking_description,
        'image_link': venue.image_link,
        'past_shows': past_shows,
        'upcoming_shows': upcoming_shows,
        "past_shows_count": len(past_shows),
        "upcoming_shows_count": len(upcoming_shows),
    }

    return render_template("pages/show_venue.html", venue=data)


# ----------------------------------------------------------------------------#
#  Create Venue
# ----------------------------------------------------------------------------#

@app.route("/venues/create", methods=["GET"])
def create_venue_form():
    form = VenueForm()
    return render_template("forms/new_venue.html", form=form)


@app.route("/venues/create", methods=["POST"])
def create_venue_submission():
    venue = Venue()
    get_utility.handle_submission(venue, "insert")
    return redirect(url_for("index"))


@app.route("/venues/<venue_id>", methods=["DELETE"])
def delete_venue(venue_id):
    venue = Venue.query.get(venue_id)
    try:
        db.session.delete(venue)
        db.session.commit()
    except Exception as e:
        logging.error(e)
        db.session.rollback()
    finally:
        db.session.close()
    return redirect(url_for("index"))


# ----------------------------------------------------------------------------#
#  Artists
# ----------------------------------------------------------------------------#
@app.route("/artists")
def artists():
    data = [{"id": artist.id, "name": artist.name} for artist in Artist.query.all()]
    return render_template("pages/artists.html", artists=data)


@app.route("/artists/search", methods=["POST"])
def search_artists():
    pattern = request.form.get("search_term", default="")
    results = get_utility.search(entity="artists", pattern=pattern)

    response = {
        "count": len(results),
        "data": [{
            "id": artist.id,
            "name": artist.name,
            "num_upcoming_shows": get_utility.get_shows_for_artist(artist.id, "future"),
        } for artist in results]
    }
    return render_template("pages/search_artists.html", results=response, search_term=pattern)


@app.route("/artists/<int:artist_id>")
def show_artist(artist_id):
    # shows the artist page with the given artist_id
    artist_past_shows = get_utility.get_shows_for_artist(artist_id, "past")
    artist_upcoming_shows = get_utility.get_shows_for_artist(artist_id, "future")

    past_shows = [{
        "venue_id": show.venue_id,
        "venue_name": show.venues.name,
        "venue_image_link": show.venues.image_link,
        "start_time": str(show.start_time),
    } for show in artist_past_shows]

    upcoming_shows = [{
        "venue_id": show.venue_id,
        "venue_name": show.venues.name,
        "venue_image_link": show.venues.image_link,
        "start_time": str(show.start_time),
    } for show in artist_upcoming_shows]

    artist = Artist.query.get(artist_id)
    if not artist:
        abort(404)
    data = {
        "id": artist.id,
        "name": artist.name,
        "genres": artist.genres,
        "city": artist.city,
        "state": artist.state,
        "phone": artist.phone,
        "website": artist.website,
        "facebook_link": artist.facebook_link,
        "seeking_venue": artist.seeking_venue,
        "seeking_description": artist.seeking_description,
        "image_link": artist.image_link,
        "past_shows": past_shows,
        "upcoming_shows": upcoming_shows,
    }
    return render_template("pages/show_artist.html", artist=data)

# ----------------------------------------------------------------------------#
#  Update
# ----------------------------------------------------------------------------#
@app.route("/artists/<int:artist_id>/edit", methods=["GET"])
def edit_artist(artist_id):
    form = ArtistForm()
    artist = Artist.query.get(artist_id)
    data = {"id": artist.id, "name": artist.name}
    return render_template("forms/edit_artist.html", form=form, artist=data)


@app.route("/artists/<int:artist_id>/edit", methods=["POST"])
def edit_artist_submission(artist_id):
    artist = Artist()
    get_utility.handle_submission(artist, operation="update", entity_id=artist_id)
    return redirect(url_for("show_artist", artist_id=artist_id))


@app.route("/venues/<int:venue_id>/edit", methods=["GET"])
def edit_venue(venue_id):
    form = VenueForm()
    venue = Venue.query.get(venue_id)
    data = {
        "id": venue.id,
        "name": venue.name,
        "genres": venue.genres,
        "address": venue.address,
        "city": venue.city,
        "state": venue.state,
        "phone": venue.phone,
        "website": venue.website,
        "facebook_link": venue.facebook_link,
        "seeking_talent": venue.seeking_talent,
        "seeking_description": venue.seeking_description,
        "image_link": venue.image_link
    }
    return render_template("forms/edit_venue.html", form=form, venue=data)


@app.route("/venues/<int:venue_id>/edit", methods=["POST"])
def edit_venue_submission(venue_id):
    venue = Venue()
    get_utility.handle_submission(venue, operation="update", entity_id=venue_id)
    return redirect(url_for("show_venue", venue_id=venue_id))


# ----------------------------------------------------------------------------#
#  Create Artist
# ----------------------------------------------------------------------------#

@app.route("/artists/create", methods=["GET"])
def create_artist_form():
    form = ArtistForm()
    return render_template("forms/new_artist.html", form=form)


@app.route("/artists/create", methods=["POST"])
def create_artist_submission():
    artist = Artist()
    get_utility.handle_submission(artist, "insert")
    return redirect(url_for("index"))


# ----------------------------------------------------------------------------#
#  Shows
# ----------------------------------------------------------------------------#

@app.route("/shows")
def shows():
    # displays list of shows at /shows
    shows_data = [{
        "venue_id": show.venue_id,
        "venue_name": show.venues.name,
        "artist_id": show.artists.id,
        "artist_name": show.artists.name,
        "artist_image_link": show.artists.image_link,
        "start_time": str(show.start_time)}
        for show in Show.query.all()
    ]
    return render_template("pages/shows.html", shows=shows_data)


@app.route("/shows/create")
def create_shows():
    # renders form. do not touch.
    form = ShowForm()
    return render_template("forms/new_show.html", form=form)


@app.route("/shows/create", methods=["POST"])
def create_show_submission():
    show = Show()
    get_utility.handle_submission(show, "insert")
    return redirect(url_for("index"))


@app.errorhandler(404)
def not_found_error(error):
    logging.error(error)
    return render_template("errors/404.html"), 404


@app.errorhandler(500)
def server_error(error):
    logging.error(error)
    return render_template("errors/500.html"), 500


if not app.debug:
    file_handler = FileHandler("error.log")
    file_handler.setFormatter(
        Formatter("%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]")
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info("errors")

# ----------------------------------------------------------------------------#
# Launch.
# ----------------------------------------------------------------------------#

if __name__ == "__main__":
    # Get Flask port from env or use 5000
    port = int(os.environ.get("FLASK_PORT", 5000))
    app.run(host="0.0.0.0", port=port)
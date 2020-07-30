#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

from app import db


#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#

class Venue(db.Model):
    __tablename__ = 'venue'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    address = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    shows = db.relationship('Shows', backref="venue", lazy=True, cascade="all, delete")
    website = db.Column(db.String(120))
    genresVen = db.relationship('GenresVen', backref='venue', lazy=True, cascade="all, delete")
    seeking_talent = db.Column(db.Boolean)
    seeking_description = db.Column(db.String(500))

    # TODO: implement any missing fields, as a database migration using Flask-Migrate

class Artist(db.Model):
    __tablename__ = 'artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    website = db.Column(db.String(120))
    seeking_venue = db.Column(db.Boolean)
    seeking_description = db.Column(db.String(500))
    genres_a = db.relationship('Genresartist', backref="artist", lazy=True)
    shows = db.relationship('Shows', backref="artist", lazy=True)

    # TODO: implement any missing fields, as a database migration using Flask-Migrate

# TODO Implement Show and Artist models, and complete all model relationships and properties, as a database migration.

class Genresartist(db.Model):
  __tablename__ = 'genresa'
  id = db.Column(db.Integer, primary_key=True)
  name = db.Column(db.String)
  artist_id = db.Column(db.Integer, db.ForeignKey(
        'artist.id'), nullable=False)

class GenresVen(db.Model):
  __tablename__ = 'genresv'
  id = db.Column(db.Integer, primary_key=True)
  name = db.Column(db.String)
  venue_id = db.Column(db.Integer, db.ForeignKey(
        'venue.id'), nullable=False)


class Shows(db.Model):
  __tablename__ = 'shows'
  id = db.Column(db.Integer, primary_key=True)
  artist_id = db.Column(db.Integer, db.ForeignKey('artist.id'), nullable=False)
  venue_id = db.Column(db.Integer, db.ForeignKey('venue.id'), nullable=False)
  start_time = db.Column(db.DateTime, nullable=False)

#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
from flask_migrate import Migrate
from sqlalchemy import func
import sys

#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)

migrate = Migrate(app, db)

# TODO: connect to a local postgresql database

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

#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  date = dateutil.parser.parse(value)
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
  return babel.dates.format_datetime(date, format)

app.jinja_env.filters['datetime'] = format_datetime

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#

@app.route('/')
def index():
  return render_template('pages/home.html')


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
  #DONE
  # TODO: replace with real venues data.
  #       num_shows should be aggregated based on number of upcoming shows per venue.

  # obtain all the venue information from db tables using query below
  allVenues = Venue.query.with_entities(func.count(Venue.id), Venue.city, Venue.state)\
                .group_by(Venue.city, Venue.state).all()

  print('All venues from db tables:')
  print(allVenues)

  data = []

  for venue in allVenues:
    venues = []

    areaVenues = Venue.query.filter_by(state=venue.state).filter_by(city=venue.city).all()
    print('All venues in the area')
    print(areaVenues)
    for areaVenue in areaVenues:
      venues.append({
        "id": areaVenue.id,
        "name": areaVenue.name
      })
    data.append({
      "city": venue.city,
      "State": venue.state,
      "venues": venues 
    })

  print('data List:')
  print(data)

  return render_template('pages/venues.html', areas=data)

@app.route('/venues/search', methods=['POST'])
def search_venues():
  # DONE
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for Hop should return "The Musical Hop".
  # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
  print('Inside the search_venues() function')
  
  search_term = request.form.get('search_term', '')
  mod_search_term = "%{}%".format(search_term)
  
  print('The Modified search term obtained from webpage is')
  print(mod_search_term)

  venues_matching = db.session.query(Venue).filter(Venue.name.ilike(mod_search_term)).all()

  data = []

  for venue in venues_matching:
    data.append({
      "id": venue.id,
      "name": venue.name,
      "num_upcoming_shows": len(db.session.query(Shows).filter(Shows.venue_id == venue.id).\
        filter(Shows.start_time>datetime.now()).all())
    })
  
  print('Data array with venues matching the search results')
  print(data)
  
  response={
    "count": len(venues_matching),
    "data": data
  }
  return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # DONE
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id

  print('************')
  print('Inside the show_venue() function')
  print('************')
  venue = db.session.query(Venue).get(venue_id)

  genres_venue = db.session.query(GenresVen).filter(GenresVen.venue_id==venue_id).all()
  genres = []

  for genre in genres_venue:
    genres.append(genre.name)

  print('Venue Genre names array')
  print(genres)

  past_shows_db = db.session.query(Shows).join(Artist).filter(Shows.venue_id==venue_id).\
  filter(Shows.start_time<datetime.now()).all()
  
    
  past_shows = []

  for show in past_shows_db:
    past_shows.append({
      "artist_id": show.artist_id,
      "artist_name": show.artist.name,
      "artist_image_link": show.artist.image_link,
      "start_time": show.start_time.strftime('%Y-%m-%d %H:%M:%S')
    })

  print('past_shows list created from DB')
  print(past_shows)

  upcoming_shows_db = db.session.query(Shows).join(Artist).filter(Shows.venue_id==venue_id).\
    filter(Shows.start_time>datetime.now()).all()

  upcoming_shows = []

  for show in upcoming_shows_db:
    upcoming_shows.append({
      "artist_id": show.artist_id,
      "artist_name": show.artist.name,
      "artist_image_link": show.artist.image_link,
      "start_time": show.start_time.strftime('%Y-%m-%d %H:%M:%S')
    })

  print('upcoming_shows list created from DB')
  print(upcoming_shows)

  data = {
    "id": venue.id,
    "name": venue.name,
    "genres": genres,
    "city": venue.city,
    "state": venue.state,
    "address": venue.address,
    "phone": venue.phone,
    "website": venue.website,
    "facebook_link": venue.facebook_link,
    "seeking_talent": venue.seeking_talent,
    "seeking_description": venue.seeking_description,
    "image_link": venue.image_link,
    "past_shows": past_shows,
    "upcoming_shows": upcoming_shows,
    "past_shows_count": len(past_shows),
    "upcoming_shows_count": len(upcoming_shows), 
  }
  
  print('assembled data list for the artist from DB data')
  print(data)

  return render_template('pages/show_venue.html', venue=data)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  # DONE
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  # DONE
  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion
  print('Inside the create_venue_submission() function')
  
  data = request.form
  print('Data from the request.form sent back by webpage')
  print(data)

  error = False

  try:
    name = request.form['name']
    state = request.form['state']
    city = request.form['city']
    address = request.form['address']
    phone = request.form['phone']
    genres = request.form.getlist('genres')
    facebook_link = request.form['facebook_link']
    venue = Venue(name=name, state=state, city=city, address=address, phone=phone,\
        facebook_link=facebook_link)
    db.session.add(venue)
    db.session.commit()

    id = db.session.query(Venue).filter(Venue.name == name)[0].id
    print('Recently added venue Id')
    print(id)

    print('Genres from the webpage')
    print(genres)
  
    for genre in genres:
      genre_entry = GenresVen(name=genre, venue_id=id)
      db.session.add(genre_entry)
      db.session.commit()
    
  except:
    db.session.rollback()
    error = True
    print(sys.exc_info())
    
  finally:
    db.session.close()

  if error:
    flash('Venue ' + request.form['name'] + ' was not successfully listed!')
    
  if not error:
    flash('Venue ' + request.form['name'] + ' was successfully listed!')   
    

  # on successful db insert, flash success
  # flash('Venue ' + request.form['name'] + ' was successfully listed!')
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Venue ' + data.name + ' could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
  return render_template('pages/home.html')

@app.route('/venues/<int:venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  # DONE  
  # TODO: Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.

  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage
  print('****************')
  print('Inside the delete_venue function and venue id sent is:')
  print(venue_id)
  print('*************')
  error = False
  try:
    venue = Venue.query.get(venue_id)
    db.session.delete(venue)
    db.session.commit()
  except:
    error = True
    db.session.rollback()
    print(sys.exc_info())
  finally:
    db.session.close()

  if error: 
    flash('An error occurred. Venue could not be deleted.')
  if not error: 
    flash('Venue was successfully deleted.')
    print('Inside the if statement with error = false')

  print('Reached the bottom of the delete_venue() function')

  # After return below the control of the program is back with the 
  # Javascript fetch() function inside the button.onclick() function. 
  # The html rendering is handled there
  
  return None
  
  
  

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  # DONE
  # TODO: replace with real data returned from querying the database
  data = []

  allArtists = Artist.query.all()

  print('All Artists from Database:')
  print(allArtists)

  for artist in allArtists:
    data.append({
      "id": artist.id,
      "name": artist.name
    })

  return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  # DONE
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
  # search for "band" should return "The Wild Sax Band".
  
  print('Inside the search_artists() function')
  
  search_term = request.form.get('search_term', '')
  mod_search_term = "%{}%".format(search_term)
  
  print('The Modified search term obtained from webpage is')
  print(mod_search_term)

  artists_matching = db.session.query(Artist).filter(Artist.name.ilike(mod_search_term)).all()

  data = []

  for artist in artists_matching:
    data.append({
      "id": artist.id,
      "name": artist.name,
      "num_upcoming_shows": len(db.session.query(Shows).filter(Shows.artist_id == artist.id).\
        filter(Shows.start_time>datetime.now()).all())
    })
  
  print('Data array with artists matching the search results')
  print(data)
  
  response={
    "count": len(artists_matching),
    "data": data
  }

  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # DONE
  # shows the artist page with the given artist_id
  # TODO: replace with real venue data from the venues table, using venue_id
  print('Inside the show_artist() function')
  artist = db.session.query(Artist).get(artist_id)

  genres_artist = db.session.query(Genresartist).filter(Genresartist.artist_id==artist_id).all()
  genres = []

  for genre in genres_artist:
    genres.append(genre.name)

  print('Artist Genre names array')
  print(genres)

  past_shows_db = db.session.query(Shows).join(Venue).filter(Shows.artist_id==artist_id).\
    filter(Shows.start_time<datetime.now()).all()
  
    
  past_shows = []

  for show in past_shows_db:
    past_shows.append({
      "venue_id": show.venue_id,
      "venue_name": show.venue.name,
      "venue_image_link": show.venue.image_link,
      "start_time": show.start_time.strftime('%Y-%m-%d %H:%M:%S')
    })

  
  print('past_shows list created from DB')
  print(past_shows)

  upcoming_shows_db = db.session.query(Shows).join(Venue).filter(Shows.artist_id==artist_id).\
    filter(Shows.start_time>datetime.now()).all()

  upcoming_shows = []

  for show in upcoming_shows_db:
    upcoming_shows.append({
      "venue_id": show.venue_id,
      "venue_name": show.venue.name,
      "venue_image_link": show.venue.image_link,
      "start_time": show.start_time.strftime('%Y-%m-%d %H:%M:%S')
    })   

  print('upcoming_shows list created from DB')
  print(upcoming_shows)

  data = {
    "id": artist.id,
    "name": artist.name,
    "genres": genres,
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
    "past_shows_count": len(past_shows),
    "upcoming_shows_count": len(upcoming_shows), 
  }
  
  print('assembled data list for the artist from DB data')
  print(data)

  return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  # DONE
  form = ArtistForm()

  artistSel = Artist.query.get(artist_id)

  genres_artist = db.session.query(Genresartist).filter(Genresartist.artist_id==artist_id).all()
  genres = []

  for genre in genres_artist:
    genres.append(genre.name)

  artist={
    "id": artistSel.id,
    "name": artistSel.name,
    "genres": genres,
    "city": artistSel.city,
    "state": artistSel.state,
    "phone": artistSel.phone,
    "website": artistSel.website,
    "facebook_link": artistSel.facebook_link,
    "seeking_venue": artistSel.seeking_venue,
    "seeking_description": artistSel.seeking_description,
    "image_link": artistSel.image_link
  }
  # TODO: populate form with fields from artist with ID <artist_id>
  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  # DONE
  # TODO: take values from the form submitted, and update existing
  # artist record with ID <artist_id> using the new attributes
  
  
#  form = ArtistForm()

 # if form.validate() == False:
 #   flash('Submitted Data is not Valid - Revise')
 #   return redirect(url_for('edit_artist', artist_id=artist_id))

  error = False
  
  artist = Artist.query.get(artist_id)
  genres_artist = db.session.query(Genresartist).filter(Genresartist.artist_id==artist_id).all()


  try:
    artist.name = request.form['name']
    artist.city = request.form['city']
    artist.state = request.form['state']
    artist.phone = request.form['phone']
    artist.facebook_link = request.form['facebook_link']
    db.session.commit()
    
    for genreDel in genres_artist:
      db.session.delete(genreDel)
      db.session.commit()

    genres = request.form.getlist('genres')

    for genre in genres:
      genre_entry = Genresartist(name=genre, artist_id=artist_id)
      db.session.add(genre_entry)
      db.session.commit()
  
  except:
    db.session.rollback()
    error = True
    print(sys.exc_info())
    
  finally:
    db.session.close()

  if error:
    flash('Artist was not successfully updated')
    
  if not error:
    flash('Artist was successfully updated!')   

  return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  # DONE
  form = VenueForm()

  venueSel = Venue.query.get(venue_id)

  genres_venue = db.session.query(GenresVen).filter(GenresVen.venue_id==venue_id).all()
  genres = []

  for genre in genres_venue:
    genres.append(genre.name)

  venue={
    "id": venueSel.id,
    "name": venueSel.name,
    "genres": genres,
    "address": venueSel.address,
    "city": venueSel.city,
    "state": venueSel.state,
    "phone": venueSel.phone,
    "website": venueSel.website,
    "facebook_link": venueSel.facebook_link,
    "seeking_talent": venueSel.seeking_talent,
    "seeking_description": venueSel.seeking_description,
    "image_link": venueSel.image_link
  }
  # TODO: populate form with values from venue with ID <venue_id>
  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  # DONE
  # TODO: take values from the form submitted, and update existing
  # venue record with ID <venue_id> using the new attributes
  error = False
  
  venue = Venue.query.get(venue_id)
  genres_venue = db.session.query(GenresVen).filter(GenresVen.venue_id==venue_id).all()


  try:
    venue.name = request.form['name']
    venue.city = request.form['city']
    venue.state = request.form['state']
    venue.address = request.form['address']
    venue.phone = request.form['phone']
    venue.facebook_link = request.form['facebook_link']
    db.session.commit()
    
    for genreDel in genres_venue:
      db.session.delete(genreDel)
      db.session.commit()

    genres = request.form.getlist('genres')

    for genre in genres:
      genre_entry = GenresVen(name=genre, venue_id=venue_id)
      db.session.add(genre_entry)
      db.session.commit()
  
  except:
    db.session.rollback()
    error = True
    print(sys.exc_info())
    
  finally:
    db.session.close()

  if error:
    flash('Venue was not successfully updated')
    
  if not error:
    flash('Venue was successfully updated!')   
    
  return redirect(url_for('show_venue', venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  # DONE
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  # DONE
  # called upon submitting the new artist listing form
  # TODO: insert form data as a new Artist record in the db, instead
  # TODO: modify data to be the data object returned from db insertion

  print('Inside the create_venue_submission() function')
  
  data = request.form
  print('Data from the request.form sent back by webpage')
  print(data)

  error = False

  try:
    name = request.form['name']
    state = request.form['state']
    city = request.form['city']
    phone = request.form['phone']
    genres = request.form.getlist('genres')
    facebook_link = request.form['facebook_link']
    artist = Artist(name=name, state=state, city=city, phone=phone,\
        facebook_link=facebook_link)
    db.session.add(artist)
    db.session.commit()

    id = db.session.query(Artist).filter(Artist.name == name)[0].id
    print('Recently added Artist Id')
    print(id)

    print('Genres from the webpage')
    print(genres)
  
    for genre in genres:
      genre_entry = Genresartist(name=genre, artist_id=id)
      db.session.add(genre_entry)
      db.session.commit()
    
  except:
    db.session.rollback()
    error = True
    print(sys.exc_info())
    
  finally:
    db.session.close()

  if error:
    flash('Artist ' + request.form['name'] + ' was not successfully listed!')
    
  if not error:
    flash('Artist ' + request.form['name'] + ' was successfully listed!')   
    

  # on successful db insert, flash success
  # flash('Artist ' + request.form['name'] + ' was successfully listed!')
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Artist ' + data.name + ' could not be listed.')
  return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # DONE
  # displays list of shows at /shows
  # TODO: replace with real venues data.
  #       num_shows should be aggregated based on number of upcoming shows per venue.
  print('Inside the shows() function')
  shows_db = db.session.query(Shows).join(Artist).join(Venue).all()
  
  data = []

  for show in shows_db:
    data.append({
    "venue_id": show.venue_id,
    "venue_name": show.venue.name,
    "artist_id": show.artist_id,
    "artist_name": show.artist.name,
    "artist_image_link": show.artist.image_link,
    "start_time": show.start_time.strftime('%Y-%m-%d %H:%M:%S')
    })

  print('All the shows data')
  print(data)
  
  return render_template('pages/shows.html', shows=data)

@app.route('/shows/create')
def create_shows():
  # DONE
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  # DONE
  # called to create new shows in the db, upon submitting new show listing form
  # TODO: insert form data as a new Show record in the db, instead
  print('Inside the create_show_submission() function')
  
  data = request.form
  print('Data from the request.form sent back by webpage')
  print(data)

  error = False

  try:
    artist_id = request.form['artist_id']
    venue_id = request.form['venue_id']
    start_time = request.form['start_time']
    show = Shows(artist_id=artist_id, venue_id=venue_id, start_time=start_time)
    db.session.add(show)
    db.session.commit()

  except:
    db.session.rollback()
    error = True
    print(sys.exc_info())
    
  finally:
    db.session.close()

  if error:
    flash('Show was not successfully listed!')
    
  if not error:
    flash('Show was successfully listed!')   


  # on successful db insert, flash success
  # flash('Show was successfully listed!')
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Show could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
  return render_template('pages/home.html')

@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500


if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')

#----------------------------------------------------------------------------#
# Launch.
#----------------------------------------------------------------------------#

# Default port:
if __name__ == '__main__':
    app.run()

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''

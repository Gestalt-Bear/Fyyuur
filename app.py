#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for, abort
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
from flask_migrate import Migrate
from models import db, Venue, Artist, Show, Genre
from config import *
from datetime import datetime

#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db.init_app(app)
migrate = Migrate(app, db)

#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#
# Models are now in models.py

#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
    if isinstance(value, datetime):
        date = value
    else:
        date = dateutil.parser.parse(value)

    if format == 'full':
        format = "EEEE MMMM, d, y 'at' h:mma"
    elif format == 'medium':
        format = "EE MM, dd, y h:mma"
    return babel.dates.format_datetime(date, format, locale='en')

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
  venues = Venue.query.all()
  
  if not venues:
      abort(404)

  # Initialize the city_state_map
  city_state_map = {}
  for venue in venues:
      city_state = (venue.city, venue.state)
      if city_state not in city_state_map:
          city_state_map[city_state] = []
      
      num_upcoming_shows = Show.query.filter(
          Show.venue_id == venue.id,
          Show.start_time > datetime.now()
      ).count()

      city_state_map[city_state].append({
          "id": venue.id,
          "name": venue.name,
          "num_upcoming_shows": num_upcoming_shows
      })

  # Prepare the data for rendering
  data = [
      {
          "city": city,
          "state": state,
          "venues": venues_list
      }
      for (city, state), venues_list in city_state_map.items()   
  ]

  return render_template('pages/venues.html', areas=data)

@app.route('/venues/search', methods=['POST'])
def search_venues():
  search_term = request.form.get('search_term', '')

  venues = Venue.query.filter(Venue.name.ilike(f'%{search_term}%')).all()
  response = {
    "count": len(venues),
    "data": []
  }

  for venue in venues:
    num_upcoming_shows = Show.query.filter(
      Show.venue_id == venue.id,
      Show.start_time > datetime.now()
    ).count()

    response["data"].append({
        "id": venue.id,
        "name": venue.name,
        "num_upcoming_shows": num_upcoming_shows
      })
  return render_template('pages/search_venues.html', results=response, search_term=search_term)

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
    venue = Venue.query.get_or_404(venue_id)
    shows = venue.venue_shows

    genres = [genre.name for genre in venue.genres]

    past_shows = []
    upcoming_shows = []

    for show in venue.shows:
        show_details = {
            "artist_id": show.artist.id,
            "artist_name": show.artist.name,
            "artist_image_link": show.artist.image_link,
            "start_time": show.start_time
        }
        if show.start_time < datetime.now():
            past_shows.append(show_details)
        else:
            upcoming_shows.append(show_details)

    data = {
        "id": venue.id,
        "name": venue.name,
        "genres": genres,
        "address": venue.address,
        "city": venue.city,
        "state": venue.state,
        "phone": venue.phone,
        "website": venue.website_link if hasattr(venue, 'website_link') else None,
        "facebook_link": venue.facebook_link,
        "seeking_talent": venue.seeking_talent,
        "seeking_description": venue.seeking_description,
        "image_link": venue.image_link,
        "past_shows": past_shows,
        "upcoming_shows": upcoming_shows,
        "past_shows_count": len(past_shows),
        "upcoming_shows_count": len(upcoming_shows),
    }

    return render_template('pages/show_venue.html', venue=data)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
    try:
        form_data = request.form
        name = form_data.get('name')
        city = form_data.get('city')
        state = form_data.get('state')
        address = form_data.get('address')
        phone = form_data.get('phone')
        genres = form_data.getlist('genres')
        facebook_link = form_data.get('facebook_link')
        image_link = form_data.get('image_link')
        website_link = form_data.get('website_link')
        seeking_talent = True if form_data.get('seeking_talent') == 'y' else False
        seeking_description = form_data.get('seeking_description')

        new_venue = Venue(
            name=name,
            city=city,
            state=state,
            address=address,
            phone=phone,
            facebook_link=facebook_link,
            image_link=image_link,
            website_link=website_link,
            seeking_talent=seeking_talent,
            seeking_description=seeking_description
        )

        genre_objects = [Genre.query.filter_by(name=genre).first() or Genre(name=genre) for genre in genres]

        new_venue.genres = genre_objects

        db.session.add(new_venue)
        db.session.commit()

        data = {
            "id": new_venue.id,
            "name": new_venue.name,
            "city": new_venue.city,
            "state": new_venue.state
        }
        flash(f"Venue '{new_venue.name}' was successfully listed!")

    except Exception as e:
        db.session.rollback()
        flash(f"An error occurred. Venue '{request.form.get('name')}' could not be listed. Error: {str(e)}")
        return render_template('forms/new_venue.hrml')
    finally:
        db.session.close()
        return render_template('pages/home.html')

@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
    venue = Venue.query.get(venue_id)
    if venue:
        venue.delete() 
        db.session.commit()
        return '',
    else:
        return {'error': 'Venue not found'},

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  raw_data = Artist.query.all()
  
  if not raw_data:
    abort(404)

  data = [{
    "id": artist.id,
    "name": artist.name
  }
    for artist in raw_data
  ]
  return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  search_term = request.form.get('search_term', '').strip()
  artists = Artist.query.filter(Artist.name.ilike(f'(%{search_term}%)')).all()
  data =[
    {
      "id": artist.id,
      "name": artist.name,
      "num_upcoming_shows": Show.query.filter(
        Show.artist_id == artist.id,
        Show.start_time > datetime.now()).count()
    }
    for artist in artists
  ]
  response = {
    "count": len(artists),
    "data": data
  }
  
  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
    artist_data = Artist.query.get_or_404(artist_id)

    genres = [genre.name for genre in artist_data.genres]

    past_shows = []
    upcoming_shows = []

    for show in artist_data.artist_shows:
        show_details = {
            "venue_id": show.venue.id,
            "venue_name": show.venue.name,
            "venue_image_link": show.venue.image_link,
            "start_time": show.start_time
        }
        if show.start_time > datetime.now():
            upcoming_shows.append(show_details)
        else:
            past_shows.append(show_details)

    data = {
        "id": artist_data.id,
        "name": artist_data.name,
        "genres": genres,
        "city": artist_data.city,
        "state": artist_data.state,
        "phone": artist_data.phone,
        "website": artist_data.website,
        "facebook_link": artist_data.facebook_link,
        "seeking_venue": artist_data.seeking_venue,
        "seeking_description": artist_data.seeking_description,
        "image_link": artist_data.image_link,
        "past_shows": past_shows,
        "upcoming_shows": upcoming_shows,
        "past_shows_count": len(past_shows),
        "upcoming_shows_count": len(upcoming_shows)
    }

    return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
    form = ArtistForm()
    artist = Artist.query.get_or_404(artist_id)

    form.name.data = artist.name
    form.genres.data = artist.genres
    form.city.data = artist.city
    form.state.data = artist.state
    form.phone.data = artist.phone
    form.facebook_link.data = artist.facebook_link
    form.image_link.data = artist.image_link
    form.website_link.data = artist.website
    form.seeking_venue.data = artist.seeking_venue
    form.seeking_description.data = artist.seeking_description

    return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
    artist = Artist.query.get_or_404(artist_id)
    form_data = request.form

    if form_data:
        artist.name = form_data.get('name')
        artist.city = form_data.get('city')
        artist.state = form_data.get('state')
        artist.phone = form_data.get('phone')
        artist.image_link = form_data.get('image_link')
        artist.website = form_data.get('website_link')
        artist.facebook_link = form_data.get('facebook_link')
        artist.seeking_venue = form_data.get('seeking_venue') == 'y'
        artist.seeking_description = form_data.get('seeking_description')
        selected_genres = form_data.getlist('genres')
        genre_objects = [Genre.query.filter_by(name=genre).first() or Genre(name=genre) for genre in selected_genres]

        for genre in genre_objects:
            if genre.id is None:
                db.session.add(genre)

        artist.genres = genre_objects

        try:
            db.session.commit()
            flash('Artist updated successfully!')
        except Exception as e:
            db.session.rollback()
            flash(f'An error occurred: {e}')
    
    return redirect(url_for('show_artist', artist_id=artist.id))


@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
    venue = Venue.query.get_or_404(venue_id)
    form = VenueForm()

    form.name.data = venue.name
    form.city.data = venue.city
    form.state.data = venue.state
    form.address.data = venue.address
    form.phone.data = venue.phone
    form.facebook_link.data = venue.facebook_link
    form.image_link.data = venue.image_link
    form.website_link.data = venue.website_link
    form.seeking_talent.data = venue.seeking_talent
    form.seeking_description.data = venue.seeking_description

    form.genres.data = [genre.name for genre in venue.genres]

    return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
    venue = Venue.query.get_or_404(venue_id)
    form_data = request.form

    if form_data:
        venue.name = form_data.get('name')
        venue.city = form_data.get('city')
        venue.state = form_data.get('state')
        venue.address = form_data.get('address')
        venue.phone = form_data.get('phone')
        venue.facebook_link = form_data.get('facebook_link')
        venue.image_link = form_data.get('image_link')
        venue.website_link = form_data.get('website_link')
        venue.seeking_talent = form_data.get('seeking_talent') == 'y'  
        venue.seeking_description = form_data.get('seeking_description')

        selected_genres = form_data.getlist('genres')
        genre_objects = [Genre.query.filter_by(name=genre).first() or Genre(name=genre) for genre in selected_genres]

        for genre in genre_objects:
            if genre.id is None:
                db.session.add(genre)

        venue.genres = genre_objects

        try:
            db.session.commit()
            flash('Venue updated successfully!')
        except Exception as e:
            db.session.rollback()
            flash(f'An error occurred: {e}')

    return redirect(url_for('show_venue', venue_id=venue.id))

#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
    form_data = request.form

    new_artist = Artist(
        name=form_data.get('name'),
        city=form_data.get('city'),
        state=form_data.get('state'),
        phone=form_data.get('phone'),
        facebook_link=form_data.get('facebook_link'),
        image_link=form_data.get('image_link'),
        website=form_data.get('website_link'),
        seeking_venue=form_data.get('seeking_venue') == 'y',
        seeking_description=form_data.get('seeking_description')
    )

    selected_genres = form_data.getlist('genres')
    genre_objects = []

    for genre_name in selected_genres:
        genre = Genre.query.filter_by(name=genre_name).first()
        if genre:
            genre_objects.append(genre)
        else:
            new_genre = Genre(name=genre_name)
            genre_objects.append(new_genre)

    new_artist.genres = genre_objects

    try:
        db.session.add(new_artist)
        db.session.commit()
        flash('Artist ' + new_artist.name + ' was successfully listed!')
    except Exception as e:
        db.session.rollback()
        flash(f'An error occurred. Artist {form_data.get("name")} could not be listed. Error: {str(e)}')
    finally:
        db.session.close()

    return redirect(url_for('index'))

#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  shows = Show.query.all()

  if not shows:
    abort(404)

  data = []
  for show in shows:
      venue = show.venue
      artist = show.artist
      data.append({
          "venue_id": venue.id,
          "venue_name": venue.name,
          "artist_id": artist.id,
          "artist_name": artist.name,
          "artist_image_link": artist.image_link,
          "start_time": show.start_time
      })

  return render_template('pages/shows.html', shows=data)

@app.route('/shows/create')
def create_shows():
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
    form_data = request.form

    venue_id = form_data.get('venue_id')
    artist_id = form_data.get('artist_id')
    start_time = form_data.get('start_time')

    new_show = Show(
        venue_id=venue_id,
        artist_id=artist_id,
        start_time=start_time
    )

    try:
        db.session.add(new_show) 
        db.session.commit()
        flash('Show was successfully listed!') 
    except Exception as e:
        db.session.rollback()
        flash(f'An error occurred. Show could not be listed. Error: {str(e)}')
    finally:
        db.session.close() 

    return redirect(url_for('index'))

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


from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

# Association table for Venue and Genre
venue_genres = db.Table('venue_genres',
    db.Column('venue_id', db.Integer, db.ForeignKey('venue.id', ondelete='CASCADE'), primary_key=True),
    db.Column('genre_id', db.Integer, db.ForeignKey('genre.id', ondelete='CASCADE'), primary_key=True)
)

# Association table for Artist and Genre
artist_genres = db.Table('artist_genres',
    db.Column('artist_id', db.Integer, db.ForeignKey('artist.id', ondelete='CASCADE'), primary_key=True),
    db.Column('genre_id', db.Integer, db.ForeignKey('genre.id', ondelete='CASCADE'), primary_key=True)
)

class Venue(db.Model):
    __tablename__ = 'venue'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    city = db.Column(db.String(120), nullable=False)
    state = db.Column(db.String(120), nullable=False)
    address = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(120), nullable=False)
    image_link = db.Column(db.String(500), nullable=True)
    facebook_link = db.Column(db.String(120), nullable=True)
    seeking_talent = db.Column(db.Boolean, default=False)
    seeking_description = db.Column(db.String(500), nullable=True)
    website_link = db.Column(db.String(500), nullable=True)

    # Relationships
    genres = db.relationship('Genre', secondary=venue_genres, back_populates='venues')
    shows = db.relationship('Show', back_populates='venue', cascade="all, delete-orphan")

class Genre(db.Model):
    __tablename__ = 'genre'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False, unique=True)  # Ensure unique genre names

    # Relationships
    venues = db.relationship('Venue', secondary=venue_genres, back_populates='genres')
    artists = db.relationship('Artist', secondary=artist_genres, back_populates='genres')

class Artist(db.Model):
    __tablename__ = 'artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    image_link = db.Column(db.String(500), nullable=True)
    website = db.Column(db.String(500), nullable=True)
    facebook_link = db.Column(db.String(120), nullable=True)
    seeking_venue = db.Column(db.Boolean, default=False)
    seeking_description = db.Column(db.String, nullable=True)

    # Relationships
    genres = db.relationship('Genre', secondary=artist_genres, back_populates='artists')
    shows = db.relationship('Show', back_populates='artist', cascade="all, delete-orphan")

class Show(db.Model):
    __tablename__ = 'show'

    id = db.Column(db.Integer, primary_key=True)
    venue_id = db.Column(db.Integer, db.ForeignKey('venue.id', ondelete='CASCADE'), nullable=False)
    artist_id = db.Column(db.Integer, db.ForeignKey('artist.id', ondelete='CASCADE'), nullable=False)
    start_time = db.Column(db.DateTime, nullable=False)

    # Relationships
    venue = db.relationship('Venue', back_populates='shows')
    artist = db.relationship('Artist', back_populates='shows')

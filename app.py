from multiprocessing.dummy import active_children
from flask import request, Flask, jsonify, Response
import marshmallow as ma
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy import or_
import uuid

import os

app = Flask(__name__)

database_host_url = os.environ.get('DATABASE_URL')
database_username = os.environ.get('kh_db_username')
database_password = os.environ.get('kh_db_password')
print(database_username)
print(database_password)
database_name = "movies"
app.config['SQLALCHEMY_DATABASE_URI'] = database_host_url
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class Studios(db.Model):
   __tablename__= "studios"
   studio_id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True, nullable=False)
   studio_name = db.Column(db.String(), nullable = False)
   city = db.Column(db.String())
   state = db.Column(db.String())
   active = db.Column(db.Boolean())

   def __init__(self, studio_name, city, state, active=True):
      self.studio_name = studio_name
      self.city = city
      self.state = state
      self.active = active
   
class StudiosSchema(ma.Schema):
   class Meta:
      fields = ['studio_id', 'studio_name', 'city', 'state','active']
   
    
studio_schema = StudiosSchema()
studios_schema = StudiosSchema(many=True)

class Directors(db.Model):
   __tablename__= "directors"
   director_id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True, nullable=False)
   director_name = db.Column(db.String(), nullable = False)
   age = db.Column(db.Integer())
   hometown = db.Column(db.String())
   
   def __init__(self, director_name, age, hometown):
      self.director_name = director_name
      self.age = age
      self.hometown = hometown
   
class DirectorsSchema(ma.Schema):
   class Meta:
      fields = ['director_id', 'director_name', 'age', 'hometown']
   
    
director_schema = DirectorsSchema()
directors_schema = DirectorsSchema(many=True)

class Movies(db.Model):
   __tablename__= "movies"
   movie_id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True, nullable=False)
   movie_title = db.Column(db.String(), nullable = False)
   studio_id = db.Column(UUID(as_uuid=True), db.ForeignKey('studios.studio_id'), nullable=False)
   director_id = db.Column(UUID(as_uuid=True), db.ForeignKey('directors.director_id'), nullable=False)
   release_year = db.Column(db.Integer())
   box_office = db.Column(db.Integer())
   studios =  db.relationship('Studios', backref = 'Movies', lazy=True)
   directors =  db.relationship('Directors', backref = 'Movies', lazy=True)
   
   def __init__(self, movie_title, studio_id, director_id, release_year, box_office):
      self.movie_title = movie_title
      self.studio_id = studio_id
      self.director_id = director_id
      self.release_year = release_year
      self.box_office = box_office
   
class MoviesSchema(ma.Schema):
   class Meta:
      fields = ['movie_id','movie_title', 'studio_id', 'director_id', 'release_year', 'box_office', 'studios', 'directors']
   
   studios = ma.fields.Nested(StudiosSchema(only=('studio_name',)))
   directors = ma.fields.Nested(DirectorsSchema(only=('director_name',)))
    
movie_schema = MoviesSchema()
movies_schema = MoviesSchema(many=True)

@app.route('/director/add', methods=['POST'])
def add_director():
   form = request.form

   fields = ['director_name', 'age', 'hometown']
   req_fields = ['director_name']
   values = []

   for field in fields:
      form_value = form.get(field)
      if form_value in req_fields and form_value == " ":
         return jsonify (f'{field} is required field'), 400
      
      values.append(form_value)

   director_name = form.get('director_name')
   age = form.get('age')
   hometown = form.get('hometown')
   new_director = Directors(director_name, age, hometown)

   db.session.add(new_director)
   db.session.commit()
   
   return jsonify('Director Added'), 200

@app.route('/studio/add', methods=['POST'])
def add_studio():
   form = request.form

   fields = ['studio_name', 'city', 'state']
   req_fields = ['studio_name']
   values = []

   for field in fields:
      form_value = form.get(field)
      if form_value in req_fields and form_value == " ":
         return jsonify (f'{field} is required field'), 400
      
      values.append(form_value)

   studio_name = form.get('studio_name')
   city = form.get('city')
   state = form.get('state')

   new_studio = Studios(studio_name, city, state)

   db.session.add(new_studio)
   db.session.commit()
   
   return jsonify('Studio Added'), 200

@app.route('/movie/add', methods=['POST'])

def add_movie():
   form = request.form

   fields = ['movie_title', 'studio_id', 'director_id', 'release_year', 'box_office']
   req_fields = ['movie_title', 'studio_id', 'director_id']
   values = []

   for field in fields:
      form_value = form.get(field)
      if form_value in req_fields and form_value == " ":
         return jsonify (f'{field} is required field'), 400
      
      values.append(form_value)

   movie_title = form.get('movie_title')
   studio_id = form.get('studio_id')
   director_id = form.get('director_id')
   release_year = form.get('release_year')
   box_office = form.get('box_office')

   new_movie = Movies(movie_title, studio_id, director_id, release_year,box_office)

   db.session.add(new_movie)
   db.session.commit()
   
   return jsonify('Movie Added'), 200

@app.route('/studio/edit/<studio_id>', methods=['PUT'])
def edit_studio(studio_id, studio_name = None, city = None, state = None):
   studio_record = db.session.query(Studios).filter(Studios.studio_id == studio_id).first()
   if not studio_record:
      return ('Studio not found'), 404
   if request:
      form = request.form
      studio_name = form.get('studio_name')
      city = form.get('city')
      state = form.get('state')
   
   if studio_name:
      studio_record.studio_name = studio_name
   if city:
      studio_record.city = city
   if state:
      studio_record.state = state

   db.session.commit()

   return jsonify('Studio Updated'), 201

@app.route('/director/edit/<director_id>', methods=['PUT'])
def edit_director(director_id, director_name = None, age = None, hometown = None):
   director_record = db.session.query(Directors).filter(Directors.director_id == director_id).first()
   if not director_record:
      return ('Director not found'), 404
   if request:
      form = request.form
      director_name = form.get('director_name')
      age = form.get('age')
      hometown = form.get('hometown')
   
   if director_name:
      director_record.director_name = director_name
   if age:
      director_record.age = age
   if hometown:
      director_record.hometown = hometown
   
   db.session.commit()

   return jsonify('Director Updated'), 201

@app.route('/movie/edit/<movie_id>', methods=['PUT'])
def edit_movie(movie_id, movie_title = None, studio_id = None, director_id = None, release_year = None, box_office = None):
   movie_record = db.session.query(Movies).filter(Movies.movie_id == movie_id).first()
   if not movie_record:
      return ('Movie not found'), 404
   if request:
      form = request.form
      movie_title = form.get('movie_title')
      studio_id = form.get('studio_id')
      director_id = form.get('director_id')
      release_year = form.get('release_year')
      box_office = form.get('box_office')
   
   if movie_title:
      movie_record.movie_title = movie_title
   if studio_id:
      movie_record.studio_id = studio_id
   if director_id:
      movie_record.director_id = director_id
   if release_year:
      movie_record.release_year = release_year
   if box_office:
      movie_record.box_office = box_office

   db.session.commit()

   return jsonify('Movie Updated'), 201

@app.route("/studio/delete/<studio_id>", methods=["DELETE"])
def studio_delete_by_id(studio_id):
    studio_data = db.session.query(Studios).filter(Studios.studio_id==studio_id).first()
    
    if studio_data:
        db.session.delete(studio_data)
        db.session.commit()

        return jsonify(f'Studio with studio_id {studio_id} deleted'), 201
    
    else:
      return jsonify(f'Studio with studio_id {studio_id} not found'), 404


@app.route('/director/delete/<director_id>', methods=['DELETE'])
def delete_director(director_id):
   director_data = db.session.query(Directors).filter(Directors.director_id == director_id).first()
   if director_data:
        db.session.delete(director_data)
        db.session.commit()

        return jsonify(f'Director with director_id {director_id} deleted'), 200

   else:
      return jsonify(f'Director with director_id {director_id} not found'), 404

@app.route("/movie/delete/<movie_id>", methods=["DELETE"])
def movie_delete_by_id(movie_id):
    movie_data = db.session.query(Movies).filter(Movies.movie_id==movie_id).first()
    
    if movie_data:
        db.session.delete(movie_data)
        db.session.commit()

        return jsonify(f'Movie with movie_id {movie_id} deleted'), 201
    
    else:
      return jsonify(f'Movie with movie_id {movie_id} not found'), 404

@app.route('/studio/<studio_id>', methods = ['GET'])
def get_studio_by_id(studio_id):
   studio_record = db.session.query(Studios).filter(Studios.studio_id==studio_id).first()

   return jsonify(studio_schema.dump(studio_record)), 200

@app.route('/director/<director_id>', methods = ['GET'])
def get_director_by_id(director_id):
   director_record = db.session.query(Directors).filter(Directors.director_id==director_id).first()

   return jsonify(director_schema.dump(director_record)), 200

@app.route('/movie/<movie_id>', methods = ['GET'])
def get_movie_by_id(movie_id):
   movie_record = db.session.query(Movies).filter(Movies.movie_id==movie_id).first()

   return jsonify(movie_schema.dump(movie_record)), 200

@app.route('/studios/list', methods=['GET'])
def get_all_studios():
   studios_records = db.session.query(Studios).all()

   return jsonify(studios_schema.dump(studios_records)), 200

@app.route('/directors/list', methods=['GET'])
def get_all_directors():
   directors_records = db.session.query(Directors).all()

   return jsonify(directors_schema.dump(directors_records)), 200

@app.route('/movies/list', methods=['GET'])
def get_all_movies():
   user_records = db.session.query(Movies).all()

   return jsonify(movies_schema.dump(user_records)), 200

@app.route('/studios/search/<search_term>', methods=['GET'])
def studios_search(search_term, internal_call=False):
   studio_results = []

   if search_term:
      search_term = search_term.lower()

      studio_results = db.session.query(Studios) \
         .filter(db.or_( \
            db.func.lower(Studios.studio_name).contains(search_term), \
            db.func.lower(Studios.city).contains(search_term), \
            db.func.lower(Studios.state).contains(search_term)))  \
         .all()

   else: 
      return jsonify('No search term'), 400

   if internal_call:
      return studios_schema.dump(studio_results)
   return jsonify(studios_schema.dump(studio_results)), 200

@app.route('/directors/search/<search_term>', methods=['GET'])
def directors_search(search_term, internal_call=False):
   director_results = []

   if search_term:
      search_term = search_term.lower()

      director_results = db.session.query(Directors) \
         .filter(db.or_( \
            db.func.lower(Directors.director_name).contains(search_term), \
            db.func.lower(Directors.hometown).contains(search_term))) \
         .all()

   else: 
      return jsonify('No search term'), 400

   if internal_call:
      return directors_schema.dump(director_results)
   return jsonify(directors_schema.dump(director_results)), 200

@app.route('/movies/search/<search_term>', methods=['GET'])
def movies_search(search_term, internal_call=False):
   movie_results = []

   if search_term:
      search_term = search_term.lower()

      movie_results = db.session.query(Movies) \
         .filter(db.func.lower(Movies.movie_title).contains(search_term)).all()

   else: 
      return jsonify('No search term'), 400

   if internal_call:
      return movies_schema.dump(movie_results)
   return jsonify(movies_schema.dump(movie_results)), 200

@app.route('/search/<search_term>', methods=['GET'])
def get_records_by_search(search_term):
   search_results = {}

   if search_term:
      search_term = search_term.lower()

      search_results['movies'] = movies_search(search_term, True)
      search_results['studios'] = studios_search(search_term, True)
      search_results['directors'] = directors_search(search_term, True)
      
   else: 
      return jsonify('No search term'), 400

   return jsonify(search_results), 200

@app.route('/studio/activate/<studio_id>', methods=['PUT'])
def activate_studio(studio_id):
   studio_record = db.session.query(Studios).filter(Studios.studio_id == studio_id).first()

   if not studio_record:
      return ('Studio not found'), 404
   
   studio_record.active = True
   db.session.commit()

   return jsonify("Studio Activated"), 200

@app.route('/studio/deactivate/<studio_id>', methods=['PUT'])
def deactivate_studio(studio_id):
   studio_record = db.session.query(Studios).filter(Studios.studio_id == studio_id).first()

   if not studio_record:
      return ('Studio not found'), 404
   
   studio_record.active = False
   db.session.commit()

   return jsonify("Studio Deactivated"), 200

@app.route('/director/<director_id>', methods = ['GET'])
def get_director(director_id):
   director_record = db.session.query(Directors).filter(Directors.director_id==director_id).first()

   return jsonify(director_schema.dump(director_record)), 200

@app.route('/studio/<studio_id>', methods = ['GET'])
def get_studio(studio_id):
   studio_record = db.session.query(Studios).filter(Studios.studio_id==studio_id).first()

   return jsonify(studio_schema.dump(studio_record)), 200

@app.route('/movie/<movie_id>', methods = ['GET'])
def get_movie(movie_id):
   movie_record = db.session.query(Movies).filter(Movies.movie_id==movie_id).first()

   return jsonify(movie_schema.dump(movie_record)), 200

if __name__ == '__main__':
   db.create_all()
   app.run()
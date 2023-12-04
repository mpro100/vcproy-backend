from flask import Flask, request, jsonify, redirect, session
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from flask_cors import CORS, cross_origin 

from config import Config


app = Flask(__name__) 
CORS(app)

# app.config["SQLALCHEMY_DATABASE_URI"] = 'mysql://proyfinal:C-123456@localhost/proyecto_final'
app.config["SQLALCHEMY_DATABASE_URI"] = 'mysql://sbsufgb73zendzuj:gksp4q29yqb9to2l@ltnya0pnki2ck9w8.chr7pe7iynqr.eu-west-1.rds.amazonaws.com:3306/ic419hyui39k3orn'

app.config['SECRET_KEY'] = Config.SECRET_KEY 


db= SQLAlchemy(app)
ma = Marshmallow(app)

class Project(db.Model):
    __tablename__ = "projects"
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    proy_cod = db.Column(db.String(20), nullable=False, unique=True)
    proy_name = db.Column(db.String(45))
    proy_description = db.Column(db.String(255))
    start_date = db.Column(db.String(255))
    end_date = db.Column(db.String(255))
    client = db.Column(db.String(255))
    manager = db.Column(db.String(255))
    proy_state = db.Column(db.String(255))


    def __init__(self, proy_cod, proy_name, proy_description, start_date, end_date, client, manager, proy_state):
        self.proy_cod = proy_cod
        self.proy_name = proy_name
        self.proy_description = proy_description
        self.start_date = start_date
        self.end_date = end_date
        self.client = client
        self.manager = manager
        self.proy_state = proy_state

class ProjectSchema(ma.Schema):
    class Meta:
        fields = ('id','proy_cod', 'proy_name', 'proy_description', 'start_date', 'end_date', 'client', 'manager', 'proy_state')

project_schema = ProjectSchema()
projects_schema = ProjectSchema(many=True)


class User(db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True, nullable=False, unique=True)
    username = db.Column(db.String(50), nullable=False, unique=True)
    password = db.Column(db.String(255), nullable = False)

    def __init__(self, username, password):
        self.username = username
        self.password = password


class UserSchema(ma.Schema):
    class Meta:
        fields = ('id', 'username', 'password')

user_schema = UserSchema()
users_schema = UserSchema(many=True)

# Inicio de sesión
@app.route('/login', methods=['POST'])
@cross_origin()
def login():
    if request.content_type != 'application/json':
        return jsonify('Error: Data must be sent as JSON')
    
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    user = User.query.filter_by(username=data['username']).first()

    if user:
        if user.password == password:
            return jsonify({"message": "Login successful", "user_id": user.id})
        else:
            return jsonify({"message": "Invalid credentials"}), 401
        
    
# Cierre de sesión
@app.route('/logout', methods=['POST'])
@cross_origin()
def logout():
   session.pop('loggedin', None)
   session.pop('id', None)
   session.pop('username', None)
   return jsonify({'message': 'Cierre de sesión exitoso'}), 200


#Listar usuarios
@app.route('/userslist',  methods=['GET'])
@cross_origin()
def get_users():
    all_users = db.session.query(User).all()
    data = users_schema.dump(all_users)
    return jsonify(data)

#Borrar usuario
@app.route('/users/<int:user_id>', methods=['DELETE'])
@cross_origin()
def delete_user(user_id):
    user = User.query.get(user_id)
    db.session.delete(user)
    db.session.commit()
    return jsonify({'message': 'Usuario eliminado correctamente'})


# Editar usuario
@app.route('/usersedit/<int:user_id>', methods=['PUT'])
@cross_origin()
def edit_user(user_id):
        data = request.get_json()
        user = User.query.get(user_id)

        if user:
            user.username = data.get('username', user.username)
            user.password = data.get('password', user.password)
            db.session.commit()
            return jsonify({'message': 'Usuario actualizado'}), 200
        else:
            return jsonify({'message': 'Usuario no encontrado'}),404


# Registro nuevo usuario
@app.route('/register', methods=['GET', 'POST'])
@cross_origin()
def register():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
 
    existing_user = User.query.filter_by(username=username).first()
    if existing_user:
        return jsonify({"message": "Usuario ya existente, elija otro usuario"})

    new_user = User(username=username, password=password)
    db.session.add(new_user)
    db.session.commit()
    return jsonify({"message": "Usuario registrado con éxito"}),200


# Listado de proyectos
@app.route('/projects', methods=['GET'])
def get_projects():
    all_projects = Project.query.all()
    projects = projects_schema.dump(all_projects)
    return jsonify(projects)


# Crear proyecto nuevo
@app.route('/project_new', methods=['POST', 'PUT'])
@cross_origin()
def create_project():
        if request.content_type != 'application/json':
            return jsonify('Error: Data must be sent as JSON')
        data = request.get_json()
        proy_cod = data.get('proy_cod')

        existing_project = Project.query.filter_by(proy_cod=proy_cod).first()

        if existing_project:
            return jsonify({"message":'Codigo de proyecto existente, elija otro código' })
            
        new_project = Project(
            proy_cod=data['proy_cod'],
            proy_name=data['proy_name'],
            proy_description=data['proy_description'],
            client=data['client'],
            start_date=data['start_date'],
            end_date=data['end_date'],
            proy_state=data['proy_state'],
            manager=data['manager']
        )
        db.session.add(new_project)
        db.session.commit()
        return jsonify({'message': 'Proyecto creado correctamente'}), 200


# Actualizar un proyecto
@app.route('/projects/<int:project_id>', methods=['GET', 'PUT'])
@cross_origin()
def update_project(project_id):
        if request.content_type != 'application/json':
            return jsonify('Error: Data must be sent as JSON')

        data = request.get_json()
        project = Project.query.get(project_id)
        if project:
            project.proy_cod = data.get('proy_cod', project.proy_cod)
            project.proy_name = data.get('proy_name', project.proy_name)
            project.proy_description = data.get('proy_description', project.proy_description)
            project.client = data.get('client', project.client)
            project.start_date = data.get('start_date', project.start_date)
            project.end_date = data.get('end_date', project.end_date)
            project.proy_state = data.get('proy_state', project.proy_state)
            project.manager = data.get('manager', project.manager)
        db.session.commit()
            
        return jsonify({'message': 'Proyecto actualizado correctamente'}), 200
    
# Eliminar un proyecto
@app.route('/projects/<int:project_id>', methods=['DELETE'])
@cross_origin()
def delete_project(project_id):
        if request.content_type != 'application/json':
            return jsonify('Error: Data must be sent as JSON')

        project = Project.query.get(project_id)

        if project:
            db.session.delete(project)
            db.session.commit()
            return jsonify({'message': 'Proyecto eliminado correctamente'}), 200
        else:
            return jsonify({'message': 'Proyecto no encontrado'}), 404




if __name__ == '__main__':
    app.run(debug=True)
#
# @author Victor Sales
#

from flask import Flask, jsonify, request
from database.database import db
from database.user import Users
from database.exercice import Exercices
from database.user_exercice import UserExercices
from flask_cors import CORS, cross_origin
import os
app = Flask(__name__)
CORS(app)

@app.before_request
def before_request():
    if db.is_closed():
        db.connect()

@app.teardown_request
def teardown_request(exception):
    if not db.is_closed():
        db.close()

@app.route('/api/get_all_users', methods=["GET"])
def get_all_users():
    try:
        users = Users.select()
        usersList = []
        for user in users:
            usersList.append({
                'id' : user.id,
                'name': user.name,
                'email': user.email
            })
        return jsonify(usersList), 200
    except Exception as e:
        return jsonify({'error': str(e)}),400

@app.route('/api/get_users', methods=['GET'])
def get_users():
    page = request.args.get('page',1, type=int)
    itens = request.args.get('itens', 10, type=int)
    try:
        users = Users.select().paginate(page,itens)
        total_users = Users.select().count()

        user_list = []
        for user in users:
            user_list.append({
                'id': user.id,
                'name': user.name,
                'email': user.email,
            })

        return jsonify(user_list), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 400 
    
@app.route('/api/get_user/<int:id>', methods=['GET'])
def get_user(id):
    
    try:
        user = Users.get_by_id(id)
        return jsonify({
            'id': user.id,
            'name': user.name,
            'password': user.password,
            'email': user.email
        })
    except Exception as e:
        return jsonify({'error': str(e)})

@app.route('/api/get_user_by_email_password', methods=['POST'])
def get_user_by_email_password():
    requestBody = request.get_json()
    email = requestBody.get('email')
    password = requestBody.get('password')
    print(request.data)  # Para depuração

    try:
        user = Users.get(Users.email == email, Users.password == password)
        
        return jsonify({
            'id': user.id,
            'name': user.name,
            'password': user.password,
            'email': user.email
        })

    except Users.DoesNotExist:
        return jsonify({'error': 'User not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500


        
@app.route('/api/update_user/<int:id>', methods=['PUT'])
def update_upser(id):
    
    updated_data = request.get_json()
    try:
        user = Users.get_by_id(id)
        user.name = updated_data.get('name', user.name) #Caso não tiver sido passado nenhum valor, manterá o valor presente no banco de dados
        user.password = updated_data.get('password', user.password)
        user.email = updated_data.get('email', user.email)
        user.save()
        return jsonify({'message':'User updated successfully'}),200
    except Exception as e:
        return jsonify({'error': str(e)})

@app.route('/api/create_user', methods=['POST'])
@cross_origin()
def create_user():
    new_user = request.get_json()

    try:
        user_created = Users.create(
            id = new_user.get('id'),
            name = new_user.get('name'),
            password = new_user.get('password'),
            email = new_user.get('email')
        )
            
        return jsonify({'id': user_created.id, 'email': user_created.email}), 200
    except Exception as e:
        return jsonify({'error': str(e)}),400
        
@app.route('/api/delete_user/<int:id>', methods=['DELETE'])
def delete_user(id):
    
    try:
        Users.delete_by_id(id)
        return jsonify({'message':'User deleted successfully'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}),400

@app.route('/api/get_exercices', methods=['GET'])
def get_exercices():
    try:
        exercices = Exercices.select()

        exercices_list = []
        for exercice in exercices:
            exercices_list.append({
                'id': exercice.id,
                'series': exercice.series,
                'repeats': exercice.repeats,
                'days': exercice.days,
            })

        return jsonify(exercices_list), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 400 
    
@app.route('/api/get_exercices/<int:id>', methods=['GET'])
def get_exercice(id):
    
    try:
        exercice = Exercices.get_by_id(id)
        return jsonify({
            'id': exercice.id,
            'series': exercice.series,
            'repeats': exercice.repeats,
            'days': exercice.days,
        })
    
    except Exception as e:
        return jsonify({'error': str(e)})
    
@app.route('/api/update_exercice/<int:id>', methods=['PUT'])
def update_exercice(id):
    
    updated_data = request.get_json()
    try:
        exercice = Exercices.get_by_id(id)
        exercice.series = updated_data.get('series', exercice.series) #Caso não tiver sido passado nenhum valor, manterá o valor presente no banco de dados
        exercice.repeats = updated_data.get('repeats', exercice.repeats)
        exercice.days = updated_data.get('days', exercice.days)
        exercice.save()

        return jsonify({'message':'Exercice updated successfully'}),200
    except Exception as e:
        return jsonify({'error': str(e)})

@app.route('/api/create_exercice', methods=['POST'])
def create_exercice():
    new_exercice = request.get_json()

    try:
        created_exercice = Exercices.create(
            name = new_exercice.get('name'),
            series = new_exercice.get('series'),
            repeats = new_exercice.get('repeats'),
            days = new_exercice.get('days')
        )

        user_id = new_exercice.get('userId') 
        exercice_id = created_exercice.id

        new_user_exercice = UserExercices.create(
            user_id = user_id,
            exercice_id = exercice_id
        )

        return jsonify({
            'id': created_exercice.id,
            'name': created_exercice.name,
            'series': created_exercice.series,
            'repeats': created_exercice.repeats,
            'days': created_exercice.days
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 400

    
@app.route('/api/delete_exercice/<int:id>', methods=['DELETE'])
def delete_exercice(id):
    
    try:
        Exercices.delete_by_id(id)
        return jsonify({'message':'Exercice deleted successfully'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}),400

@app.route('/api/get_users_exercices', methods=['GET'])
def get_users_exercices():
    try:
        users_exercices = UserExercices.select()
        users_exercices_list = []

        for ue in users_exercices:
            users_exercices_list.append({
                'user_id': ue.user.id,
                'exercice_id': ue.exercice.id
            })
        
        return jsonify(users_exercices_list), 200
    except Exception as e:
        return jsonify({"message": str(e)}), 400


@app.route('/api/get_user_exercices/<int:id>', methods=['GET'])
def get_user_exercice(id):
    try:

        user_exercices = UserExercices.select().where(UserExercices.user == id)
        exercices_list = []

        for ue in user_exercices:
            exercices_list.append({
                'exercice_id': ue.exercice.id,
                'name': ue.exercice.name,
                'series': ue.exercice.series,
                'repeats': ue.exercice.repeats,
                'days': ue.exercice.days,
            })

        return jsonify(exercices_list), 200 

    except Exception as e:
        return jsonify({'error': str(e)}), 400

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)), debug=True)

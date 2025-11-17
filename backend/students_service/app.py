from flask import Flask, request, jsonify
from flask_cors import CORS
from datetime import datetime
import uuid

app = Flask(__name__)
CORS(app, resources={
    r"/*": {
        "origins": ["http://localhost:4200", "https://your-frontend-domain.com"],
        "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization"]
    }
})

# Base de datos en memoria para estudiantes
students_db = [
    {
        'id': '1',
        'name': 'Juan Pérez',
        'email': 'juan.perez@email.com',
        'phone': '555-0101',
        'address': 'Calle 123 #45-67',
        'birth_date': '2008-05-15',
        'grade_level': '10',
        'status': 'active',
        'parent_name': 'María Pérez',
        'parent_phone': '555-0102',
        'created_at': '2024-01-15T10:30:00Z',
        'updated_at': '2024-01-15T10:30:00Z'
    },
    {
        'id': '2',
        'name': 'Ana García',
        'email': 'ana.garcia@email.com',
        'phone': '555-0201',
        'address': 'Carrera 456 #78-90',
        'birth_date': '2009-03-22',
        'grade_level': '9',
        'status': 'active',
        'parent_name': 'Carlos García',
        'parent_phone': '555-0202',
        'created_at': '2024-01-16T14:20:00Z',
        'updated_at': '2024-01-16T14:20:00Z'
    },
    {
        'id': '3',
        'name': 'Luis Martínez',
        'email': 'luis.martinez@email.com',
        'phone': '555-0301',
        'address': 'Avenida 789 #12-34',
        'birth_date': '2007-11-08',
        'grade_level': '11',
        'status': 'active',
        'parent_name': 'Elena Martínez',
        'parent_phone': '555-0302',
        'created_at': '2024-01-17T16:45:00Z',
        'updated_at': '2024-01-17T16:45:00Z'
    }
]

@app.route('/')
def home():
    return jsonify({
        'service': 'Students Service',
        'version': '1.0.0',
        'endpoints': {
            'get_all': 'GET /students',
            'get_one': 'GET /students/{id}',
            'create': 'POST /students',
            'update': 'PUT /students/{id}',
            'delete': 'DELETE /students/{id}'
        }
    })

@app.route('/health')
def health():
    return jsonify({'status': 'healthy', 'service': 'students'})

@app.route('/students', methods=['GET'])
def get_students():
    """Obtener todos los estudiantes"""
    try:
        # Filtros opcionales
        grade_level = request.args.get('grade_level')
        status = request.args.get('status', 'active')
        
        filtered_students = students_db
        
        if grade_level:
            filtered_students = [s for s in filtered_students if s.get('grade_level') == grade_level]
        
        if status:
            filtered_students = [s for s in filtered_students if s.get('status') == status]
        
        return jsonify({
            'students': filtered_students,
            'count': len(filtered_students),
            'total': len(students_db)
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/students/<student_id>', methods=['GET'])
def get_student(student_id):
    """Obtener un estudiante por ID"""
    try:
        student = next((s for s in students_db if s['id'] == student_id), None)
        
        if not student:
            return jsonify({'error': 'Student not found'}), 404
        
        return jsonify({'student': student}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/students', methods=['POST'])
def create_student():
    """Crear un nuevo estudiante"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Validar campos requeridos
        required_fields = ['name', 'email', 'phone']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'error': f'Missing required field: {field}'}), 400
        
        # Verificar si el email ya existe
        if any(s['email'] == data['email'] for s in students_db):
            return jsonify({'error': 'Email already exists'}), 400
        
        # Crear estudiante
        new_id = str(len(students_db) + 1)
        timestamp = datetime.utcnow().isoformat() + 'Z'
        
        student = {
            'id': new_id,
            'name': data['name'],
            'email': data['email'],
            'phone': data['phone'],
            'address': data.get('address', ''),
            'birth_date': data.get('birth_date', ''),
            'grade_level': data.get('grade_level', ''),
            'status': data.get('status', 'active'),
            'parent_name': data.get('parent_name', ''),
            'parent_phone': data.get('parent_phone', ''),
            'created_at': timestamp,
            'updated_at': timestamp
        }
        
        students_db.append(student)
        
        return jsonify({
            'message': 'Student created successfully',
            'student': student
        }), 201
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/students/<student_id>', methods=['PUT'])
def update_student(student_id):
    """Actualizar un estudiante"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Buscar estudiante
        student_index = next((i for i, s in enumerate(students_db) if s['id'] == student_id), None)
        
        if student_index is None:
            return jsonify({'error': 'Student not found'}), 404
        
        # Verificar email único (si se está actualizando)
        if 'email' in data:
            existing_email = any(s['email'] == data['email'] and s['id'] != student_id for s in students_db)
            if existing_email:
                return jsonify({'error': 'Email already exists'}), 400
        
        # Actualizar campos
        updatable_fields = ['name', 'email', 'phone', 'address', 'birth_date', 'grade_level', 'status', 'parent_name', 'parent_phone']
        
        for field in updatable_fields:
            if field in data:
                students_db[student_index][field] = data[field]
        
        students_db[student_index]['updated_at'] = datetime.utcnow().isoformat() + 'Z'
        
        return jsonify({
            'message': 'Student updated successfully',
            'student': students_db[student_index]
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/students/<student_id>', methods=['DELETE'])
def delete_student(student_id):
    """Eliminar un estudiante"""
    try:
        student_index = next((i for i, s in enumerate(students_db) if s['id'] == student_id), None)
        
        if student_index is None:
            return jsonify({'error': 'Student not found'}), 404
        
        deleted_student = students_db.pop(student_index)
        
        return jsonify({
            'message': 'Student deleted successfully',
            'deleted_student': deleted_student
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Manejo de errores
@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Endpoint not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal server error'}), 500


@app.route('/student/grades')
def student_grades():
    # Mock: calificaciones recientes y promedio
    grades = [
        {'subject': 'Matemáticas', 'date': '2024-11-15', 'grade': 4.2},
        {'subject': 'Español', 'date': '2024-11-14', 'grade': 4.8},
        {'subject': 'Ciencias', 'date': '2024-11-13', 'grade': 3.9},
        {'subject': 'Inglés', 'date': '2024-11-12', 'grade': 4.5}
    ]
    average = round(sum(g['grade'] for g in grades) / len(grades), 2)
    return jsonify({'recent': grades, 'average': average}), 200


@app.route('/student/notifications')
def student_notifications():
    notes = [
        {'id': 'n1', 'title': 'Boletín del 3er periodo disponible', 'type': 'info'},
        {'id': 'n2', 'title': 'Entrega de proyecto de Ciencias mañana', 'type': 'warning'},
        {'id': 'n3', 'title': 'Reunión de padres el viernes 22', 'type': 'info'}
    ]
    return jsonify({'notifications': notes}), 200


@app.route('/student/schedule-today')
def student_schedule_today():
    schedule = [
        {'time': '7:00 - 7:45', 'subject': 'Matemáticas', 'location': 'A101', 'teacher': 'Prof. García'},
        {'time': '7:45 - 8:30', 'subject': 'Español', 'location': 'A102', 'teacher': 'Prof. López'},
        {'time': '8:30 - 9:15', 'subject': 'Ciencias', 'location': 'Lab 1', 'teacher': 'Prof. Martín'},
        {'time': '10:00 - 10:45', 'subject': 'Inglés', 'location': 'A103', 'teacher': 'Prof. Smith'},
        {'time': '10:45 - 11:30', 'subject': 'Ed. Física', 'location': 'Polideportivo', 'teacher': 'Prof. Ruiz'}
    ]
    return jsonify({'date': datetime.utcnow().strftime('%A, %d de %B de %Y'), 'events': schedule}), 200

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001)
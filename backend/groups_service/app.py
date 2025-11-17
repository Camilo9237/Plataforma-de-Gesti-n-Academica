from flask import Flask, request, jsonify
from flask_cors import CORS
from datetime import datetime
from keycloak import KeycloakOpenID
from functools import wraps


app = Flask(__name__)
app.secret_key = "PlataformaColegios"
CORS(app)

keycloak_openid = KeycloakOpenID(
    server_url="http://localhost:8082",
    client_id="01",
    realm_name="platamaformaInstitucional",
    client_secret_key="2m2KWH4lyYgh9CwoM1y2QI6bFrDjR3OV"
)

def tiene_rol(token_info, cliente_id, rol_requerido):
    try:
        # Revisar roles a nivel de realm
        realm_roles = token_info.get("realm_access", {}).get("roles", [])
        if rol_requerido in realm_roles:
            return True

        # Revisar roles a nivel de cliente (resource_access)
        resource_roles = token_info.get("resource_access", {}).get(cliente_id, {}).get("roles", [])
        if rol_requerido in resource_roles:
            return True

        return False
    except Exception:
        return False

def token_required(rol_requerido):
    def decorator(f):
        @wraps(f)
        def decorated (*args, **kwargs):
            auth_header = request.headers.get('Authorization', None)
            if not auth_header:
                return jsonify({"error": "Token Requerido"}), 401
            
            try:
                token = auth_header.split(" ")[1]
                userinfo = keycloak_openid.decode_token(token)
            except Exception as e:
                return jsonify({"error": "Token inválido o expirado"}), 401
            if not tiene_rol(userinfo, keycloak_openid.client_id, rol_requerido):
                return jsonify({"error": f"Acceso denegado: se requiere el rol '{rol_requerido}'"}), 403
            # guardar información del usuario en 'g' para que la función pueda acceder si lo necesita
            g.userinfo = userinfo
            return f(*args, **kwargs)
        return decorated
    return decorator

# Base de datos en memoria para grupos
groups_db = [
    {
        'id': '1',
        'name': '10-A Matemáticas',
        'grade_level': '10',
        'subject': 'Matemáticas',
        'teacher_id': '1',
        'teacher_name': 'Dr. María López',
        'students_count': 28,
        'max_students': 30,
        'schedule': {
            'days': ['Lunes', 'Miércoles', 'Viernes'],
            'time': '08:00 AM - 09:30 AM'
        },
        'classroom': 'Aula 101',
        'academic_year': '2024',
        'semester': '1',
        'status': 'active',
        'description': 'Matemáticas avanzadas para décimo grado',
        'student_ids': ['1', '2'],  # IDs de estudiantes inscritos
        'created_at': '2024-01-20T09:00:00Z',
        'updated_at': '2024-01-20T09:00:00Z'
    },
    {
        'id': '2',
        'name': '9-B Ciencias Naturales',
        'grade_level': '9',
        'subject': 'Ciencias Naturales',
        'teacher_id': '2',
        'teacher_name': 'Lic. Carlos Rodríguez',
        'students_count': 25,
        'max_students': 28,
        'schedule': {
            'days': ['Martes', 'Jueves'],
            'time': '10:00 AM - 11:30 AM'
        },
        'classroom': 'Laboratorio 1',
        'academic_year': '2024',
        'semester': '1',
        'status': 'active',
        'description': 'Biología y química básica para noveno grado',
        'student_ids': ['3'],
        'created_at': '2024-01-21T10:00:00Z',
        'updated_at': '2024-01-21T10:00:00Z'
    },
    {
        'id': '3',
        'name': '11-A Literatura',
        'grade_level': '11',
        'subject': 'Literatura',
        'teacher_id': '3',
        'teacher_name': 'Prof. Ana Martín',
        'students_count': 22,
        'max_students': 25,
        'schedule': {
            'days': ['Lunes', 'Miércoles', 'Viernes'],
            'time': '02:00 PM - 03:30 PM'
        },
        'classroom': 'Aula 203',
        'academic_year': '2024',
        'semester': '1',
        'status': 'active',
        'description': 'Literatura hispanoamericana y análisis de textos',
        'student_ids': [],
        'created_at': '2024-01-22T14:30:00Z',
        'updated_at': '2024-01-22T14:30:00Z'
    }
]

@app.route('/')
def home():
    return jsonify({
        'service': 'Groups Service',
        'version': '1.0.0',
        'endpoints': {
            'get_all': 'GET /groups',
            'get_one': 'GET /groups/{id}',
            'create': 'POST /groups',
            'update': 'PUT /groups/{id}',
            'delete': 'DELETE /groups/{id}',
            'add_student': 'POST /groups/{id}/students/{student_id}',
            'remove_student': 'DELETE /groups/{id}/students/{student_id}',
            'get_students': 'GET /groups/{id}/students'
        }
    })

@app.route('/health')
def health():
    return jsonify({'status': 'healthy', 'service': 'groups'})

@app.route('/groups', methods=['GET'])
def get_groups():
    """Obtener todos los grupos"""
    try:
        # Filtros opcionales
        grade_level = request.args.get('grade_level')
        subject = request.args.get('subject')
        teacher_id = request.args.get('teacher_id')
        academic_year = request.args.get('academic_year')
        status = request.args.get('status', 'active')
        
        filtered_groups = groups_db
        
        if grade_level:
            filtered_groups = [g for g in filtered_groups if g.get('grade_level') == grade_level]
        
        if subject:
            filtered_groups = [g for g in filtered_groups if g.get('subject', '').lower() == subject.lower()]
        
        if teacher_id:
            filtered_groups = [g for g in filtered_groups if g.get('teacher_id') == teacher_id]
        
        if academic_year:
            filtered_groups = [g for g in filtered_groups if g.get('academic_year') == academic_year]
        
        if status:
            filtered_groups = [g for g in filtered_groups if g.get('status') == status]
        
        return jsonify({
            'groups': filtered_groups,
            'count': len(filtered_groups),
            'total': len(groups_db)
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/groups/<group_id>', methods=['GET'])
def get_group(group_id):
    """Obtener un grupo por ID"""
    try:
        group = next((g for g in groups_db if g['id'] == group_id), None)
        
        if not group:
            return jsonify({'error': 'Group not found'}), 404
        
        return jsonify({'group': group}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/groups', methods=['POST'])
def create_group():
    """Crear un nuevo grupo"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Validar campos requeridos
        required_fields = ['name', 'grade_level', 'subject', 'teacher_id', 'teacher_name']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'error': f'Missing required field: {field}'}), 400
        
        # Verificar si el nombre ya existe
        if any(g['name'] == data['name'] for g in groups_db):
            return jsonify({'error': 'Group name already exists'}), 400
        
        # Crear grupo
        new_id = str(len(groups_db) + 1)
        timestamp = datetime.utcnow().isoformat() + 'Z'
        
        group = {
            'id': new_id,
            'name': data['name'],
            'grade_level': data['grade_level'],
            'subject': data['subject'],
            'teacher_id': data['teacher_id'],
            'teacher_name': data['teacher_name'],
            'students_count': 0,
            'max_students': data.get('max_students', 30),
            'schedule': data.get('schedule', {}),
            'classroom': data.get('classroom', ''),
            'academic_year': data.get('academic_year', '2024'),
            'semester': data.get('semester', '1'),
            'status': data.get('status', 'active'),
            'description': data.get('description', ''),
            'student_ids': [],
            'created_at': timestamp,
            'updated_at': timestamp
        }
        
        groups_db.append(group)
        
        return jsonify({
            'message': 'Group created successfully',
            'group': group
        }), 201
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/groups/<group_id>', methods=['PUT'])
def update_group(group_id):
    """Actualizar un grupo"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Buscar grupo
        group_index = next((i for i, g in enumerate(groups_db) if g['id'] == group_id), None)
        
        if group_index is None:
            return jsonify({'error': 'Group not found'}), 404
        
        # Verificar nombre único (si se está actualizando)
        if 'name' in data:
            existing_name = any(g['name'] == data['name'] and g['id'] != group_id for g in groups_db)
            if existing_name:
                return jsonify({'error': 'Group name already exists'}), 400
        
        # Actualizar campos
        updatable_fields = ['name', 'grade_level', 'subject', 'teacher_id', 'teacher_name', 'max_students', 'schedule', 'classroom', 'academic_year', 'semester', 'status', 'description']
        
        for field in updatable_fields:
            if field in data:
                groups_db[group_index][field] = data[field]
        
        groups_db[group_index]['updated_at'] = datetime.utcnow().isoformat() + 'Z'
        
        return jsonify({
            'message': 'Group updated successfully',
            'group': groups_db[group_index]
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/groups/<group_id>', methods=['DELETE'])
def delete_group(group_id):
    """Eliminar un grupo"""
    try:
        group_index = next((i for i, g in enumerate(groups_db) if g['id'] == group_id), None)
        
        if group_index is None:
            return jsonify({'error': 'Group not found'}), 404
        
        deleted_group = groups_db.pop(group_index)
        
        return jsonify({
            'message': 'Group deleted successfully',
            'deleted_group': deleted_group
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/groups/<group_id>/students', methods=['GET'])
def get_group_students(group_id):
    """Obtener estudiantes de un grupo"""
    try:
        group = next((g for g in groups_db if g['id'] == group_id), None)
        
        if not group:
            return jsonify({'error': 'Group not found'}), 404
        
        return jsonify({
            'group_id': group_id,
            'group_name': group['name'],
            'student_ids': group.get('student_ids', []),
            'students_count': group.get('students_count', 0),
            'max_students': group.get('max_students', 30)
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/groups/<group_id>/students/<student_id>', methods=['POST'])
def add_student_to_group(group_id, student_id):
    """Agregar estudiante a un grupo"""
    try:
        group_index = next((i for i, g in enumerate(groups_db) if g['id'] == group_id), None)
        
        if group_index is None:
            return jsonify({'error': 'Group not found'}), 404
        
        group = groups_db[group_index]
        
        # Verificar si el grupo no está lleno
        if group['students_count'] >= group.get('max_students', 30):
            return jsonify({'error': 'Group is full'}), 400
        
        # Verificar si el estudiante ya está en el grupo
        if student_id in group.get('student_ids', []):
            return jsonify({'error': 'Student already in group'}), 400
        
        # Agregar estudiante
        if 'student_ids' not in group:
            group['student_ids'] = []
        
        group['student_ids'].append(student_id)
        group['students_count'] = len(group['student_ids'])
        group['updated_at'] = datetime.utcnow().isoformat() + 'Z'
        
        return jsonify({
            'message': 'Student added to group successfully',
            'group_id': group_id,
            'student_id': student_id,
            'students_count': group['students_count']
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/groups/<group_id>/students/<student_id>', methods=['DELETE'])
def remove_student_from_group(group_id, student_id):
    """Remover estudiante de un grupo"""
    try:
        group_index = next((i for i, g in enumerate(groups_db) if g['id'] == group_id), None)
        
        if group_index is None:
            return jsonify({'error': 'Group not found'}), 404
        
        group = groups_db[group_index]
        
        # Verificar si el estudiante está en el grupo
        if student_id not in group.get('student_ids', []):
            return jsonify({'error': 'Student not in group'}), 404
        
        # Remover estudiante
        group['student_ids'].remove(student_id)
        group['students_count'] = len(group['student_ids'])
        group['updated_at'] = datetime.utcnow().isoformat() + 'Z'
        
        return jsonify({
            'message': 'Student removed from group successfully',
            'group_id': group_id,
            'student_id': student_id,
            'students_count': group['students_count']
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

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5003)
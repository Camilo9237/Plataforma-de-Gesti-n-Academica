from flask import Flask, request, jsonify, g
from flask_cors import CORS
import os
from datetime import datetime
from functools import wraps

try:
    from keycloak import KeycloakOpenID
except Exception:
    KeycloakOpenID = None

app = Flask(__name__)
app.secret_key = os.getenv('APP_SECRET', 'plataforma_secret')
CORS(app)

# Keycloak config
KEYCLOAK_SERVER = os.getenv('KEYCLOAK_SERVER_URL', 'http://localhost:8082')
KEYCLOAK_CLIENT_ID = os.getenv('KEYCLOAK_CLIENT_ID', '01')
KEYCLOAK_REALM = os.getenv('KEYCLOAK_REALM', 'plataformaInstitucional')
KEYCLOAK_CLIENT_SECRET = os.getenv('KEYCLOAK_CLIENT_SECRET', None)

keycloak_openid = None
if KeycloakOpenID is not None:
    try:
        keycloak_openid = KeycloakOpenID(
            server_url=KEYCLOAK_SERVER,
            client_id=KEYCLOAK_CLIENT_ID,
            realm_name=KEYCLOAK_REALM,
            client_secret_key=KEYCLOAK_CLIENT_SECRET
        )
    except Exception:
        keycloak_openid = None


def tiene_rol(token_info, cliente_id, rol_requerido):
    """Comprueba si los claims del token contienen el rol requerido.

    Busca tanto en realm_access como en resource_access[cliente_id].
    """
    try:
        realm_roles = token_info.get('realm_access', {}).get('roles', [])
        if rol_requerido in realm_roles:
            return True
        resource_roles = token_info.get('resource_access', {}).get(cliente_id, {}).get('roles', [])
        if rol_requerido in resource_roles:
            return True
        return False
    except Exception:
        return False


def token_required(rol_requerido):
    """Decorador que valida la presencia del token y del rol requerido.

    - Si Keycloak no está disponible, permite tokens mock para desarrollo.
    - Si Keycloak está disponible, intenta decodificar el token y comprobar el rol.
    """
    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            # Modo desarrollo: permitir token mock
            if keycloak_openid is None:
                auth = request.headers.get('Authorization', '')
                if auth.startswith('Bearer mock-access-token') or auth.startswith('Bearer mock-token-for-admin'):
                    g.userinfo = {'sub': 'admin', 'roles': ['administrador']}
                    return f(*args, **kwargs)
                return jsonify({'error': 'Keycloak no configurado'}), 500

            auth_header = request.headers.get('Authorization', None)
            if not auth_header:
                return jsonify({'error': 'Token Requerido'}), 401
            try:
                token = auth_header.split(' ')[1]
                # decode_token puede requerir parámetros según la versión; usamos la forma básica
                userinfo = keycloak_openid.decode_token(token)
            except Exception:
                return jsonify({'error': 'Token inválido o expirado'}), 401

            if not tiene_rol(userinfo, KEYCLOAK_CLIENT_ID, rol_requerido):
                return jsonify({'error': f"Acceso denegado: se requiere el rol '{rol_requerido}'"}), 403

            g.userinfo = userinfo
            return f(*args, **kwargs)

        return decorated

    return decorator


@app.route('/')
def home():
    return jsonify({'service': 'Administrator Service', 'version': '1.0.0'})


@app.route('/health')
def health():
    return jsonify({'status': 'healthy', 'service': 'administrator'})


@app.route('/dashboard')
@token_required('administrador')
def dashboard():
    # ejemplo original para administradores (mantener compatibilidad)
    return jsonify({'message': 'Administrator dashboard', 'time': datetime.utcnow().isoformat() + 'Z'})


@app.route('/admin/stats')
@token_required('administrador')
def admin_stats():
    # Datos mock para el panel administrativo
    data = {
        'total_students': 1247,
        'enrollment_complete_pct': 92.3,
        'active_campuses': 3,
        'active_teachers': 78
    }
    return jsonify(data)


@app.route('/admin/pending-tasks')
@token_required('administrador')
def admin_pending_tasks():
    tasks = [
        {'id': 't1', 'title': 'Revisión de matrículas pendientes', 'count': 15, 'severity': 'urgent'},
        {'id': 't2', 'title': 'Aprobación de certificados', 'count': 8, 'severity': 'normal'},
        {'id': 't3', 'title': 'Validación de documentos', 'count': 23, 'severity': 'normal'},
        {'id': 't4', 'title': 'Asignación de docentes', 'count': 5, 'severity': 'urgent'}
    ]
    return jsonify({'tasks': tasks})


@app.route('/admin/campuses')
@token_required('administrador')
def admin_campuses():
    campuses = [
        {'name': 'Sede Principal', 'students': 567, 'occupancy_pct': 89, 'status': 'Activa'},
        {'name': 'Sede Norte', 'students': 423, 'occupancy_pct': 76, 'status': 'Activa'},
        {'name': 'Sede Sur', 'students': 257, 'occupancy_pct': 45, 'status': 'Activa'}
    ]
    return jsonify({'campuses': campuses})


@app.route('/admin/recent-stats')
@token_required('administrador')
def admin_recent_stats():
    recent = [
        {'month': 'Nov 2024', 'enrollments': 45, 'dropouts': 3, 'avg': 4.1},
        {'month': 'Oct 2024', 'enrollments': 32, 'dropouts': 7, 'avg': 4.0},
        {'month': 'Sep 2024', 'enrollments': 52, 'dropouts': 5, 'avg': 4.2}
    ]
    return jsonify({'recent': recent})


def _extract_roles_from_userinfo(userinfo):
    roles = set()
    # caso mock (g.userinfo puede contener 'roles')
    if isinstance(userinfo, dict):
        if 'roles' in userinfo and isinstance(userinfo.get('roles'), (list, tuple)):
            for r in userinfo.get('roles', []):
                roles.add(str(r))

        # realm access
        realm_roles = userinfo.get('realm_access', {}).get('roles', []) if userinfo.get('realm_access') else []
        for r in realm_roles:
            roles.add(str(r))

        # resource access: iterar recursos
        resource_access = userinfo.get('resource_access', {}) or {}
        for client, info in resource_access.items():
            for r in info.get('roles', []):
                roles.add(str(r))

    return roles


def _get_primary_role(userinfo):
    # prioridad: administrador > docente > estudiante
    roles = _extract_roles_from_userinfo(userinfo)
    if 'administrador' in roles or 'admin' in roles:
        return 'administrador'
    if 'docente' in roles or 'teacher' in roles:
        return 'docente'
    if 'estudiante' in roles or 'student' in roles:
        return 'estudiante'
    return None


def _extract_username(userinfo):
    if not isinstance(userinfo, dict):
        return None
    # common claim names
    return userinfo.get('preferred_username') or userinfo.get('username') or userinfo.get('sub')


def auth_required_any(f):
    """Decorador que exige autenticación (cualquier rol), útil para dashboards generales."""
    @wraps(f)
    def decorated(*args, **kwargs):
        # development mock if keycloak not configured
        allowed_roles = {'administrador', 'docente', 'estudiante'}
        if keycloak_openid is None:
            auth = request.headers.get('Authorization', '')
            if auth.startswith('Bearer mock-access-token'):
                g.userinfo = {'sub': 'dev-user', 'roles': ['estudiante']}
            elif auth.startswith('Bearer mock-token-for-admin'):
                g.userinfo = {'sub': 'admin', 'roles': ['administrador']}
            elif auth.startswith('Bearer mock-token-for-docente'):
                g.userinfo = {'sub': 'doc1', 'roles': ['docente']}
            else:
                return jsonify({'error': 'Keycloak no configurado o token mock faltante'}), 500

            # validar rol permitido
            primary = _get_primary_role(g.userinfo)
            if not primary or primary not in allowed_roles:
                return jsonify({'error': 'Acceso denegado: rol no autorizado', 'role': primary}), 403
            return f(*args, **kwargs)

        auth_header = request.headers.get('Authorization', None)
        if not auth_header:
            return jsonify({'error': 'Token Requerido'}), 401
        try:
            token = auth_header.split(' ')[1]
            userinfo = keycloak_openid.decode_token(token)
        except Exception:
            return jsonify({'error': 'Token inválido o expirado'}), 401

        # validar que el usuario tenga un rol reconocido y permitido
        primary = _get_primary_role(userinfo)
        if not primary or primary not in allowed_roles:
            return jsonify({'error': 'Acceso denegado: rol no autorizado', 'role': primary}), 403

        g.userinfo = userinfo
        return f(*args, **kwargs)

    return decorated


@app.route('/dashboard-general')
@auth_required_any
def dashboard_general():
    """Endpoint general que saluda según el rol del usuario autenticado.

    Responde con JSON: { message, role, user, time }
    """
    userinfo = getattr(g, 'userinfo', {}) or {}
    role = _get_primary_role(userinfo) or 'usuario'
    user = _extract_username(userinfo) or 'desconocido'
    mensaje = f"Bienvenido {role}" if role != 'usuario' else 'Bienvenido usuario'
    return jsonify({'message': mensaje, 'role': role, 'user': user, 'time': datetime.utcnow().isoformat() + 'Z'})


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5003, debug=True)

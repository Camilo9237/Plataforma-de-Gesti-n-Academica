// ==========================================
//   SCRIPT UNIFICADO DE INICIALIZACIÓN
//   Modelo completo con todas las colecciones
// ==========================================

use colegio;

print("🗑️  Eliminando base de datos anterior...");
db.dropDatabase();
print("✔ Base de datos 'colegio' eliminada");

use colegio;

// ==========================================
//   COLECCIÓN: USUARIOS
// ==========================================
db.createCollection("usuarios", {
  validator: {
    $jsonSchema: {
      bsonType: "object",
      required: ["correo", "rol"],
      properties: {
        correo: { bsonType: "string" },
        rol: {
          enum: ["estudiante", "docente", "administrador"],
          description: "Rol del usuario"
        },
        nombres: { bsonType: "string" },
        apellidos: { bsonType: "string" },
        documento: { bsonType: "string" },
        telefono: { bsonType: "string" },
        activo: { bsonType: "bool" },
        creado_en: { bsonType: "timestamp" },
        keycloak_id: { bsonType: "string" },
        
        // CAMPOS ESPECÍFICOS DE ESTUDIANTE
        codigo_est: { bsonType: "string" },
        id_grupo: { 
          bsonType: "objectId",
          description: "Referencia al grupo del estudiante"
        },
        fecha_nacimiento: { bsonType: "date" },
        direccion: { bsonType: "string" },
        nombre_acudiente: { bsonType: "string" },
        telefono_acudiente: { bsonType: "string" },
        
        // CAMPOS ESPECÍFICOS DE DOCENTE
        codigo_docente: { bsonType: "string" },
        especialidad: { bsonType: "string" },
        titulo: { bsonType: "string" },
        fecha_ingreso: { bsonType: "date" }
      }
    }
  }
});

db.usuarios.createIndex({ correo: 1 }, { unique: true });
db.usuarios.createIndex({ rol: 1 });
db.usuarios.createIndex({ codigo_est: 1 }, { unique: true, sparse: true });
db.usuarios.createIndex({ codigo_docente: 1 }, { unique: true, sparse: true });
db.usuarios.createIndex({ id_grupo: 1 });
db.usuarios.createIndex({ keycloak_id: 1 });

print("✔ Colección 'usuarios' creada");

// ==========================================
//   COLECCIÓN: GRUPOS
// ==========================================
db.createCollection("grupos", {
  validator: {
    $jsonSchema: {
      bsonType: "object",
      required: ["nombre_grupo", "grado", "jornada", "anio_lectivo"],
      properties: {
        nombre_grupo: { bsonType: "string" },
        grado: { bsonType: "string" },
        jornada: { enum: ["mañana", "tarde"] },
        anio_lectivo: { bsonType: "string" },
        id_director_grupo: { bsonType: "objectId" },
        director_info: { bsonType: "object" },
        capacidad_max: { bsonType: "int" },
        estudiantes_actuales: { bsonType: "int" },
        salon_principal: { bsonType: "string" },
        activo: { bsonType: "bool" },
        creado_en: { bsonType: "timestamp" }
      }
    }
  }
});

db.grupos.createIndex({ nombre_grupo: 1, anio_lectivo: 1 }, { unique: true });
db.grupos.createIndex({ grado: 1, jornada: 1 });

print("✔ Colección 'grupos' creada");

// ==========================================
//   COLECCIÓN: CURSOS (Asignaturas por grado)
// ==========================================
db.createCollection("cursos", {
  validator: {
    $jsonSchema: {
      bsonType: "object",
      required: ["nombre_curso", "codigo_curso", "grado", "area"],
      properties: {
        nombre_curso: { bsonType: "string" },
        codigo_curso: { bsonType: "string" },
        grado: { bsonType: "string" },
        area: { bsonType: "string" },
        descripcion: { bsonType: "string" },
        creditos: { bsonType: "int" },
        intensidad_horaria_semanal: { bsonType: "int" },
        activo: { bsonType: "bool" },
        creado_en: { bsonType: "timestamp" }
      }
    }
  }
});

db.cursos.createIndex({ codigo_curso: 1 }, { unique: true });
db.cursos.createIndex({ grado: 1, area: 1 });

print("✔ Colección 'cursos' creada");

// ==========================================
//   COLECCIÓN: ASIGNACIONES_DOCENTES
// ==========================================
db.createCollection("asignaciones_docentes", {
  validator: {
    $jsonSchema: {
      bsonType: "object",
      required: ["id_grupo", "id_curso", "id_docente", "periodo", "anio_lectivo"],
      properties: {
        id_grupo: { bsonType: "objectId" },
        id_curso: { bsonType: "objectId" },
        id_docente: { bsonType: "objectId" },
        periodo: { enum: ["1", "2", "3", "4"] },
        anio_lectivo: { bsonType: "string" },
        grupo_info: { bsonType: "object" },
        curso_info: { bsonType: "object" },
        docente_info: { bsonType: "object" },
        salon_asignado: { bsonType: "string" },
        activo: { bsonType: "bool" },
        creado_en: { bsonType: "timestamp" }
      }
    }
  }
});

db.asignaciones_docentes.createIndex({ id_grupo: 1, id_curso: 1, periodo: 1 }, { unique: true });
db.asignaciones_docentes.createIndex({ id_docente: 1, periodo: 1 });

print("✔ Colección 'asignaciones_docentes' creada");

// ==========================================
//   COLECCIÓN: HORARIOS
// ==========================================
db.createCollection("horarios", {
  validator: {
    $jsonSchema: {
      bsonType: "object",
      required: ["grupo", "año_lectivo", "horario"],
      properties: {
        grupo: { bsonType: "string" },
        año_lectivo: { bsonType: "string" },
        horario: {
          bsonType: "array",
          items: {
            bsonType: "object",
            required: ["hora_inicio", "hora_fin", "dia"],
            properties: {
              hora_inicio: { bsonType: "string" },
              hora_fin: { bsonType: "string" },
              dia: { enum: ["lunes", "martes", "miércoles", "jueves", "viernes"] },
              id_curso: { bsonType: "objectId" },
              curso_info: { bsonType: "object" }
            }
          }
        },
        creado_en: { bsonType: "timestamp" }
      }
    }
  }
});

db.horarios.createIndex({ grupo: 1, año_lectivo: 1 }, { unique: true });

print("✔ Colección 'horarios' creada");

// ==========================================
//   COLECCIÓN: MATRICULAS
// ==========================================
db.createCollection("matriculas", {
  validator: {
    $jsonSchema: {
      bsonType: "object",
      required: ["id_estudiante", "id_grupo", "anio_lectivo"],
      properties: {
        id_estudiante: { bsonType: "objectId" },
        id_grupo: { bsonType: "objectId" },
        anio_lectivo: { bsonType: "string" },
        fecha_matricula: { bsonType: "timestamp" },
        estado: { enum: ["activa", "inactiva", "retirada"] },
        estudiante_info: { bsonType: "object" },
        grupo_info: { bsonType: "object" },
        calificaciones: {
          bsonType: "array",
          items: {
            bsonType: "object",
            properties: {
              id_asignacion: { bsonType: "objectId" },
              periodo: { enum: ["1", "2", "3", "4"] },
              notas: {
                bsonType: "array",
                items: {
                  bsonType: "object",
                  properties: {
                    tipo: { bsonType: "string" },
                    nota: { bsonType: ["double", "int"] },
                    nota_maxima: { bsonType: ["double", "int"] },
                    peso: { bsonType: ["double", "int"] },
                    fecha_eval: { bsonType: "date" },
                    comentarios: { bsonType: "string" }
                  }
                }
              }
            }
          }
        },
        observaciones: { bsonType: "string" },
        creado_en: { bsonType: "timestamp" }
      }
    }
  }
});

db.matriculas.createIndex({ id_estudiante: 1, anio_lectivo: 1 }, { unique: true });
db.matriculas.createIndex({ id_estudiante: 1, id_grupo: 1 });
db.matriculas.createIndex({ estado: 1 });

print("✔ Colección 'matriculas' creada");

// ==========================================
//   COLECCIÓN: OBSERVACIONES
// ==========================================
db.createCollection("observaciones", {
  validator: {
    $jsonSchema: {
      bsonType: "object",
      required: ["id_estudiante", "id_docente", "tipo", "descripcion", "fecha"],
      properties: {
        id_estudiante: { bsonType: "objectId" },
        id_docente: { bsonType: "objectId" },
        id_curso: { bsonType: "objectId" },
        tipo: { enum: ["positiva", "negativa", "neutral"] },
        categoria: { enum: ["academica", "disciplinaria", "convivencia", "participacion", "otra"] },
        descripcion: { bsonType: "string" },
        fecha: { bsonType: "date" },
        seguimiento: { bsonType: "string" },
        gravedad: { enum: ["leve", "moderada", "grave"] },
        notificado_acudiente: { bsonType: "bool" },
        fecha_notificacion: { bsonType: "date" },
        estudiante_info: { bsonType: "object" },
        docente_info: { bsonType: "object" },
        curso_info: { bsonType: "object" },
        creado_en: { bsonType: "timestamp" }
      }
    }
  }
});

db.observaciones.createIndex({ id_estudiante: 1, fecha: -1 });
db.observaciones.createIndex({ id_docente: 1 });
db.observaciones.createIndex({ tipo: 1, categoria: 1 });

print("✔ Colección 'observaciones' creada");

// ==========================================
//   COLECCIÓN: ASISTENCIA
// ==========================================
db.createCollection("asistencia", {
  validator: {
    $jsonSchema: {
      bsonType: "object",
      required: ["id_curso", "id_docente", "fecha", "registros"],
      properties: {
        id_curso: { bsonType: "objectId" },
        id_docente: { bsonType: "objectId" },
        id_asignacion: { bsonType: "objectId" },
        fecha: { bsonType: "date" },
        periodo: { enum: ["1", "2", "3", "4"] },
        registros: {
          bsonType: "array",
          items: {
            bsonType: "object",
            properties: {
              id_estudiante: { bsonType: "objectId" },
              estudiante_info: { bsonType: "object" },
              estado: { enum: ["presente", "ausente", "tarde", "excusa"] },
              observaciones: { bsonType: "string" }
            }
          }
        },
        curso_info: { bsonType: "object" },
        creado_en: { bsonType: "timestamp" }
      }
    }
  }
});

db.asistencia.createIndex({ id_curso: 1, fecha: 1 });
db.asistencia.createIndex({ id_docente: 1, fecha: -1 });

print("✔ Colección 'asistencia' creada");

// ==========================================
//   COLECCIÓN: REPORTES
// ==========================================
db.createCollection("reportes");
print("✔ Colección 'reportes' creada");

// ==========================================
//   COLECCIÓN: CERTIFICADOS
// ==========================================
db.createCollection("certificados");
print("✔ Colección 'certificados' creada");

// ==========================================
//   COLECCIÓN: AUDITORÍA
// ==========================================
db.createCollection("auditoria");
db.auditoria.createIndex({ id_usuario: 1, fecha: -1 });
print("✔ Colección 'auditoria' creada");

print("\n✅ Esquema de base de datos creado exitosamente\n");

// ==========================================
//   INSERTAR DATOS DE PRUEBA
// ==========================================

print("🌱 Insertando datos de prueba...\n");

// ===== ADMINISTRADORES =====
const admin1 = db.usuarios.insertOne({
  correo: "admin@colegio.edu.co",
  rol: "administrador",
  nombres: "Admin",
  apellidos: "Sistema",
  telefono: "3001234567",
  documento: "1234567890",
  activo: true,
  creado_en: Timestamp()
}).insertedId;

print("✔ Administrador creado");

// ===== DOCENTES =====
const docentes = [
  {
    correo: "juan.perez@colegio.edu.co",
    nombres: "Juan Carlos",
    apellidos: "Pérez Gómez",
    documento: "10123456",
    codigo_docente: "DOC001",
    especialidad: "Matemáticas"
  },
  {
    correo: "maria.lopez@colegio.edu.co",
    nombres: "María Fernanda",
    apellidos: "López Martínez",
    documento: "10234567",
    codigo_docente: "DOC002",
    especialidad: "Lengua Castellana"
  },
  {
    correo: "carlos.garcia@colegio.edu.co",
    nombres: "Carlos Alberto",
    apellidos: "García Rodríguez",
    documento: "10345678",
    codigo_docente: "DOC003",
    especialidad: "Ciencias Naturales"
  },
  {
    correo: "ana.martinez@colegio.edu.co",
    nombres: "Ana María",
    apellidos: "Martínez Torres",
    documento: "10456789",
    codigo_docente: "DOC004",
    especialidad: "Inglés"
  },
  {
    correo: "luis.rodriguez@colegio.edu.co",
    nombres: "Luis Eduardo",
    apellidos: "Rodríguez Castro",
    documento: "10567890",
    codigo_docente: "DOC005",
    especialidad: "Educación Física"
  },
  {
    correo: "diana.torres@colegio.edu.co",
    nombres: "Diana Patricia",
    apellidos: "Torres Méndez",
    documento: "10678901",
    codigo_docente: "DOC006",
    especialidad: "Ciencias Sociales"
  }
];

const docentesIds = {};
docentes.forEach(doc => {
  const id = db.usuarios.insertOne({
    ...doc,
    rol: "docente",
    telefono: "310" + Math.floor(Math.random() * 10000000),
    titulo: "Licenciado",
    fecha_ingreso: ISODate("2020-01-15"),
    activo: true,
    creado_en: Timestamp()
  }).insertedId;
  
  docentesIds[doc.codigo_docente] = id;
});

print("✔ 6 Docentes creados");

// ===== CURSOS (Asignaturas por grado) =====
const asignaturas = [
  { nombre: "Matemáticas", codigo: "MAT", area: "matemáticas", creditos: 4, intensidad: 5 },
  { nombre: "Español", codigo: "ESP", area: "lenguaje", creditos: 4, intensidad: 5 },
  { nombre: "Inglés", codigo: "ING", area: "inglés", creditos: 3, intensidad: 4 },
  { nombre: "Ciencias Naturales", codigo: "CIE", area: "ciencias", creditos: 3, intensidad: 4 },
  { nombre: "Ciencias Sociales", codigo: "SOC", area: "sociales", creditos: 3, intensidad: 4 },
  { nombre: "Educación Física", codigo: "EDF", area: "educación_física", creditos: 2, intensidad: 2 }
];

const cursosIds = {};

["10", "11"].forEach(grado => {
  asignaturas.forEach(asig => {
    const codigo = asig.codigo + grado;
    const id = db.cursos.insertOne({
      nombre_curso: asig.nombre,
      codigo_curso: codigo,
      grado: grado,
      area: asig.area,
      descripcion: `${asig.nombre} para grado ${grado}°`,
      creditos: NumberInt(asig.creditos),
      intensidad_horaria_semanal: NumberInt(asig.intensidad),
      activo: true,
      creado_en: Timestamp()
    }).insertedId;
    
    cursosIds[codigo] = id;
  });
});

print("✔ 12 Asignaturas creadas");

// ===== GRUPOS =====
const grupos = [
  { nombre: "10°A", grado: "10", jornada: "mañana", director: docentesIds["DOC001"], capacidad: 40, salon: "Aula 201" },
  { nombre: "10°B", grado: "10", jornada: "mañana", director: docentesIds["DOC002"], capacidad: 38, salon: "Aula 202" },
  { nombre: "11°A", grado: "11", jornada: "mañana", director: docentesIds["DOC003"], capacidad: 35, salon: "Aula 301" },
  { nombre: "11°B", grado: "11", jornada: "mañana", director: docentesIds["DOC004"], capacidad: 35, salon: "Aula 302" }
];

const gruposIds = {};

grupos.forEach(grupo => {
  const director = db.usuarios.findOne({ _id: grupo.director });
  
  const id = db.grupos.insertOne({
    nombre_grupo: grupo.nombre,
    grado: grupo.grado,
    jornada: grupo.jornada,
    anio_lectivo: "2025",
    id_director_grupo: grupo.director,
    director_info: {
      nombres: director.nombres,
      apellidos: director.apellidos,
      codigo_docente: director.codigo_docente
    },
    capacidad_max: NumberInt(grupo.capacidad),
    estudiantes_actuales: NumberInt(0),
    salon_principal: grupo.salon,
    activo: true,
    creado_en: Timestamp()
  }).insertedId;
  
  gruposIds[grupo.nombre] = id;
});

print("✔ 4 Grupos creados");

// ===== ESTUDIANTES =====
const estudiantes = [
  { codigo: "EST001", nombres: "Carlos", apellidos: "Ramírez López", doc: "1001234567", grupo: "10°A", nacimiento: "2010-05-20", acudiente: "Luis Ramírez", tel_acudiente: "3005551111" },
  { codigo: "EST002", nombres: "Ana", apellidos: "Torres Gómez", doc: "1001234568", grupo: "10°A", nacimiento: "2010-09-12", acudiente: "Marta Torres", tel_acudiente: "3015552222" },
  { codigo: "EST003", nombres: "Sofía", apellidos: "Méndez Castro", doc: "1001234569", grupo: "10°A", nacimiento: "2010-02-08", acudiente: "Roberto Méndez", tel_acudiente: "3025553333" },
  { codigo: "EST004", nombres: "Miguel", apellidos: "Santos Díaz", doc: "1001234570", grupo: "10°B", nacimiento: "2010-11-15", acudiente: "Patricia Santos", tel_acudiente: "3035554444" },
  { codigo: "EST005", nombres: "Laura", apellidos: "González Ruiz", doc: "1001234571", grupo: "10°B", nacimiento: "2010-03-22", acudiente: "Sandra González", tel_acudiente: "3045555555" },
  { codigo: "EST006", nombres: "David", apellidos: "Martínez Vargas", doc: "1001234572", grupo: "10°B", nacimiento: "2010-07-14", acudiente: "Jorge Martínez", tel_acudiente: "3055556666" },
  { codigo: "EST007", nombres: "Valentina", apellidos: "López Parra", doc: "1001234573", grupo: "11°A", nacimiento: "2009-01-09", acudiente: "María López", tel_acudiente: "3065557777" },
  { codigo: "EST008", nombres: "Santiago", apellidos: "Herrera Ortiz", doc: "1001234574", grupo: "11°A", nacimiento: "2009-10-25", acudiente: "Carlos Herrera", tel_acudiente: "3075558888" },
  { codigo: "EST009", nombres: "Isabella", apellidos: "Castro Rojas", doc: "1001234575", grupo: "11°A", nacimiento: "2009-04-18", acudiente: "Andrea Castro", tel_acudiente: "3085559999" },
  { codigo: "EST010", nombres: "Andrés", apellidos: "Morales Silva", doc: "1001234576", grupo: "11°B", nacimiento: "2009-12-03", acudiente: "Luis Morales", tel_acudiente: "3095550000" },
  { codigo: "EST011", nombres: "Camila", apellidos: "Rivera Pérez", doc: "1001234577", grupo: "11°B", nacimiento: "2009-06-21", acudiente: "Patricia Rivera", tel_acudiente: "3105551111" },
  { codigo: "EST012", nombres: "Juan", apellidos: "Díaz Ramírez", doc: "1001234578", grupo: "11°B", nacimiento: "2009-08-30", acudiente: "Roberto Díaz", tel_acudiente: "3115552222" }
];

const estudiantesIds = {};

estudiantes.forEach(est => {
  const id = db.usuarios.insertOne({
    correo: `${est.nombres.toLowerCase()}.${est.apellidos.split(' ')[0].toLowerCase()}@colegio.edu.co`,
    rol: "estudiante",
    nombres: est.nombres,
    apellidos: est.apellidos,
    documento: est.doc,
    codigo_est: est.codigo,
    id_grupo: gruposIds[est.grupo],
    fecha_nacimiento: ISODate(est.nacimiento),
    direccion: `Calle ${Math.floor(Math.random() * 50)} #${Math.floor(Math.random() * 50)}-${Math.floor(Math.random() * 100)}`,
    nombre_acudiente: est.acudiente,
    telefono_acudiente: est.tel_acudiente,
    telefono: "320" + Math.floor(Math.random() * 10000000),
    activo: true,
    creado_en: Timestamp()
  }).insertedId;
  
  estudiantesIds[est.codigo] = { id: id, grupo: est.grupo };
  
  db.grupos.updateOne(
    { _id: gruposIds[est.grupo] },
    { $inc: { estudiantes_actuales: 1 } }
  );
});

print("✔ 12 Estudiantes creados");

// ===== ASIGNACIONES DOCENTES =====
const asignacionesConfig = [
  { grupo: "10°A", curso: "MAT10", docente: "DOC001" },
  { grupo: "10°A", curso: "ESP10", docente: "DOC002" },
  { grupo: "10°A", curso: "ING10", docente: "DOC004" },
  { grupo: "10°A", curso: "CIE10", docente: "DOC003" },
  { grupo: "10°A", curso: "SOC10", docente: "DOC006" },
  { grupo: "10°A", curso: "EDF10", docente: "DOC005" },
  { grupo: "10°B", curso: "MAT10", docente: "DOC001" },
  { grupo: "10°B", curso: "ESP10", docente: "DOC002" },
  { grupo: "10°B", curso: "ING10", docente: "DOC004" },
  { grupo: "10°B", curso: "CIE10", docente: "DOC003" },
  { grupo: "10°B", curso: "SOC10", docente: "DOC006" },
  { grupo: "10°B", curso: "EDF10", docente: "DOC005" },
  { grupo: "11°A", curso: "MAT11", docente: "DOC001" },
  { grupo: "11°A", curso: "ESP11", docente: "DOC002" },
  { grupo: "11°A", curso: "ING11", docente: "DOC004" },
  { grupo: "11°A", curso: "CIE11", docente: "DOC003" },
  { grupo: "11°A", curso: "SOC11", docente: "DOC006" },
  { grupo: "11°A", curso: "EDF11", docente: "DOC005" },
  { grupo: "11°B", curso: "MAT11", docente: "DOC001" },
  { grupo: "11°B", curso: "ESP11", docente: "DOC002" },
  { grupo: "11°B", curso: "ING11", docente: "DOC004" },
  { grupo: "11°B", curso: "CIE11", docente: "DOC003" },
  { grupo: "11°B", curso: "SOC11", docente: "DOC006" },
  { grupo: "11°B", curso: "EDF11", docente: "DOC005" }
];

const asignacionesIds = {};

asignacionesConfig.forEach(asig => {
  const grupo = db.grupos.findOne({ nombre_grupo: asig.grupo });
  const curso = db.cursos.findOne({ codigo_curso: asig.curso });
  const docente = db.usuarios.findOne({ codigo_docente: asig.docente });
  
  const asignacionId = db.asignaciones_docentes.insertOne({
    id_grupo: grupo._id,
    id_curso: curso._id,
    id_docente: docente._id,
    periodo: "1",
    anio_lectivo: "2025",
    grupo_info: {
      nombre_grupo: grupo.nombre_grupo,
      grado: grupo.grado,
      jornada: grupo.jornada
    },
    curso_info: {
      nombre_curso: curso.nombre_curso,
      codigo_curso: curso.codigo_curso,
      area: curso.area
    },
    docente_info: {
      nombres: docente.nombres,
      apellidos: docente.apellidos,
      codigo_docente: docente.codigo_docente,
      especialidad: docente.especialidad
    },
    salon_asignado: grupo.salon_principal,
    activo: true,
    creado_en: Timestamp()
  }).insertedId;
  
  const key = `${asig.grupo}_${asig.curso}`;
  asignacionesIds[key] = asignacionId;
});

print("✔ 24 Asignaciones docentes creadas");

// ===== MATRÍCULAS CON CALIFICACIONES =====
function generarCalificaciones(asignacionId, periodo) {
  const tipos = ["Parcial", "Taller", "Quiz", "Proyecto"];
  const notas = [];
  
  tipos.forEach((tipo, index) => {
    const nota = parseFloat((Math.random() * 2 + 3).toFixed(1)); // 3.0 - 5.0
    notas.push({
      tipo: tipo,
      nota: nota,
      nota_maxima: 5.0,
      peso: index === 3 ? 0.25 : 0.25,
      fecha_eval: new Date(2025, parseInt(periodo) - 1, 5 + (index * 7)),
      comentarios: nota >= 4.0 ? "Buen desempeño" : "Debe mejorar"
    });
  });
  
  return {
    id_asignacion: asignacionId,
    periodo: periodo,
    notas: notas
  };
}

Object.entries(estudiantesIds).forEach(([codigo, data]) => {
  const estudiante = db.usuarios.findOne({ codigo_est: codigo });
  const grupo = db.grupos.findOne({ _id: estudiante.id_grupo });
  
  // Obtener asignaciones del grupo
  const asignacionesGrupo = db.asignaciones_docentes.find({
    id_grupo: grupo._id,
    periodo: "1"
  }).toArray();
  
  // Generar calificaciones para cada asignación
  const calificaciones = asignacionesGrupo.map(asig => 
    generarCalificaciones(asig._id, "1")
  );
  
  db.matriculas.insertOne({
    id_estudiante: estudiante._id,
    id_grupo: grupo._id,
    anio_lectivo: "2025",
    fecha_matricula: Timestamp(),
    estado: "activa",
    estudiante_info: {
      nombres: estudiante.nombres,
      apellidos: estudiante.apellidos,
      codigo_est: estudiante.codigo_est,
      documento: estudiante.documento
    },
    grupo_info: {
      nombre_grupo: grupo.nombre_grupo,
      grado: grupo.grado,
      jornada: grupo.jornada
    },
    calificaciones: calificaciones,
    observaciones: "Matrícula regular 2025",
    creado_en: Timestamp()
  });
});

print("✔ 12 Matrículas con calificaciones creadas");

// ===== HORARIOS =====
const horasClases = [
  "07:00-08:00",
  "08:00-09:00",
  "09:00-10:00",
  "10:30-11:30", // Descanso 10:00-10:30
  "11:30-12:30"
];

const dias = ["lunes", "martes", "miércoles", "jueves", "viernes"];

["10°A", "10°B", "11°A", "11°B"].forEach(nombreGrupo => {
  const grupo = db.grupos.findOne({ nombre_grupo: nombreGrupo });
  const asignacionesGrupo = db.asignaciones_docentes.find({
    id_grupo: grupo._id,
    periodo: "1"
  }).toArray();
  
  const horario = [];
  let asignacionIndex = 0;
  
  dias.forEach(dia => {
    horasClases.forEach(hora => {
      const [inicio, fin] = hora.split('-');
      const asignacion = asignacionesGrupo[asignacionIndex % asignacionesGrupo.length];
      
      horario.push({
        hora_inicio: inicio,
        hora_fin: fin,
        dia: dia,
        id_curso: asignacion.id_curso,
        curso_info: {
          nombre_curso: asignacion.curso_info.nombre_curso,
          codigo_curso: asignacion.curso_info.codigo_curso,
          docente_nombres: `${asignacion.docente_info.nombres} ${asignacion.docente_info.apellidos}`,
          salon: asignacion.salon_asignado
        }
      });
      
      asignacionIndex++;
    });
  });
  
  db.horarios.insertOne({
    grupo: nombreGrupo,
    año_lectivo: "2025",
    horario: horario,
    creado_en: Timestamp()
  });
});

print("✔ 4 Horarios creados");

// ===== OBSERVACIONES =====
const tiposObservaciones = [
  { tipo: "positiva", categoria: "academica", descripcion: "Excelente participación en clase", gravedad: null },
  { tipo: "positiva", categoria: "convivencia", descripcion: "Demuestra valores de respeto y solidaridad", gravedad: null },
  { tipo: "negativa", categoria: "disciplinaria", descripcion: "Interrumpe constantemente la clase", gravedad: "leve" },
  { tipo: "negativa", categoria: "academica", descripcion: "No entrega tareas", gravedad: "moderada" }
];

// Crear 2 observaciones por estudiante
Object.entries(estudiantesIds).forEach(([codigo, data]) => {
  const estudiante = db.usuarios.findOne({ codigo_est: codigo });
  const grupo = db.grupos.findOne({ _id: estudiante.id_grupo });
  const asignacionesGrupo = db.asignaciones_docentes.find({
    id_grupo: grupo._id
  }).toArray();
  
  // Seleccionar 2 observaciones aleatorias
  for (let i = 0; i < 2; i++) {
    const obsTemplate = tiposObservaciones[Math.floor(Math.random() * tiposObservaciones.length)];
    const asignacion = asignacionesGrupo[Math.floor(Math.random() * asignacionesGrupo.length)];
    const docente = db.usuarios.findOne({ _id: asignacion.id_docente });
    
    db.observaciones.insertOne({
      id_estudiante: estudiante._id,
      id_docente: docente._id,
      id_curso: asignacion.id_curso,
      tipo: obsTemplate.tipo,
      categoria: obsTemplate.categoria,
      descripcion: obsTemplate.descripcion,
      fecha: new Date(2025, Math.floor(Math.random() * 3), Math.floor(Math.random() * 28) + 1),
      seguimiento: obsTemplate.tipo === "negativa" ? "Citación a acudiente programada" : "Felicitación verbal",
      gravedad: obsTemplate.gravedad,
      notificado_acudiente: obsTemplate.tipo === "negativa",
      fecha_notificacion: obsTemplate.tipo === "negativa" ? new Date() : null,
      estudiante_info: {
        nombres: estudiante.nombres,
        apellidos: estudiante.apellidos,
        codigo_est: estudiante.codigo_est
      },
      docente_info: {
        nombres: docente.nombres,
        apellidos: docente.apellidos,
        especialidad: docente.especialidad
      },
      curso_info: asignacion.curso_info,
      creado_en: Timestamp()
    });
  }
});

print("✔ 24 Observaciones creadas");

// ===== ASISTENCIA =====
// Crear registros de asistencia para los últimos 5 días
for (let dia = 0; dia < 5; dia++) {
  const fecha = new Date();
  fecha.setDate(fecha.getDate() - dia);
  
  // Para cada asignación crear un registro de asistencia
  const asignaciones = db.asignaciones_docentes.find({ periodo: "1" }).toArray();
  
  asignaciones.forEach(asignacion => {
    const grupo = db.grupos.findOne({ _id: asignacion.id_grupo });
    const estudiantes_grupo = db.usuarios.find({
      id_grupo: grupo._id,
      rol: "estudiante"
    }).toArray();
    
    const registros = estudiantes_grupo.map(est => {
      const estados = ["presente", "presente", "presente", "ausente", "tarde"];
      const estado = estados[Math.floor(Math.random() * estados.length)];
      
      return {
        id_estudiante: est._id,
        estudiante_info: {
          nombres: est.nombres,
          apellidos: est.apellidos,
          codigo_est: est.codigo_est
        },
        estado: estado,
        observaciones: estado === "ausente" ? "Falta justificada" : ""
      };
    });
    
    db.asistencia.insertOne({
      id_curso: asignacion.id_curso,
      id_docente: asignacion.id_docente,
      id_asignacion: asignacion._id,
      fecha: fecha,
      periodo: "1",
      registros: registros,
      curso_info: asignacion.curso_info,
      creado_en: Timestamp()
    });
  });
}

print("✔ Registros de asistencia creados");

// ===== AUDITORÍA =====
db.auditoria.insertOne({
  id_usuario: admin1,
  accion: "INICIALIZAR_BD_COMPLETA",
  entidad_afectada: "sistema",
  detalles: {
    mensaje: "Base de datos inicializada con estructura completa",
    colecciones: [
      "usuarios", "grupos", "cursos", "asignaciones_docentes",
      "horarios", "matriculas", "observaciones", "asistencia"
    ]
  },
  fecha: Timestamp()
});

print("✔ Registro de auditoría creado");

print("\n✅ BASE DE DATOS INICIALIZADA COMPLETAMENTE\n");

print("📊 Resumen de datos creados:");
print(`   - Usuarios: ${db.usuarios.countDocuments()}`);
print(`   - Grupos: ${db.grupos.countDocuments()}`);
print(`   - Cursos: ${db.cursos.countDocuments()}`);
print(`   - Asignaciones: ${db.asignaciones_docentes.countDocuments()}`);
print(`   - Matrículas: ${db.matriculas.countDocuments()}`);
print(`   - Horarios: ${db.horarios.countDocuments()}`);
print(`   - Observaciones: ${db.observaciones.countDocuments()}`);
print(`   - Asistencias: ${db.asistencia.countDocuments()}`);
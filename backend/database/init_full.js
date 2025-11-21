// ==========================================
//   SCRIPT UNIFICADO DE INICIALIZACIÓN
//   Reinicia, crea esquema e inserta datos
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
      required: ["correo", "rol", "nombres", "apellidos"],
      properties: {
        correo: { bsonType: "string", description: "Correo único del usuario" },
        rol: {
          enum: ["administrador", "docente", "estudiante"],
          description: "Rol del usuario"
        },
        nombres: { bsonType: "string" },
        apellidos: { bsonType: "string" },
        creado_en: { bsonType: "timestamp" },
        activo: { bsonType: "bool" },
        telefono: { bsonType: "string" },
        documento: { bsonType: "string" },
        codigo_empleado: { bsonType: "string" },
        especialidad: { bsonType: "string" },
        fecha_ingreso: { bsonType: "date" },
        codigo_est: { bsonType: "string" },
        fecha_nacimiento: { bsonType: "date" },
        direccion: { bsonType: "string" },
        nombre_acudiente: { bsonType: "string" },
        telefono_acudiente: { bsonType: "string" }
      }
    }
  }
});

db.usuarios.createIndex({ correo: 1 }, { unique: true });
db.usuarios.createIndex({ rol: 1 });
db.usuarios.createIndex({ codigo_empleado: 1 }, { sparse: true });
db.usuarios.createIndex({ codigo_est: 1 }, { sparse: true });
db.usuarios.createIndex({ documento: 1 }, { sparse: true });

print("✔ Colección 'usuarios' creada");

// ==========================================
//   COLECCIÓN: CURSOS
// ==========================================
db.createCollection("cursos", {
  validator: {
    $jsonSchema: {
      bsonType: "object",
      required: ["nombre_curso", "codigo_curso", "periodo"],
      properties: {
        nombre_curso: { bsonType: "string" },
        codigo_curso: { bsonType: "string" },
        id_docente: { bsonType: "objectId" },
        grado: { bsonType: "string" },
        periodo: {
          enum: ["1", "2", "3", "4"],
          description: "Periodo académico"
        },
        capacidad_max: { bsonType: "int" },
        activo: { bsonType: "bool" },
        docente_info: {
          bsonType: "object",
          properties: {
            nombres: { bsonType: "string" },
            apellidos: { bsonType: "string" },
            especialidad: { bsonType: "string" }
          }
        }
      }
    }
  }
});

db.cursos.createIndex({ codigo_curso: 1 }, { unique: true });
db.cursos.createIndex({ id_docente: 1 });
db.cursos.createIndex({ grado: 1, periodo: 1 });

print("✔ Colección 'cursos' creada");

// ==========================================
//   COLECCIÓN: MATRICULAS
// ==========================================
db.createCollection("matriculas", {
  validator: {
    $jsonSchema: {
      bsonType: "object",
      required: ["id_estudiante", "id_curso"],
      properties: {
        id_estudiante: { bsonType: "objectId" },
        id_curso: { bsonType: "objectId" },
        fecha_matricula: { bsonType: "timestamp" },
        estado: {
          enum: ["activo", "finalizado", "retirado", "pendiente"],
          description: "Estado de la matrícula"
        },
        calificaciones: {
          bsonType: "array",
          items: {
            bsonType: "object",
            required: ["tipo", "nota", "peso", "fecha_eval", "periodo"],
            properties: {
              tipo: { bsonType: "string" },
              nota: { bsonType: ["double", "int"] },
              nota_maxima: { bsonType: ["double", "int"] },
              peso: { bsonType: ["double", "int"] },
              fecha_eval: { bsonType: "date" },
              periodo: { bsonType: "string", enum: ["1", "2", "3", "4"] },
              comentarios: { bsonType: "string" }
            }
          }
        },
        estudiante_info: {
          bsonType: "object",
          properties: {
            nombres: { bsonType: "string" },
            apellidos: { bsonType: "string" },
            codigo_est: { bsonType: "string" }
          }
        },
        curso_info: {
          bsonType: "object",
          properties: {
            nombre_curso: { bsonType: "string" },
            codigo_curso: { bsonType: "string" },
            grado: { bsonType: "string" },
            periodo: { bsonType: "string" }
          }
        }
      }
    }
  }
});

db.matriculas.createIndex({ id_estudiante: 1, id_curso: 1 }, { unique: true });
db.matriculas.createIndex({ id_estudiante: 1 });
db.matriculas.createIndex({ id_curso: 1 });
db.matriculas.createIndex({ estado: 1 });

print("✔ Colección 'matriculas' creada");

// ==========================================
//   COLECCIÓN: REPORTES
// ==========================================
db.createCollection("reportes", {
  validator: {
    $jsonSchema: {
      bsonType: "object",
      required: ["tipo_reporte", "generado_por"],
      properties: {
        tipo_reporte: {
          enum: ["boletin", "resumen_curso", "rendimiento_docente", "certificado"]
        },
        generado_por: { bsonType: "objectId" },
        id_estudiante: { bsonType: "objectId" },
        id_curso: { bsonType: "objectId" },
        id_docente: { bsonType: "objectId" },
        fecha_generado: { bsonType: "timestamp" },
        datos_reporte: {
          bsonType: "object",
          description: "Datos específicos del reporte"
        }
      }
    }
  }
});

db.reportes.createIndex({ tipo_reporte: 1 });
db.reportes.createIndex({ fecha_generado: 1 });

print("✔ Colección 'reportes' creada");

// ==========================================
//   COLECCIÓN: CERTIFICADOS
// ==========================================
db.createCollection("certificados", {
  validator: {
    $jsonSchema: {
      bsonType: "object",
      required: ["id_estudiante", "tipo_certificado", "fecha_emision"],
      properties: {
        id_estudiante: { bsonType: "objectId" },
        id_curso: { bsonType: "objectId" },
        tipo_certificado: { bsonType: "string" },
        fecha_emision: { bsonType: "date" },
        emitido_por: { bsonType: "objectId" },
        datos_certificado: {
          bsonType: "object"
        }
      }
    }
  }
});

db.certificados.createIndex({ id_estudiante: 1 });
db.certificados.createIndex({ fecha_emision: 1 });

print("✔ Colección 'certificados' creada");

// ==========================================
//   COLECCIÓN: AUDITORÍA
// ==========================================
db.createCollection("auditoria", {
  validator: {
    $jsonSchema: {
      bsonType: "object",
      required: ["accion"],
      properties: {
        id_usuario: { bsonType: "objectId" },
        accion: { bsonType: "string" },
        id_entidad: { bsonType: "objectId" },
        detalles: { bsonType: ["string", "object"] },
        fecha: { bsonType: "timestamp" },
        entidad_afectada: { bsonType: "string" },
        ip: { bsonType: "string" }
      }
    }
  }
});

db.auditoria.createIndex({ id_usuario: 1 });
db.auditoria.createIndex({ accion: 1 });
db.auditoria.createIndex({ fecha: 1 });

print("✔ Colección 'auditoria' creada");

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
        fecha: { bsonType: "date" },
        periodo: { bsonType: "string" },
        registros: {
          bsonType: "array",
          items: {
            bsonType: "object",
            required: ["id_estudiante", "estado"],
            properties: {
              id_estudiante: { bsonType: "objectId" },
              estudiante_info: {
                bsonType: "object",
                properties: {
                  nombres: { bsonType: "string" },
                  apellidos: { bsonType: "string" },
                  codigo_est: { bsonType: "string" }
                }
              },
              estado: {
                enum: ["presente", "ausente", "tarde", "excusa"]
              },
              observaciones: { bsonType: "string" }
            }
          }
        },
        curso_info: {
          bsonType: "object",
          properties: {
            nombre_curso: { bsonType: "string" },
            codigo_curso: { bsonType: "string" },
            grado: { bsonType: "string" }
          }
        },
        creado_en: { bsonType: "timestamp" },
        actualizado_en: { bsonType: "timestamp" }
      }
    }
  }
});

db.asistencia.createIndex({ id_curso: 1, fecha: 1 });
db.asistencia.createIndex({ id_docente: 1 });
db.asistencia.createIndex({ fecha: -1 });

print("✔ Colección 'asistencia' creada");

// ==========================================
//   COLECCIÓN: OBSERVACIONES
// ==========================================
db.createCollection("observaciones", {
  validator: {
    $jsonSchema: {
      bsonType: "object",
      required: ["id_estudiante", "id_docente", "id_curso", "tipo", "descripcion", "fecha"],
      properties: {
        id_estudiante: { bsonType: "objectId" },
        id_docente: { bsonType: "objectId" },
        id_curso: { bsonType: "objectId" },
        tipo: {
          enum: ["positiva", "negativa", "neutral"]
        },
        descripcion: { bsonType: "string" },
        fecha: { bsonType: "date" },
        seguimiento: { bsonType: "string" },
        categoria: { 
          enum: ["academica", "disciplinaria", "convivencia", "participacion", "otra"]
        },
        gravedad: {
          enum: ["leve", "moderada", "grave"]
        },
        notificado_acudiente: { bsonType: "bool" },
        fecha_notificacion: { bsonType: "date" },
        estudiante_info: {
          bsonType: "object",
          properties: {
            nombres: { bsonType: "string" },
            apellidos: { bsonType: "string" },
            codigo_est: { bsonType: "string" }
          }
        },
        docente_info: {
          bsonType: "object",
          properties: {
            nombres: { bsonType: "string" },
            apellidos: { bsonType: "string" },
            especialidad: { bsonType: "string" }
          }
        },
        curso_info: {
          bsonType: "object",
          properties: {
            nombre_curso: { bsonType: "string" },
            codigo_curso: { bsonType: "string" },
            grado: { bsonType: "string" }
          }
        },
        archivos_adjuntos: {
          bsonType: "array",
          items: {
            bsonType: "object",
            properties: {
              nombre: { bsonType: "string" },
              url: { bsonType: "string" },
              tipo: { bsonType: "string" }
            }
          }
        },
        creado_en: { bsonType: "timestamp" },
        actualizado_en: { bsonType: "timestamp" }
      }
    }
  }
});

db.observaciones.createIndex({ id_estudiante: 1 });
db.observaciones.createIndex({ id_docente: 1 });
db.observaciones.createIndex({ id_curso: 1 });
db.observaciones.createIndex({ tipo: 1 });
db.observaciones.createIndex({ fecha: -1 });
db.observaciones.createIndex({ categoria: 1 });

print("✔ Colección 'observaciones' creada");
print("✅ Esquema de base de datos creado exitosamente\n");

// ==========================================
//   INSERTAR DATOS DE PRUEBA
// ==========================================

print("🌱 Insertando datos de prueba...\n");

// ===== ADMINISTRADORES =====
const admin1 = db.usuarios.insertOne({
  correo: "admin1@colegio.edu.co",
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
const docente1 = db.usuarios.insertOne({
  correo: "juan.perez@colegio.edu.co",
  rol: "docente",
  nombres: "Juan",
  apellidos: "Pérez",
  telefono: "3105551234",
  documento: "10123456",
  codigo_empleado: "DOC001",
  especialidad: "Matemáticas",
  fecha_ingreso: ISODate("2020-01-15"),
  activo: true,
  creado_en: Timestamp()
}).insertedId;

const docente2 = db.usuarios.insertOne({
  correo: "maria.lopez@colegio.edu.co",
  rol: "docente",
  nombres: "María",
  apellidos: "López",
  telefono: "3115552233",
  documento: "10234567",
  codigo_empleado: "DOC002",
  especialidad: "Español",
  fecha_ingreso: ISODate("2019-03-10"),
  activo: true,
  creado_en: Timestamp()
}).insertedId;

const docente3 = db.usuarios.insertOne({
  correo: "carlos.garcia@colegio.edu.co",
  rol: "docente",
  nombres: "Carlos",
  apellidos: "García",
  telefono: "3125553344",
  documento: "10345678",
  codigo_empleado: "DOC003",
  especialidad: "Ciencias",
  fecha_ingreso: ISODate("2021-08-01"),
  activo: true,
  creado_en: Timestamp()
}).insertedId;

const docente4 = db.usuarios.insertOne({
  correo: "ana.martinez@colegio.edu.co",
  rol: "docente",
  nombres: "Ana",
  apellidos: "Martínez",
  telefono: "3135555555",
  documento: "10456789",
  codigo_empleado: "DOC004",
  especialidad: "Inglés",
  fecha_ingreso: ISODate("2020-08-01"),
  activo: true,
  creado_en: Timestamp()
}).insertedId;

const docente5 = db.usuarios.insertOne({
  correo: "luis.rodriguez@colegio.edu.co",
  rol: "docente",
  nombres: "Luis",
  apellidos: "Rodríguez",
  telefono: "3145556666",
  documento: "10567890",
  codigo_empleado: "DOC005",
  especialidad: "Educación Física",
  fecha_ingreso: ISODate("2021-01-15"),
  activo: true,
  creado_en: Timestamp()
}).insertedId;

const docente6 = db.usuarios.insertOne({
  correo: "diana.torres@colegio.edu.co",
  rol: "docente",
  nombres: "Diana",
  apellidos: "Torres",
  telefono: "3155557777",
  documento: "10678901",
  codigo_empleado: "DOC006",
  especialidad: "Arte",
  fecha_ingreso: ISODate("2019-06-10"),
  activo: true,
  creado_en: Timestamp()
}).insertedId;

print("✔ 6 Docentes creados");

// ===== ESTUDIANTES =====
const estudiante1 = db.usuarios.insertOne({
  correo: "carlos.ramirez@colegio.edu.co",
  rol: "estudiante",
  nombres: "Carlos",
  apellidos: "Ramírez",
  documento: "1001234567",
  codigo_est: "EST001",
  fecha_nacimiento: ISODate("2010-05-20"),
  direccion: "Cra 10 #20-30",
  nombre_acudiente: "Luis Ramírez",
  telefono_acudiente: "3005551111",
  activo: true,
  creado_en: Timestamp()
}).insertedId;

const estudiante2 = db.usuarios.insertOne({
  correo: "ana.torres@colegio.edu.co",
  rol: "estudiante",
  nombres: "Ana",
  apellidos: "Torres",
  documento: "1001234568",
  codigo_est: "EST002",
  fecha_nacimiento: ISODate("2011-09-12"),
  direccion: "Calle 5 #10-22",
  nombre_acudiente: "Marta Torres",
  telefono_acudiente: "3015552222",
  activo: true,
  creado_en: Timestamp()
}).insertedId;

const estudiante3 = db.usuarios.insertOne({
  correo: "sofia.mendez@colegio.edu.co",
  rol: "estudiante",
  nombres: "Sofía",
  apellidos: "Méndez",
  documento: "1001234569",
  codigo_est: "EST003",
  fecha_nacimiento: ISODate("2010-02-08"),
  direccion: "Av 3 #12-50",
  nombre_acudiente: "Roberto Méndez",
  telefono_acudiente: "3025553333",
  activo: true,
  creado_en: Timestamp()
}).insertedId;

const estudiante4 = db.usuarios.insertOne({
  correo: "miguel.santos@colegio.edu.co",
  rol: "estudiante",
  nombres: "Miguel",
  apellidos: "Santos",
  documento: "1001234570",
  codigo_est: "EST004",
  fecha_nacimiento: ISODate("2010-11-15"),
  direccion: "Calle 8 #15-40",
  nombre_acudiente: "Patricia Santos",
  telefono_acudiente: "3035554444",
  activo: true,
  creado_en: Timestamp()
}).insertedId;

const estudiante5 = db.usuarios.insertOne({
  correo: "laura.gonzalez@colegio.edu.co",
  rol: "estudiante",
  nombres: "Laura",
  apellidos: "González",
  documento: "1001234571",
  codigo_est: "EST005",
  fecha_nacimiento: ISODate("2010-03-22"),
  direccion: "Calle 12 #18-25",
  nombre_acudiente: "Sandra González",
  telefono_acudiente: "3045555555",
  activo: true,
  creado_en: Timestamp()
}).insertedId;

const estudiante6 = db.usuarios.insertOne({
  correo: "david.martinez@colegio.edu.co",
  rol: "estudiante",
  nombres: "David",
  apellidos: "Martínez",
  documento: "1001234572",
  codigo_est: "EST006",
  fecha_nacimiento: ISODate("2010-07-14"),
  direccion: "Av 7 #22-30",
  nombre_acudiente: "Jorge Martínez",
  telefono_acudiente: "3055556666",
  activo: true,
  creado_en: Timestamp()
}).insertedId;

const estudiante7 = db.usuarios.insertOne({
  correo: "valentina.lopez@colegio.edu.co",
  rol: "estudiante",
  nombres: "Valentina",
  apellidos: "López",
  documento: "1001234573",
  codigo_est: "EST007",
  fecha_nacimiento: ISODate("2011-01-09"),
  direccion: "Cra 15 #10-12",
  nombre_acudiente: "María López",
  telefono_acudiente: "3065557777",
  activo: true,
  creado_en: Timestamp()
}).insertedId;

const estudiante8 = db.usuarios.insertOne({
  correo: "santiago.herrera@colegio.edu.co",
  rol: "estudiante",
  nombres: "Santiago",
  apellidos: "Herrera",
  documento: "1001234574",
  codigo_est: "EST008",
  fecha_nacimiento: ISODate("2010-10-25"),
  direccion: "Calle 20 #5-40",
  nombre_acudiente: "Carlos Herrera",
  telefono_acudiente: "3075558888",
  activo: true,
  creado_en: Timestamp()
}).insertedId;

const estudiante9 = db.usuarios.insertOne({
  correo: "isabella.castro@colegio.edu.co",
  rol: "estudiante",
  nombres: "Isabella",
  apellidos: "Castro",
  documento: "1001234575",
  codigo_est: "EST009",
  fecha_nacimiento: ISODate("2011-04-18"),
  direccion: "Av 10 #30-15",
  nombre_acudiente: "Andrea Castro",
  telefono_acudiente: "3085559999",
  activo: true,
  creado_en: Timestamp()
}).insertedId;

const estudiante10 = db.usuarios.insertOne({
  correo: "andres.morales@colegio.edu.co",
  rol: "estudiante",
  nombres: "Andrés",
  apellidos: "Morales",
  documento: "1001234576",
  codigo_est: "EST010",
  fecha_nacimiento: ISODate("2010-12-03"),
  direccion: "Cra 8 #14-28",
  nombre_acudiente: "Luis Morales",
  telefono_acudiente: "3095550000",
  activo: true,
  creado_en: Timestamp()
}).insertedId;

const estudiante11 = db.usuarios.insertOne({
  correo: "camila.rivera@colegio.edu.co",
  rol: "estudiante",
  nombres: "Camila",
  apellidos: "Rivera",
  documento: "1001234577",
  codigo_est: "EST011",
  fecha_nacimiento: ISODate("2011-06-21"),
  direccion: "Calle 25 #12-35",
  nombre_acudiente: "Patricia Rivera",
  telefono_acudiente: "3105551111",
  activo: true,
  creado_en: Timestamp()
}).insertedId;

const estudiante12 = db.usuarios.insertOne({
  correo: "juan.diaz@colegio.edu.co",
  rol: "estudiante",
  nombres: "Juan",
  apellidos: "Díaz",
  documento: "1001234578",
  codigo_est: "EST012",
  fecha_nacimiento: ISODate("2010-08-30"),
  direccion: "Av 12 #20-18",
  nombre_acudiente: "Roberto Díaz",
  telefono_acudiente: "3115552222",
  activo: true,
  creado_en: Timestamp()
}).insertedId;

const estudiante13 = db.usuarios.insertOne({
  correo: "nicolas.parra@colegio.edu.co",
  rol: "estudiante",
  nombres: "Nicolás",
  apellidos: "Parra",
  documento: "1001234579",
  codigo_est: "EST013",
  fecha_nacimiento: ISODate("2010-04-12"),
  direccion: "Calle 30 #8-15",
  nombre_acudiente: "Liliana Parra",
  telefono_acudiente: "3125553333",
  activo: true,
  creado_en: Timestamp()
}).insertedId;

print("✔ 13 Estudiantes creados");

// ===== CURSOS =====
const curso1 = db.cursos.insertOne({
  nombre_curso: "Matemáticas 10° A",
  codigo_curso: "MAT10A",
  id_docente: docente1,
  grado: "10",
  periodo: "1",
  capacidad_max: NumberInt(40),
  activo: true,
  docente_info: {
    nombres: "Juan",
    apellidos: "Pérez",
    especialidad: "Matemáticas"
  }
}).insertedId;

const curso2 = db.cursos.insertOne({
  nombre_curso: "Español 10° A",
  codigo_curso: "ESP10A",
  id_docente: docente2,
  grado: "10",
  periodo: "1",
  capacidad_max: NumberInt(40),
  activo: true,
  docente_info: {
    nombres: "María",
    apellidos: "López",
    especialidad: "Español"
  }
}).insertedId;

const curso3 = db.cursos.insertOne({
  nombre_curso: "Ciencias 10° A",
  codigo_curso: "CIE10A",
  id_docente: docente3,
  grado: "10",
  periodo: "1",
  capacidad_max: NumberInt(40),
  activo: true,
  docente_info: {
    nombres: "Carlos",
    apellidos: "García",
    especialidad: "Ciencias"
  }
}).insertedId;

const curso4 = db.cursos.insertOne({
  nombre_curso: "Matemáticas 10° A - Periodo 2",
  codigo_curso: "MAT10B",
  id_docente: docente1,
  grado: "10",
  periodo: "2",
  capacidad_max: NumberInt(40),
  activo: true,
  docente_info: {
    nombres: "Juan",
    apellidos: "Pérez",
    especialidad: "Matemáticas"
  }
}).insertedId;

const curso5 = db.cursos.insertOne({
  nombre_curso: "Español 11° A",
  codigo_curso: "ESP11A",
  id_docente: docente2,
  grado: "11",
  periodo: "1",
  capacidad_max: NumberInt(35),
  activo: true,
  docente_info: {
    nombres: "María",
    apellidos: "López",
    especialidad: "Español"
  }
}).insertedId;

const curso6 = db.cursos.insertOne({
  nombre_curso: "Español 10° B",
  codigo_curso: "ESP10B",
  id_docente: docente2,
  grado: "10",
  periodo: "1",
  capacidad_max: NumberInt(38),
  activo: true,
  docente_info: {
    nombres: "María",
    apellidos: "López",
    especialidad: "Español"
  }
}).insertedId;

const curso7 = db.cursos.insertOne({
  nombre_curso: "Literatura 11° A",
  codigo_curso: "LIT11A",
  id_docente: docente2,
  grado: "11",
  periodo: "1",
  capacidad_max: NumberInt(35),
  activo: true,
  docente_info: {
    nombres: "María",
    apellidos: "López",
    especialidad: "Español"
  }
}).insertedId;

const curso8 = db.cursos.insertOne({
  nombre_curso: "Matemáticas 11° A",
  codigo_curso: "MAT11A",
  id_docente: docente1,
  grado: "11",
  periodo: "1",
  capacidad_max: NumberInt(35),
  activo: true,
  docente_info: {
    nombres: "Juan",
    apellidos: "Pérez",
    especialidad: "Matemáticas"
  }
}).insertedId;

const curso9 = db.cursos.insertOne({
  nombre_curso: "Álgebra 10° B",
  codigo_curso: "ALG10B",
  id_docente: docente1,
  grado: "10",
  periodo: "1",
  capacidad_max: NumberInt(38),
  activo: true,
  docente_info: {
    nombres: "Juan",
    apellidos: "Pérez",
    especialidad: "Matemáticas"
  }
}).insertedId;

const curso10 = db.cursos.insertOne({
  nombre_curso: "Ciencias 11° A",
  codigo_curso: "CIE11A",
  id_docente: docente3,
  grado: "11",
  periodo: "1",
  capacidad_max: NumberInt(35),
  activo: true,
  docente_info: {
    nombres: "Carlos",
    apellidos: "García",
    especialidad: "Ciencias"
  }
}).insertedId;

const curso11 = db.cursos.insertOne({
  nombre_curso: "Inglés 10° A",
  codigo_curso: "ING10A",
  id_docente: docente4,
  grado: "10",
  periodo: "1",
  capacidad_max: NumberInt(40),
  activo: true,
  docente_info: {
    nombres: "Ana",
    apellidos: "Martínez",
    especialidad: "Inglés"
  }
}).insertedId;

const curso12 = db.cursos.insertOne({
  nombre_curso: "Inglés 11° A",
  codigo_curso: "ING11A",
  id_docente: docente4,
  grado: "11",
  periodo: "1",
  capacidad_max: NumberInt(35),
  activo: true,
  docente_info: {
    nombres: "Ana",
    apellidos: "Martínez",
    especialidad: "Inglés"
  }
}).insertedId;

const curso13 = db.cursos.insertOne({
  nombre_curso: "Educación Física 10° A",
  codigo_curso: "EDF10A",
  id_docente: docente5,
  grado: "10",
  periodo: "1",
  capacidad_max: NumberInt(45),
  activo: true,
  docente_info: {
    nombres: "Luis",
    apellidos: "Rodríguez",
    especialidad: "Educación Física"
  }
}).insertedId;

print("✔ 13 Cursos creados");

// ==========================================
//   FUNCIÓN PARA GENERAR CALIFICACIONES
//   CON PERIODOS (1, 2, 3, 4)
// ==========================================

function generarCalificacionesPorPeriodo() {
  const tipos = ["Parcial", "Taller", "Quiz"];
  const calificaciones = [];
  
  // Generar calificaciones para cada uno de los 4 periodos
  for (let periodo = 1; periodo <= 4; periodo++) {
    tipos.forEach((tipo, index) => {
      const nota = Math.random() * 2 + 3; // Entre 3.0 y 5.0
      const mes = periodo - 1; // 0=Enero, 1=Febrero, etc.
      const dia = 5 + (index * 15); // Distribuir en el mes
      
      calificaciones.push({
        tipo: tipo,
        nota: Number(nota.toFixed(1)),
        nota_maxima: Number(5.0),
        peso: Number(0.33),
        periodo: String(periodo), // "1", "2", "3", "4"
        fecha_eval: new Date(2025, mes, dia),
        comentarios: nota >= 4.0 ? "Buen desempeño" : "Debe reforzar"
      });
    });
  }
  
  return calificaciones;
}

print("✔ Función generarCalificacionesPorPeriodo() definida");

// ==========================================
//   INSERTAR MATRÍCULAS CON CALIFICACIONES
// ==========================================

// Estudiantes para cada curso
const matriculasData = [
  // Matemáticas 10° A
  { estudiantes: [estudiante1, estudiante2, estudiante3, estudiante4], curso: curso1, cursoInfo: { nombre_curso: "Matemáticas 10° A", codigo_curso: "MAT10A", grado: "10", periodo: "1" } },
  // Español 10° A
  { estudiantes: [estudiante1, estudiante2, estudiante11, estudiante12], curso: curso2, cursoInfo: { nombre_curso: "Español 10° A", codigo_curso: "ESP10A", grado: "10", periodo: "1" } },
  // Ciencias 10° A
  { estudiantes: [estudiante1, estudiante3, estudiante4, estudiante13], curso: curso3, cursoInfo: { nombre_curso: "Ciencias 10° A", codigo_curso: "CIE10A", grado: "10", periodo: "1" } },
  // Español 11° A
  { estudiantes: [estudiante5, estudiante6, estudiante7, estudiante8, estudiante9, estudiante10], curso: curso5, cursoInfo: { nombre_curso: "Español 11° A", codigo_curso: "ESP11A", grado: "11", periodo: "1" } },
  // Español 10° B
  { estudiantes: [estudiante1, estudiante2, estudiante11, estudiante12], curso: curso6, cursoInfo: { nombre_curso: "Español 10° B", codigo_curso: "ESP10B", grado: "10", periodo: "1" } },
  // Literatura 11° A
  { estudiantes: [estudiante5, estudiante6, estudiante7, estudiante8], curso: curso7, cursoInfo: { nombre_curso: "Literatura 11° A", codigo_curso: "LIT11A", grado: "11", periodo: "1" } },
  // Matemáticas 11° A
  { estudiantes: [estudiante5, estudiante6, estudiante7, estudiante9, estudiante10], curso: curso8, cursoInfo: { nombre_curso: "Matemáticas 11° A", codigo_curso: "MAT11A", grado: "11", periodo: "1" } },
  // Inglés 10° A
  { estudiantes: [estudiante1, estudiante2, estudiante3, estudiante4, estudiante11, estudiante12], curso: curso11, cursoInfo: { nombre_curso: "Inglés 10° A", codigo_curso: "ING10A", grado: "10", periodo: "1" } }
];

let totalMatriculas = 0;

matriculasData.forEach((data) => {
  data.estudiantes.forEach((estudianteId) => {
    const estudiante = db.usuarios.findOne({ _id: estudianteId });
    
    db.matriculas.insertOne({
      id_estudiante: estudianteId,
      id_curso: data.curso,
      fecha_matricula: Timestamp(),
      estado: "activo",
      calificaciones: generarCalificacionesPorPeriodo(), // ✅ 12 calificaciones (3 por periodo x 4 periodos)
      estudiante_info: {
        nombres: estudiante.nombres,
        apellidos: estudiante.apellidos,
        codigo_est: estudiante.codigo_est
      },
      curso_info: data.cursoInfo
    });
    
    totalMatriculas++;
  });
});

print("✔ " + totalMatriculas + " Matrículas creadas con calificaciones distribuidas en 4 periodos");

// ==========================================
//   AUDITORÍA
// ==========================================

db.auditoria.insertOne({
  id_usuario: admin1,
  accion: "INICIALIZAR_BD_COMPLETA",
  entidad_afectada: "sistema",
  detalles: { mensaje: "Base de datos inicializada con esquema y datos completos" },
  fecha: Timestamp()
});

print("✔ Registro de auditoría creado");

// ==========================================
//   RESUMEN FINAL
// ==========================================

print("\n✅ ¡BASE DE DATOS INICIALIZADA COMPLETAMENTE!\n");
print("📊 Resumen Final:");
print("   - Usuarios totales: " + db.usuarios.countDocuments());
print("   - Administradores: " + db.usuarios.countDocuments({ rol: "administrador" }));
print("   - Docentes: " + db.usuarios.countDocuments({ rol: "docente" }));
print("   - Estudiantes: " + db.usuarios.countDocuments({ rol: "estudiante" }));
print("   - Cursos totales: " + db.cursos.countDocuments());
print("   - Matrículas totales: " + db.matriculas.countDocuments());
print("   - Registros de auditoría: " + db.auditoria.countDocuments());

print("\n🎓 Distribución por docente:");
print("   - María López: " + db.cursos.countDocuments({ codigo_curso: { $regex: /^(ESP|LIT)/ } }) + " cursos");
print("   - Juan Pérez: " + db.cursos.countDocuments({ codigo_curso: { $regex: /^(MAT|ALG)/ } }) + " cursos");
print("   - Carlos García: " + db.cursos.countDocuments({ codigo_curso: { $regex: /^CIE/ } }) + " cursos");
print("   - Ana Martínez: " + db.cursos.countDocuments({ codigo_curso: { $regex: /^ING/ } }) + " cursos");
print("   - Luis Rodríguez: " + db.cursos.countDocuments({ codigo_curso: { $regex: /^EDF/ } }) + " cursos");

print("\n📚 Distribución de matrículas por curso:");
db.matriculas.aggregate([
  { $group: { _id: "$curso_info.nombre_curso", total: { $sum: 1 } } },
  { $sort: { total: -1 } }
]).forEach(function (doc) {
  print("   - " + doc._id + ": " + doc.total + " estudiantes");
});

print("\n✅ Calificaciones distribuidas en 4 periodos para cada matrícula");
print("   Cada estudiante tiene 12 calificaciones (3 por periodo)");
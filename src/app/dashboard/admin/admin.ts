import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Router, RouterModule } from '@angular/router'; // ✅ Agregar RouterModule
import { ApiService } from '../../services/api.service';

@Component({
  selector: 'app-admin',
  standalone: true,
  imports: [
    CommonModule,
    RouterModule  // ✅ Agregar RouterModule aquí
  ],
  templateUrl: './admin.html',
  styleUrls: ['./admin.css']
})
export default class AdminComponent implements OnInit {
  loading = false;
  error: string | null = null;
  activeView: 'dashboard' | 'students' | 'courses' | 'enrollments' = 'dashboard';

  adminName = 'Administrador';

  // Estadísticas
  stats = {
    totalStudents: 0,
    totalCourses: 0,
    totalTeachers: 0,
    totalEnrollments: 0,
    pendingEnrollments: 0
  };

  // Datos
  students: any[] = [];
  courses: any[] = [];
  enrollments: any[] = [];

  constructor(
    private api: ApiService,
    private router: Router
  ) {}

  ngOnInit(): void {
    this.loadUserInfo();
    this.loadData();
  }

  loadUserInfo(): void {
    const userInfo = localStorage.getItem('userInfo');
    if (userInfo) {
      try {
        const user = JSON.parse(userInfo);
        this.adminName = user.nombres || 'Administrador';
      } catch (e) {
        console.error('Error parsing userInfo:', e);
      }
    }
  }

  loadData(): void {
    this.loading = true;
    this.error = null;

    // Cargar todas las secciones en paralelo
    Promise.all([
      this.loadStudents(),
      this.loadCourses(),
      this.loadEnrollments(),
      this.loadStats()
    ]).then(() => {
      this.loading = false;
    }).catch((err) => {
      console.error('❌ Error cargando datos:', err);
      this.error = 'Error al cargar los datos del panel';
      this.loading = false;
    });
  }

  loadStudents(): Promise<void> {
    return new Promise((resolve, reject) => {
      this.api.getAdminStudents().subscribe({
        next: (response: any) => {
          console.log('✅ Estudiantes cargados:', response);
          this.students = response.students || [];
          resolve();
        },
        error: (err) => {
          console.error('❌ Error cargando estudiantes:', err);
          reject(err);
        }
      });
    });
  }

  loadCourses(): Promise<void> {
    return new Promise((resolve, reject) => {
      this.api.getAdminCourses().subscribe({
        next: (response: any) => {
          console.log('✅ Cursos cargados:', response);
          this.courses = response.courses || [];
          resolve();
        },
        error: (err) => {
          console.error('❌ Error cargando cursos:', err);
          reject(err);
        }
      });
    });
  }

  loadEnrollments(): Promise<void> {
    return new Promise((resolve, reject) => {
      this.api.getAdminEnrollments().subscribe({
        next: (response: any) => {
          console.log('✅ Matrículas cargadas:', response);
          this.enrollments = response.enrollments || [];
          resolve();
        },
        error: (err) => {
          console.error('❌ Error cargando matrículas:', err);
          reject(err);
        }
      });
    });
  }

  loadStats(): Promise<void> {
    return new Promise((resolve, reject) => {
      this.api.getAdminStatistics().subscribe({
        next: (response: any) => {
          console.log('✅ Estadísticas cargadas:', response);
          
          if (response.success) {
            this.stats = {
              totalStudents: response.total_estudiantes || 0,
              totalCourses: response.total_cursos || 0,
              totalTeachers: response.total_docentes || 0,
              totalEnrollments: response.total_matriculas || 0,
              pendingEnrollments: response.matriculas_pendientes || 0
            };
          }
          resolve();
        },
        error: (err) => {
          console.error('❌ Error cargando estadísticas:', err);
          reject(err);
        }
      });
    });
  }

  changeView(view: 'dashboard' | 'students' | 'courses' | 'enrollments'): void {
    this.activeView = view;
    console.log('📍 Vista cambiada a:', view);
  }

  goToReports(): void {
    this.router.navigate(['/dashboard/admin/reports']);
  }

  // ==========================================
  //   GESTIÓN DE ESTUDIANTES
  // ==========================================

  deleteStudent(studentId: string): void {
    if (!confirm('¿Está seguro de eliminar este estudiante? Esta acción no se puede deshacer.')) {
      return;
    }

    this.api.deleteStudent(studentId).subscribe({
      next: (response) => {
        console.log('✅ Estudiante eliminado:', response);
        this.loadStudents();
        this.loadStats();
      },
      error: (err) => {
        console.error('❌ Error eliminando estudiante:', err);
        alert('Error al eliminar el estudiante');
      }
    });
  }

  // ==========================================
  //   GESTIÓN DE CURSOS
  // ==========================================

  deleteCourse(courseId: string): void {
    if (!confirm('¿Está seguro de eliminar este curso? Esta acción no se puede deshacer.')) {
      return;
    }

    this.api.deleteCourse(courseId).subscribe({
      next: (response) => {
        console.log('✅ Curso eliminado:', response);
        this.loadCourses();
        this.loadStats();
      },
      error: (err) => {
        console.error('❌ Error eliminando curso:', err);
        alert('Error al eliminar el curso');
      }
    });
  }

  // ==========================================
  //   GESTIÓN DE MATRÍCULAS
  // ==========================================

  approveEnrollment(enrollmentId: string): void {
    if (!confirm('¿Está seguro de aprobar esta matrícula?')) {
      return;
    }

    this.api.updateEnrollment(enrollmentId, { estado: 'aprobado' }).subscribe({
      next: (response) => {
        console.log('✅ Matrícula aprobada:', response);
        this.loadEnrollments();
        this.loadStats();
      },
      error: (err) => {
        console.error('❌ Error aprobando matrícula:', err);
        alert('Error al aprobar la matrícula');
      }
    });
  }

  rejectEnrollment(enrollmentId: string): void {
    if (!confirm('¿Está seguro de rechazar esta matrícula?')) {
      return;
    }

    this.api.updateEnrollment(enrollmentId, { estado: 'rechazado' }).subscribe({
      next: (response) => {
        console.log('✅ Matrícula rechazada:', response);
        this.loadEnrollments();
        this.loadStats();
      },
      error: (err) => {
        console.error('❌ Error rechazando matrícula:', err);
        alert('Error al rechazar la matrícula');
      }
    });
  }

  deleteEnrollment(enrollmentId: string): void {
    if (!confirm('¿Está seguro de eliminar esta matrícula? Esta acción no se puede deshacer.')) {
      return;
    }

    this.api.deleteEnrollment(enrollmentId).subscribe({
      next: (response) => {
        console.log('✅ Matrícula eliminada:', response);
        this.loadEnrollments();
        this.loadStats();
      },
      error: (err) => {
        console.error('❌ Error eliminando matrícula:', err);
        alert('Error al eliminar la matrícula');
      }
    });
  }
}
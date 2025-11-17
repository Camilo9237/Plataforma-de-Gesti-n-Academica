import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ApiService } from '../../services/api.service';

@Component({
  selector: 'app-dashboard-student',
  standalone: true,
  imports: [CommonModule],
  template: `
    <div class="student-dashboard">
      <h1>Panel Estudiante</h1>

      <div class="top-row">
        <div class="grades-card">
          <div class="card-header">
            <div>
              <div class="title">Mis Calificaciones Recientes</div>
              <div class="subtitle">Últimas evaluaciones registradas</div>
            </div>
            <div class="avg">{{ grades?.average ?? '—' }}</div>
          </div>

          <div class="grade-list">
            <div class="grade-item" *ngFor="let g of grades?.recent">
              <div class="subject">{{ g.subject }}</div>
              <div class="meta">{{ g.date }}</div>
              <div class="score">{{ g.grade }}</div>
            </div>
          </div>
        </div>

        <div class="notifications-card">
          <div class="title">Notificaciones</div>
          <div class="notes">
            <div class="note" *ngFor="let n of notifications?.notifications">
              <div class="note-title">{{ n.title }}</div>
              <div class="note-type">{{ n.type }}</div>
            </div>
          </div>
          <button class="view-btn">Ver Boletines</button>
        </div>
      </div>

      <div class="schedule">
        <h3>Horario de Hoy</h3>
        <div class="schedule-grid">
          <div class="event" *ngFor="let e of schedule?.events">
            <div class="time">{{ e.time }}</div>
            <div class="subject">{{ e.subject }}</div>
            <div class="meta">{{ e.location }} · {{ e.teacher }}</div>
          </div>
        </div>
      </div>

      <div class="quick-actions">
        <button class="action">Boletines</button>
        <button class="action">Horarios</button>
        <button class="action">Tareas</button>
        <button class="action">Certificados</button>
      </div>

      <div *ngIf="loading" class="loading">Cargando datos...</div>
      <div *ngIf="error" class="error">{{ error }}</div>
    </div>
  `,
  styles: [
    ".student-dashboard { padding: 18px; font-family: Arial, sans-serif }",
    ".top-row { display:flex; gap:16px; margin-bottom:18px }",
    ".grades-card { flex:1; background:#fff; border:1px solid #eee; border-radius:8px; padding:12px }",
    ".card-header { display:flex; justify-content:space-between; align-items:center }",
    ".title { font-weight:600 }",
    ".subtitle { font-size:12px; color:#777 }",
    ".avg { font-size:28px; color:#2e7d32 }",
    ".grade-list { margin-top:10px }",
    ".grade-item { display:flex; justify-content:space-between; padding:8px 0; border-bottom:1px solid #f5f5f5 }",
    ".score { background:#e8f5e9; padding:6px 10px; border-radius:12px }",
    ".notifications-card { width:320px; background:#fff; border:1px solid #eee; border-radius:8px; padding:12px }",
    ".notes { margin-top:8px }",
    ".note { padding:8px 0; border-bottom:1px solid #f2f2f2 }",
    ".view-btn { margin-top:10px; background:#4caf50; color:#fff; border:none; padding:8px 12px; border-radius:6px }",
    ".schedule { margin-top:12px }",
    ".schedule-grid { display:grid; grid-template-columns: repeat(auto-fill, minmax(200px, 1fr)); gap:12px }",
    ".event { background:#fff; border:1px solid #eee; padding:10px; border-radius:8px }",
    ".time { font-size:12px; color:#666 }",
    ".meta { font-size:12px; color:#888 }",
    ".quick-actions { margin-top:16px; display:flex; gap:8px }",
    ".action { padding:10px 14px; border-radius:8px; border:1px solid #e0e0e0; background:#fff }",
    ".loading { margin-top:12px; color:#333 }",
    ".error { color: #b00020; margin-top:12px }"
  ]
})
export class StudentDashboard implements OnInit {
  grades: any = null;
  notifications: any = null;
  schedule: any = null;
  loading = false;
  error: string | null = null;

  constructor(private api: ApiService) {}

  ngOnInit(): void {
    this.loadAll();
  }

  loadAll() {
    this.loading = true;
    this.error = null;

    this.api.getStudentGrades().subscribe({
      next: (res) => this.grades = res,
      error: (err) => { this.error = 'Error al cargar calificaciones'; console.error(err); }
    });

    this.api.getStudentNotifications().subscribe({
      next: (res) => this.notifications = res,
      error: (err) => { this.error = this.error || 'Error al cargar notificaciones'; console.error(err); }
    });

    this.api.getStudentSchedule().subscribe({
      next: (res) => this.schedule = res,
      error: (err) => { this.error = this.error || 'Error al cargar horario'; console.error(err); }
    });

    setTimeout(() => this.loading = false, 500);
  }
}
 

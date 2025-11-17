import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ApiService } from '../../services/api.service';

@Component({
  selector: 'app-dashboard-teacher',
  standalone: true,
  imports: [CommonModule],
  template: `
    <div class="teacher-dashboard">
      <h1>Panel Docente</h1>

      <div class="main-grid">
        <section class="left">
          <h3>Mis Grupos</h3>
          <div *ngFor="let g of groups" class="group">
            <div class="group-row">
              <div class="group-name">{{ g.name }}</div>
              <button class="view">Ver Grupo</button>
            </div>
            <div class="progress"><div class="bar" [style.width.%]="g.progress_pct"></div></div>
            <div class="meta">{{ g.students }} estudiantes · Progreso {{ g.progress_pct }}%</div>
          </div>
        </section>

        <section class="right">
          <h3>Calificaciones Pendientes</h3>
          <ul class="pending">
            <li *ngFor="let p of pending?.pending">
              <div class="course">{{ p.course }}</div>
              <div class="count">{{ p.pending }} pendientes</div>
            </li>
          </ul>
          <button class="go">Ir a Calificaciones</button>
        </section>
      </div>

      <div class="actions">
        <button class="action">Registro de Notas</button>
        <button class="action">Asistencia</button>
        <button class="action">Observaciones</button>
        <button class="action">Reportes</button>
      </div>

      <div *ngIf="loading" class="loading">Cargando datos...</div>
      <div *ngIf="error" class="error">{{ error }}</div>
    </div>
  `,
  styles: [
    ".teacher-dashboard { padding: 18px; font-family: Arial, sans-serif }",
    ".main-grid { display:flex; gap:16px }",
    ".left { flex:1; background:#fff; border:1px solid #eee; padding:12px; border-radius:8px }",
    ".right { width:320px; background:#fff; border:1px solid #eee; padding:12px; border-radius:8px }",
    ".group { margin-bottom:12px }",
    ".group-row { display:flex; justify-content:space-between; align-items:center }",
    ".view { background:#fff; border:1px solid #e0e0e0; padding:6px 10px; border-radius:6px }",
    ".progress { height:10px; background:#f2f2f2; border-radius:6px; overflow:hidden; margin-top:6px }",
    ".bar { height:100%; background:#4caf50 }",
    ".meta { font-size:12px; color:#777; margin-top:6px }",
    ".pending { list-style:none; padding:0; margin:0 }",
    ".pending li { display:flex; justify-content:space-between; padding:8px 0; border-bottom:1px solid #f5f5f5 }",
    ".actions { margin-top:16px; display:flex; gap:8px }",
    ".action { padding:10px 14px; border-radius:8px; border:1px solid #e0e0e0; background:#fff }",
    ".loading { margin-top:12px; color:#333 }",
    ".error { color: #b00020; margin-top:12px }"
  ]
})
export class TeacherDashboard implements OnInit {
  groups: any[] = [];
  pending: any = null;
  loading = false;
  error: string | null = null;

  constructor(private api: ApiService) {}

  ngOnInit(): void {
    this.loadAll();
  }

  loadAll() {
    this.loading = true;
    this.error = null;

    this.api.getTeacherGroups().subscribe({
      next: (res) => this.groups = res?.groups || [],
      error: (err) => { this.error = 'Error al cargar grupos'; console.error(err); }
    });

    this.api.getTeacherPendingGrades().subscribe({
      next: (res) => this.pending = res,
      error: (err) => { this.error = this.error || 'Error al cargar calificaciones pendientes'; console.error(err); }
    });

    setTimeout(() => this.loading = false, 500);
  }
}


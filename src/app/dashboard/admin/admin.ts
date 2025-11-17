import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ApiService } from '../../services/api.service';

@Component({
  selector: 'app-dashboard-admin',
  standalone: true,
  imports: [CommonModule],
  template: `
    <div class="admin-dashboard">
      <h1>Panel Administrativo</h1>

      <div class="cards">
        <div class="card">
          <div class="card-title">Total Estudiantes</div>
          <div class="card-value">{{ stats?.total_students ?? '—' }}</div>
          <div class="card-sub">Estudiantes activos</div>
        </div>
        <div class="card">
          <div class="card-title">Matrículas Completas</div>
          <div class="card-value">{{ stats?.enrollment_complete_pct ?? '—' }}%</div>
          <div class="card-sub">Porcentaje</div>
        </div>
        <div class="card">
          <div class="card-title">Sedes Activas</div>
          <div class="card-value">{{ stats?.active_campuses ?? '—' }}</div>
          <div class="card-sub">Funcionando normalmente</div>
        </div>
        <div class="card">
          <div class="card-title">Docentes Activos</div>
          <div class="card-value">{{ stats?.active_teachers ?? '—' }}</div>
          <div class="card-sub">Personal docente</div>
        </div>
      </div>

      <div class="main-grid">
        <section class="left">
          <h3>Tareas Pendientes</h3>
          <ul class="tasks">
            <li *ngFor="let t of pending?.tasks">
              <div class="task-left">
                <div class="task-title">{{ t.title }}</div>
                <div class="task-count">{{ t.count }} pendientes</div>
              </div>
              <div class="task-badge" [class.urgent]="t.severity==='urgent'">{{ t.severity === 'urgent' ? 'Urgente' : '' }}</div>
            </li>
          </ul>
        </section>

        <section class="middle">
          <h3>Resumen de Sedes</h3>
          <div *ngFor="let c of campuses" class="campus">
            <div class="campus-header">
              <div class="campus-name">{{ c.name }}</div>
              <div class="campus-status">{{ c.status }}</div>
            </div>
            <div class="campus-stats">{{ c.students }} estudiantes</div>
            <div class="progress">
              <div class="progress-bar" [style.width.%]="c.occupancy_pct"></div>
            </div>
            <div class="campus-footer">Ocupación {{ c.occupancy_pct }}%</div>
          </div>
          <button class="btn">Gestionar Sedes</button>
        </section>

        <section class="right">
          <h3>Estadísticas Recientes</h3>
          <div class="recent" *ngFor="let r of recent?.recent">
            <div class="recent-month">{{ r.month }}</div>
            <div class="recent-values">Matriculas: {{ r.enrollments }} · Deserciones: {{ r.dropouts }} · Promedio: {{ r.avg }}</div>
          </div>
        </section>
      </div>

      <div class="quick-actions">
        <button class="action">Matrículas</button>
        <button class="action">Reportes</button>
        <button class="action">Usuarios</button>
        <button class="action">Configuración</button>
      </div>
      <div *ngIf="loading" class="loading">Cargando datos...</div>
      <div *ngIf="error" class="error">{{ error }}</div>
    </div>
  `,
  styles: [
    ".admin-dashboard { padding: 18px; font-family: Arial, sans-serif }",
    ".cards { display:flex; gap:12px; margin-bottom:18px }",
    ".card { background:#fff; border:1px solid #e6e6e6; padding:12px; border-radius:8px; flex:1 }",
    ".card-title { font-size:12px; color:#666 }",
    ".card-value { font-size:22px; margin-top:6px }",
    ".card-sub { font-size:11px; color:#999 }",
    ".main-grid { display:flex; gap:16px }",
    ".left, .middle, .right { background:#fff; border:1px solid #eee; padding:12px; border-radius:8px }",
    ".left { flex:1 }",
    ".middle { flex:1.5 }",
    ".right { flex:0.9 }",
    ".tasks { list-style:none; padding:0; margin:0 }",
    ".tasks li { display:flex; justify-content:space-between; padding:8px 0; border-bottom:1px solid #f2f2f2 }",
    ".task-title { font-weight:600 }",
    ".task-count { font-size:12px; color:#777 }",
    ".task-badge { background:#e6f7ea; color:#2e7d32; padding:4px 8px; border-radius:12px; font-size:12px }",
    ".task-badge.urgent { background:#ffebee; color:#b00020 }",
    ".campus { margin-bottom:12px }",
    ".campus-header { display:flex; justify-content:space-between; align-items:center }",
    ".progress { height:10px; background:#f2f2f2; border-radius:6px; overflow:hidden; margin-top:6px }",
    ".progress-bar { height:100%; background:#4caf50 }",
    ".quick-actions { margin-top:16px; display:flex; gap:8px }",
    ".action { padding:10px 14px; border-radius:8px; border:1px solid #e0e0e0; background:#fff }",
    ".loading { margin-top:12px; color:#333 }",
    ".error { color: #b00020; margin-top:12px }"
  ]
})
export class AdminDashboard implements OnInit {
  stats: any = null;
  pending: any = null;
  campuses: any[] = [];
  recent: any = null;
  loading = false;
  error: string | null = null;

  constructor(private api: ApiService) {}

  ngOnInit(): void {
    this.loadAll();
  }

  loadAll() {
    this.loading = true;
    this.error = null;

    this.api.getAdminStats().subscribe({
      next: (res) => this.stats = res,
      error: (err) => { this.error = 'Error al cargar estadísticas'; console.error(err); }
    });

    this.api.getPendingTasks().subscribe({
      next: (res) => this.pending = res,
      error: (err) => { this.error = this.error || 'Error al cargar tareas'; console.error(err); }
    });

    this.api.getCampuses().subscribe({
      next: (res) => this.campuses = res?.campuses || [],
      error: (err) => { this.error = this.error || 'Error al cargar sedes'; console.error(err); }
    });

    this.api.getRecentStats().subscribe({
      next: (res) => this.recent = res,
      error: (err) => { this.error = this.error || 'Error al cargar estadísticas recientes'; console.error(err); }
    });

    setTimeout(() => this.loading = false, 600);
  }
}
 

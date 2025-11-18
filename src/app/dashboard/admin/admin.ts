import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ApiService } from '../../services/api.service';
import { Router } from '@angular/router';

@Component({
  selector: 'app-dashboard-admin',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './admin.html',
  styleUrls: ['./admin.css']
})
export class AdminDashboard implements OnInit {
  stats: any = null;
  pending: any = null;
  campuses: any[] = [];
  recent: any = null;
  loading = false;
  error: string | null = null;

  constructor(private api: ApiService, private router: Router) {}

  ngOnInit(): void {
    this.loadAll();
  }

  goToMatriculas() {
    this.router.navigate(['/dashboard/admin/matriculas']);
  }

  goToInformes() {
    this.router.navigate(['/dashboard/admin/informes']);
  }

  goToUsuarios() {
    this.router.navigate(['/dashboard/admin/usuarios']);
  }

  goToConfiguracion() {
    this.router.navigate(['/dashboard/admin/configuracion']);
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
 

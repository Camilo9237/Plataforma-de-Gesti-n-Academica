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
export default class AdminComponent implements OnInit {  // ✅ Cambiar a 'export default'
  stats: any = null;
  pending: any = null;
  campuses: any[] = [];
  recent: any = null;
  loading = false;
  error: string | null = null;

  constructor(private api: ApiService, private router: Router) {}

  ngOnInit() {
    this.loadCampuses();
    this.loadStatistics();
    this.loadRecentActivity();
  }

  loadCampuses() {
    this.api.getCampuses().subscribe({
      next: (res: any) => this.campuses = res?.campuses || [],
      error: () => this.campuses = []
    });
  }

  loadStatistics() {
    this.api.getAdminStats().subscribe({
      next: (res: any) => this.stats = res,
      error: (err: any) => { 
        this.error = 'Error al cargar estadísticas'; 
        console.error(err); 
      }
    });

    this.api.getPendingTasks().subscribe({
      next: (res: any) => this.pending = res,
      error: (err: any) => { 
        this.error = this.error || 'Error al cargar tareas'; 
        console.error(err); 
      }
    });
  }

  loadRecentActivity() {
    this.api.getRecentStats().subscribe({
      next: (res: any) => this.recent = res,
      error: (err: any) => { 
        this.error = this.error || 'Error al cargar actividad reciente'; 
        console.error(err); 
      }
    });
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

    this.loadStatistics();
    this.loadCampuses();
    this.loadRecentActivity();

    setTimeout(() => this.loading = false, 600);
  }
}
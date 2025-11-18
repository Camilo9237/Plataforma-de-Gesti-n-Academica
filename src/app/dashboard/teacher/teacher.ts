import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ApiService } from '../../services/api.service';

@Component({
  selector: 'app-dashboard-teacher',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './teacher.html',
  styleUrls: ['./teacher.css']
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


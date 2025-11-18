import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ApiService } from '../../services/api.service';

@Component({
  selector: 'app-dashboard-student',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './student.html',
  styleUrls: ['./student.css']
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
 

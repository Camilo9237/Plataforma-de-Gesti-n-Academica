import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterModule } from '@angular/router';
import { ApiService } from '../../services/api.service';

@Component({
  selector: 'app-dashboard-student',
  standalone: true,
  imports: [CommonModule, RouterModule],
  templateUrl: './student.html',
  styleUrls: ['./student.css']
})
export default class StudentComponent implements OnInit {  // ✅ Cambiar a 'export default'
  grades: any = null;
  notifications: any = null;
  schedule: any = null;
  loading = false;
  error: string | null = null;

  constructor(private api: ApiService) {}

  ngOnInit() {
    this.api.getStudentGrades().subscribe({
      next: (res: any) => this.grades = res,
      error: (err: any) => { this.error = 'Error al cargar calificaciones'; console.error(err); }
    });
    this.api.getStudentNotifications().subscribe({
      next: (res: any) => this.notifications = res,
      error: (err: any) => { this.error = this.error || 'Error al cargar notificaciones'; console.error(err); }
    });
    this.api.getStudentSchedule().subscribe({
      next: (res: any) => this.schedule = res,
      error: (err: any) => { this.error = this.error || 'Error al cargar horario'; console.error(err); }
    });
  }
}
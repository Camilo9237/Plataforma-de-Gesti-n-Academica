import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterModule } from '@angular/router';
import { ApiService } from '../../services/api.service';
import { Router } from '@angular/router';

@Component({
  selector: 'app-dashboard-teacher',
  standalone: true,
  imports: [CommonModule, RouterModule],
  templateUrl: './teacher.html',
  styleUrls: ['./teacher.css']
})
export default class TeacherComponent implements OnInit {  // ✅ Cambiar a 'export default'
  groups: any[] = [];
  pending: any = null;
  loading = false;
  error: string | null = null;

  constructor(private api: ApiService, private router: Router) {}

  ngOnInit() {
    this.loadGroups();
  }

  loadGroups() {
    this.api.getTeacherGroups().subscribe({
      next: (res: any) => this.groups = res?.groups || [],
      error: (err) => console.error('Error loading groups:', err)
    });
  }

  logout(): void {
    if (confirm('¿Está seguro que desea cerrar sesión?')) {
      localStorage.removeItem('access_token');
      localStorage.removeItem('user_role');
      localStorage.removeItem('userInfo');
      this.router.navigate(['/login']);
    }
  }
}
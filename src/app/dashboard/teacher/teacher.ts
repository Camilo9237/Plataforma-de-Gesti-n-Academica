import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterModule } from '@angular/router';
import { ApiService } from '../../services/api.service';

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

  constructor(private api: ApiService) {}

  ngOnInit() {
    this.loadGroups();
  }

  loadGroups() {
    this.api.getTeacherGroups().subscribe({
      next: (res: any) => this.groups = res?.groups || [],
      error: (err) => console.error('Error loading groups:', err)
    });
  }
}
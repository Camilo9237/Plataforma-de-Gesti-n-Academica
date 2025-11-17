import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { environment } from '../../environments/environment';

@Injectable({ providedIn: 'root' })
export class ApiService {
  constructor(private http: HttpClient) {}

  login(payload: { username: string; password: string }) {
    return this.http.post<any>(`${environment.api.login}/login`, payload);
  }

  getDashboard() {
    return this.http.get<any>(`${environment.api.admin}/dashboard-general`);
  }
  getStudentsList() {
    return this.http.get<any>(`${environment.api.students}/students`);
  }

  getTeachersList() {
    return this.http.get<any>(`${environment.api.teachers}/teachers`);
  }

  getAdminOverview() {
    return this.http.get<any>(`${environment.api.admin}/dashboard-general`);
  }

  getAdminStats() {
    return this.http.get<any>(`${environment.api.admin}/admin/stats`);
  }

  getPendingTasks() {
    return this.http.get<any>(`${environment.api.admin}/admin/pending-tasks`);
  }

  getCampuses() {
    return this.http.get<any>(`${environment.api.admin}/admin/campuses`);
  }

  getRecentStats() {
    return this.http.get<any>(`${environment.api.admin}/admin/recent-stats`);
  }

  // Más métodos por servicio pueden añadirse aquí...
 
  /* Student endpoints */
  getStudentGrades() {
    return this.http.get<any>(`${environment.api.students}/student/grades`);
  }

  getStudentNotifications() {
    return this.http.get<any>(`${environment.api.students}/student/notifications`);
  }

  getStudentSchedule() {
    return this.http.get<any>(`${environment.api.students}/student/schedule-today`);
  }
  
  /* Teacher endpoints */
  getTeacherGroups() {
    return this.http.get<any>(`${environment.api.teachers}/teacher/groups`);
  }

  getTeacherPendingGrades() {
    return this.http.get<any>(`${environment.api.teachers}/teacher/pending-grades`);
  }

  getTeacherOverview() {
    return this.http.get<any>(`${environment.api.teachers}/teacher/overview`);
  }
}

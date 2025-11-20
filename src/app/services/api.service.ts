import { Injectable } from '@angular/core';
import { HttpClient, HttpResponse } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../../environments/environment';

@Injectable({
  providedIn: 'root'
})
export class ApiService {
  constructor(private http: HttpClient) {}

  // ===== AUTENTICACIÓN =====
  login(credentials: { username: string; password: string }) {
    return this.http.post(`${environment.api.login}/login`, credentials);
  }

  // ===== ESTUDIANTES =====
  getStudents() {
    return this.http.get(`${environment.api.students}/students`);
  }

  getStudent(id: string) {
    return this.http.get(`${environment.api.students}/students/${id}`);
  }

  createStudent(data: any) {
    return this.http.post(`${environment.api.students}/students`, data);
  }

  updateStudent(id: string, data: any) {
    return this.http.put(`${environment.api.students}/students/${id}`, data);
  }

  deleteStudent(id: string) {
    return this.http.delete(`${environment.api.students}/students/${id}`);
  }

  getStudentGrades() {
    return this.http.get(`${environment.api.students}/student/grades`);
  }

  getStudentNotifications() {
    return this.http.get(`${environment.api.students}/student/notifications`);
  }

  getStudentSchedule() {
    return this.http.get(`${environment.api.students}/student/schedule`);
  }

  // ===== PROFESORES =====
  getTeachers() {
    return this.http.get(`${environment.api.teachers}/teachers`);
  }

  getTeacher(id: string) {
    return this.http.get(`${environment.api.teachers}/teachers/${id}`);
  }

  createTeacher(data: any) {
    return this.http.post(`${environment.api.teachers}/teachers`, data);
  }

  updateTeacher(id: string, data: any) {
    return this.http.put(`${environment.api.teachers}/teachers/${id}`, data);
  }

  deleteTeacher(id: string) {
    return this.http.delete(`${environment.api.teachers}/teachers/${id}`);
  }

  getTeacherGroups() {
    return this.http.get(`${environment.api.teachers}/teacher/groups`);
  }

  getTeacherPendingGrades() {
    return this.http.get(`${environment.api.teachers}/teacher/pending-grades`);
  }

  // ===== CALIFICACIONES (PROFESOR) =====
  
  getCourseGrades(courseId: string) {
    return this.http.get(`${environment.api.teachers}/teacher/courses/${courseId}/grades`);
  }

  addGrade(data: {
    enrollment_id: string;
    tipo: string;
    nota: number;
    peso: number;
    nota_maxima?: number;
    comentarios?: string;
  }) {
    return this.http.post(`${environment.api.teachers}/teacher/grades`, data);
  }

  updateGrade(enrollmentId: string, gradeIndex: number, data: any) {
    return this.http.put(`${environment.api.teachers}/teacher/grades/${enrollmentId}`, {
      ...data,
      grade_index: gradeIndex
    });
  }

  deleteGrade(enrollmentId: string, gradeIndex: number) {
    return this.http.delete(`${environment.api.teachers}/teacher/grades/${enrollmentId}/${gradeIndex}`);
  }

  bulkUploadGrades(data: {
    course_id: string;
    tipo: string;
    peso: number;
    grades: Array<{enrollment_id: string; nota: number; comentarios?: string}>;
  }) {
    return this.http.post(`${environment.api.teachers}/teacher/grades/bulk`, data);
  }



  // ===== ADMINISTRADORES =====
  getAdministrators() {
    return this.http.get(`${environment.api.administrator}/administrators`);
  }

  getAdministrator(id: string) {
    return this.http.get(`${environment.api.administrator}/administrators/${id}`);
  }

  createAdministrator(data: any) {
    return this.http.post(`${environment.api.administrator}/administrators`, data);
  }

  updateAdministrator(id: string, data: any) {
    return this.http.put(`${environment.api.administrator}/administrators/${id}`, data);
  }

  deleteAdministrator(id: string) {
    return this.http.delete(`${environment.api.administrator}/administrators/${id}`);
  }

  getAdminStats() {
    return this.http.get(`${environment.api.admin}/admin/stats`);
  }

  getPendingTasks() {
    return this.http.get(`${environment.api.admin}/admin/pending-tasks`);
  }

  getCampuses() {
    return this.http.get(`${environment.api.admin}/admin/campuses`);
  }

  getRecentStats() {
    return this.http.get(`${environment.api.admin}/admin/recent-stats`);
  }

  // ===== REPORTES PDF =====
  
  /**
   * Descarga certificado de estudios
   * @param studentId ID del estudiante
   * @param tipo Tipo de certificado: 'estudios', 'calificaciones', etc.
   */
  downloadCertificado(studentId: string, tipo: string): Observable<HttpResponse<Blob>> {
    const url = `${environment.api.students}/student/certificado/${tipo}?student_id=${studentId}`;
    return this.http.get(url, { 
      responseType: 'blob',
      observe: 'response' 
    });
  }

  /**
   * Descarga boletín de calificaciones en PDF
   * @param studentId ID del estudiante
   * @param periodo Periodo académico
   */
  downloadBoletin(studentId: string, periodo: string): Observable<HttpResponse<Blob>> {
    const url = `${environment.api.students}/student/boletin?student_id=${studentId}&periodo=${periodo}`;
    return this.http.get(url, { 
      responseType: 'blob',
      observe: 'response' 
    });
  }
}
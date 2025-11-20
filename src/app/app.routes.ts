import { Routes } from '@angular/router';
import { RoleGuard } from './guards/role-guard';

export const routes: Routes = [
  { path: '', redirectTo: '/login', pathMatch: 'full' },
  { 
    path: 'login', 
    loadComponent: () => import('./authentication/login/login').then(m => m.default) 
  },
  {
    path: 'dashboard/student',
    loadComponent: () => import('./dashboard/student/student').then(m => m.default),
    canActivate: [RoleGuard],
    data: { role: 'estudiante' }
  },
  {
    path: 'dashboard/teacher',
    loadComponent: () => import('./dashboard/teacher/teacher').then(m => m.default),
    canActivate: [RoleGuard],
    data: { role: 'docente' }
  },
   {
    path: 'dashboard/teacher/grades',
    loadComponent: () => import('./dashboard/teacher/grades/grades').then(m => m.default),
    canActivate: [RoleGuard],
    data: { role: 'docente' }
  },
  {
    path: 'dashboard/admin',
    loadComponent: () => import('./dashboard/admin/admin').then(m => m.default),
    canActivate: [RoleGuard],
    data: { role: 'administrador' }
  },
  {
    path: 'unauthorized',
    loadComponent: () => import('./authentication/unauthorized/unauthorized').then(m => m.default)
  },
  { path: '**', redirectTo: '/login' }
];
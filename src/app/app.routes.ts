import { Routes } from '@angular/router';
import { RoleGuard } from './authentication/role.guard';

export const routes: Routes = [
	{
		path: 'login',
		loadComponent: () => import('./authentication/login/login').then(m => m.Login)
	},
	{
		path: 'dashboard',
		loadComponent: () => import('./dashboard/dashboard').then(m => m.Dashboard),
		canActivate: [RoleGuard]
	},
	{
		path: 'dashboard/student',
		loadComponent: () => import('./dashboard/student/student').then(m => m.StudentDashboard),
		canActivate: [RoleGuard]
	},
	{
		path: 'dashboard/student/boletines',
		loadComponent: () => import('./dashboard/student/boletines/boletines').then(m => m.Boletines),
		canActivate: [RoleGuard]
	},
	{
		path: 'dashboard/student/certificados',
		loadComponent: () => import('./dashboard/student/certificados/certificados').then(m => m.default),
		canActivate: [RoleGuard]
	},
	{
		path: 'dashboard/student/tareas',
		loadComponent: () => import('./dashboard/student/tareas/tareas').then(m => m.default),
		canActivate: [RoleGuard]
	},
	{
		path: 'dashboard/student/horario',
		loadComponent: () => import('./dashboard/student/horario/horario').then(m => m.Horario),
		canActivate: [RoleGuard]
	},
	{
		path: 'dashboard/teacher',
		loadComponent: () => import('./dashboard/teacher/teacher').then(m => m.TeacherDashboard),
		canActivate: [RoleGuard]
	},
	{
		path: 'dashboard/teacher/grades',
		loadComponent: () => import('./dashboard/teacher/grades/grades').then(m => m.default),
		canActivate: [RoleGuard]
	},
	{
		path: 'dashboard/teacher/attendance',
		loadComponent: () => import('./dashboard/teacher/attendance/attendance').then(m => m.default),
		canActivate: [RoleGuard]
	},
	{
		path: 'dashboard/teacher/observations',
		loadComponent: () => import('./dashboard/teacher/observations/observations').then(m => m.default),
		canActivate: [RoleGuard]
	},
	{
		path: 'dashboard/admin',
		loadComponent: () => import('./dashboard/admin/admin').then(m => m.AdminDashboard),
		canActivate: [RoleGuard]
	},
	{
		path: 'dashboard/admin/matriculas',
		loadComponent: () => import('./dashboard/admin/matriculas/matriculas').then(m => m.Matriculas),
		canActivate: [RoleGuard]
	},
	{
		path: 'dashboard/admin/informes',
		loadComponent: () => import('./dashboard/admin/informes/informes').then(m => m.Informes),
		canActivate: [RoleGuard]
	},
	{
		path: 'dashboard/admin/configuracion',
		loadComponent: () => import('./dashboard/admin/configuracion/configuracion').then(m => m.Configuracion),
		canActivate: [RoleGuard]
	},
	{
		path: 'dashboard/admin/usuarios',
		loadComponent: () => import('./dashboard/admin/usuarios/usuarios').then(m => m.Usuarios),
		canActivate: [RoleGuard]
	},
	{
		path: '',
		redirectTo: 'login',
		pathMatch: 'full'
	},
	{
		path: '**',
		redirectTo: 'login'
	}
];

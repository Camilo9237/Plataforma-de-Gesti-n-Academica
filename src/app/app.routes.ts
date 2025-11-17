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
		path: 'dashboard/teacher',
		loadComponent: () => import('./dashboard/teacher/teacher').then(m => m.TeacherDashboard),
		canActivate: [RoleGuard]
	},
	{
		path: 'dashboard/admin',
		loadComponent: () => import('./dashboard/admin/admin').then(m => m.AdminDashboard),
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

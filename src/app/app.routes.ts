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
		path: '',
		redirectTo: 'login',
		pathMatch: 'full'
	},
	{
		path: '**',
		redirectTo: 'login'
	}
];

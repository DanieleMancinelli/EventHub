import { Routes } from '@angular/router';
import { authGuard } from './core/auth.guard';

export const routes: Routes = [
  { 
    path: '', 
    loadComponent: () => import('./pages/home/home').then(m => m.HomeComponent) 
  },
  { 
    path: 'dettaglio-evento/:id', 
    loadComponent: () => import('./pages/dettaglio-evento/dettaglio-evento').then(m => m.DettaglioEventoComponent) 
  },
  { 
    path: 'miei-biglietti', 
    loadComponent: () => import('./pages/miei-biglietti/miei-biglietti').then(m => m.MieiBigliettiComponent),
    canActivate: [authGuard]
  },
  { path: '**', redirectTo: '' }
];

import { Routes } from '@angular/router';
import { HomeComponent } from './pages/home/home';
import { DettaglioEventoComponent } from './pages/dettaglio-evento/dettaglio-evento';
import { MieiBigliettiComponent } from './pages/miei-biglietti/miei-biglietti';
import { OrganizzatoreDashboardComponent } from './pages/organizzatore-dashboard/organizzatore-dashboard';
import { AdminDashboardComponent } from './pages/admin-dashboard/admin-dashboard';
import { authGuard } from './core/auth.guard';

export const routes: Routes = [
  { path: '', component: HomeComponent },
  { path: 'dettaglio-evento/:id', component: DettaglioEventoComponent },
  { path: 'miei-biglietti', component: MieiBigliettiComponent, canActivate: [authGuard] },
  { path: 'organizzatore', component: OrganizzatoreDashboardComponent, canActivate: [authGuard] },
  { path: 'admin', component: AdminDashboardComponent, canActivate: [authGuard] },
  { path: '**', redirectTo: '' }
];

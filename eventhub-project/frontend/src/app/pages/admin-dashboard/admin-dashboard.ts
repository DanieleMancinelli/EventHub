import { Component, OnInit, inject, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { DataService } from '../../services/data.service';
import { AuthService } from '../../core/auth.service';

@Component({
  selector: 'app-admin-dashboard',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './admin-dashboard.html'
})
export class AdminDashboardComponent implements OnInit {
  private dataService = inject(DataService);
  private auth = inject(AuthService);
  
  segnalazioni = signal<any[]>([]);
  utenti = signal<any[]>([]);

  ngOnInit() { this.carica(); }

  carica() {
    this.dataService.getSegnalazioni().subscribe(res => this.segnalazioni.set(res));
    this.dataService.getUtenti().subscribe(res => {
      // FILTRO: Rimuovo me stesso dalla lista utenti
      const me = this.auth.getUserId();
      this.utenti.set(res.filter((u: any) => u.utente_id !== me));
    });
  }

  gestisci(id: number, azione: string) {
    if (azione === 'elimina') {
      this.dataService.eliminaRecensione(id).subscribe(() => this.carica());
    } else {
      this.dataService.approvaRecensione(id).subscribe(() => this.carica());
    }
  }

  banna(id: string) { this.dataService.toggleBan(id).subscribe(() => this.carica()); }
  promuovi(id: string) { this.dataService.togglePromuovi(id).subscribe(() => this.carica()); }
}

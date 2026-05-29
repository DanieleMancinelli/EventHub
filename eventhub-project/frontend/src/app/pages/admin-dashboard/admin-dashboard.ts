import { Component, OnInit, inject, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { DataService } from '../../services/data.service';

@Component({
  selector: 'app-admin-dashboard',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './admin-dashboard.html'
})
export class AdminDashboardComponent implements OnInit {
  private dataService = inject(DataService);
  segnalazioni = signal<any[]>([]);

  ngOnInit() { this.carica(); }

  carica() {
    this.dataService.getSegnalazioni().subscribe(res => this.segnalazioni.set(res));
  }

  gestisci(id: number, azione: string) {
    if (azione === 'elimina') {
      this.dataService.eliminaRecensione(id).subscribe(() => this.carica());
    } else {
      this.dataService.approvaRecensione(id).subscribe(() => this.carica());
    }
  }
}

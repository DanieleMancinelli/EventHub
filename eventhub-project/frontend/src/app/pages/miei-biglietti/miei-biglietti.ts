import { Component, OnInit, inject, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { DataService } from '../../services/data.service';
import { RouterLink } from '@angular/router';

@Component({
  selector: 'app-miei-biglietti',
  standalone: true,
  imports: [CommonModule, RouterLink],
  templateUrl: './miei-biglietti.html'
})
export class MieiBigliettiComponent implements OnInit {
  private dataService = inject(DataService);
  biglietti = signal<any[]>([]);

  ngOnInit() { this.carica(); }
  carica() { this.dataService.getMieiBiglietti().subscribe(res => this.biglietti.set(res)); }

  // MODIFICA: Riceve il codice stringa, non l'ID numero
  annulla(codice: string) {
    if (confirm("Vuoi davvero annullare questo specifico biglietto?")) {
      this.dataService.disiscriviti(codice).subscribe(() => {
        alert("Biglietto annullato.");
        this.carica();
      });
    }
  }
}

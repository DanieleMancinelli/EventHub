import { Component, OnInit, inject, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ActivatedRoute, RouterLink } from '@angular/router';
import { FormsModule } from '@angular/forms';
import { DataService } from '../../services/data.service';
import { AuthService } from '../../core/auth.service';
import { environment } from '../../../environments/environment';

@Component({
  selector: 'app-dettaglio-evento',
  standalone: true,
  imports: [CommonModule, RouterLink, FormsModule],
  templateUrl: './dettaglio-evento.html'
})
export class DettaglioEventoComponent implements OnInit {
  private route = inject(ActivatedRoute);
  private dataService = inject(DataService);
  public auth = inject(AuthService);
  apiUrl = environment.apiUrl;

  evento = signal<any>(null);
  recensioni = signal<any[]>([]);
  messaggio = signal('');
  
  // Per la nuova recensione
  nuovaRec = { rating: 5, commento: '' };

  ngOnInit() {
    const id = this.route.snapshot.params['id'];
    this.caricaDati(id);
  }

  caricaDati(id: number) {
    this.dataService.getDettaglioEvento(id).subscribe(res => this.evento.set(res));
    this.dataService.getRecensioni(id).subscribe(res => this.recensioni.set(res));
  }

  isPassato(): boolean {
    if (!this.evento()) return false;
    return new Date(this.evento().data_evento) < new Date();
  }

  prenota() {
    this.dataService.iscriviti(this.evento().id).subscribe({
      next: (res) => this.messaggio.set("Iscrizione riuscita!"),
      error: () => this.messaggio.set("Errore iscrizione.")
    });
  }

  inviaRecensione() {
    this.dataService.inviaRecensione(this.evento().id, this.nuovaRec).subscribe(() => {
      this.nuovaRec = { rating: 5, commento: '' };
      this.caricaDati(this.evento().id);
    });
  }

  segnala(id: number) {
    this.dataService.segnalaRecensione(id).subscribe(() => {
      alert("Recensione segnalata all'admin.");
      this.caricaDati(this.evento().id);
    });
  }
}

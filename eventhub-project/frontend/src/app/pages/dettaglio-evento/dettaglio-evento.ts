import { Component, OnInit, inject, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ActivatedRoute, RouterLink } from '@angular/router';
import { DataService } from '../../services/data.service';
import { AuthService } from '../../core/auth.service';
import { environment } from '../../../environments/environment';

@Component({
  selector: 'app-dettaglio-evento',
  standalone: true,
  imports: [CommonModule, RouterLink],
  templateUrl: './dettaglio-evento.html'
})
export class DettaglioEventoComponent implements OnInit {
  private route = inject(ActivatedRoute);
  private dataService = inject(DataService);
  public auth = inject(AuthService);
  apiUrl = environment.apiUrl;

  evento = signal<any>(null);
  messaggio = signal('');

  ngOnInit() {
    const id = this.route.snapshot.params['id'];
    console.log("ID recuperato dalla rotta:", id);
    
    this.dataService.getDettaglioEvento(id).subscribe({
      next: (res) => {
        console.log("Dati evento ricevuti:", res);
        this.evento.set(res);
      },
      error: (err) => {
        console.error("Errore API dettagli:", err);
        this.messaggio.set("Errore nel caricamento dell'evento.");
      }
    });
  }

  prenota() {
    this.dataService.iscriviti(this.evento().id).subscribe({
      next: (res) => this.messaggio.set("Iscrizione riuscita! Codice: " + res.codice),
      error: () => this.messaggio.set("Posti esauriti o sei già iscritto.")
    });
  }
}

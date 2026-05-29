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
    this.dataService.getDettaglioEvento(id).subscribe(res => this.evento.set(res));
  }

  prenota() {
    this.dataService.iscriviti(this.evento().id).subscribe({
      next: (res) => this.messaggio.set("Iscrizione riuscita! Codice: " + res.codice),
      error: () => this.messaggio.set("Errore: posti esauriti o già iscritto.")
    });
  }
}

import { Component, OnInit, inject, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { RouterLink } from '@angular/router';
import { DataService } from '../../services/data.service';
import { environment } from '../../../environments/environment';

@Component({
  selector: 'app-home',
  standalone: true,
  imports: [CommonModule, FormsModule, RouterLink],
  templateUrl: './home.html',
  styleUrl: './home.css'
})
export class HomeComponent implements OnInit {
  private dataService = inject(DataService);
  apiUrl = environment.apiUrl;

  eventi = signal<any[]>([]);
  filtri = { categoria: '', citta: '', prezzo_max: '' };

  ngOnInit() {
    this.carica();
  }

  carica() {
    this.dataService.getEventi(this.filtri).subscribe(res => this.eventi.set(res));
  }
}

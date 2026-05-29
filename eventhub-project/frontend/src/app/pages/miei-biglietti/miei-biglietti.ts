import { Component, OnInit, inject, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { DataService } from '../../services/data.service';

@Component({
  selector: 'app-miei-biglietti',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './miei-biglietti.html'
})
export class MieiBigliettiComponent implements OnInit {
  private dataService = inject(DataService);
  biglietti = signal<any[]>([]);

  ngOnInit() {
    this.dataService.getMieiBiglietti().subscribe(res => this.biglietti.set(res));
  }
}

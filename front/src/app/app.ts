import { CommonModule } from '@angular/common';
import { Component } from '@angular/core';
import { FormsModule } from '@angular/forms';

type TurnStatus = 'Pendiente' | 'En atención' | 'Atendido' | 'Cancelado';

interface Turn {
  id: number;
  name: string;
  service: string;
  time: string;
  status: TurnStatus;
}

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './app.html',
  styleUrl: './app.css'
})
export class App {
  view: 'cliente' | 'asesor' = 'cliente';
  nextId = 11;
  customerName = '';
  selectedService = 'Atención general';
  notice = '';
  noticeType: 'success' | 'error' = 'success';
  myTurn: Turn | null = null;

  turns: Turn[] = [
    { id: 6, name: 'Cliente 06', service: 'Atención general', time: '08:25', status: 'Pendiente' },
    { id: 7, name: 'Cliente 07', service: 'Pagos y consultas', time: '08:30', status: 'Pendiente' },
    { id: 8, name: 'Cliente 08', service: 'Atención general', time: '08:34', status: 'Pendiente' },
    { id: 9, name: 'Cliente 09', service: 'Pagos y consultas', time: '08:38', status: 'Pendiente' },
    { id: 10, name: 'Cliente 10', service: 'Atención general', time: '08:45', status: 'Pendiente' }
  ];

  get waiting(): Turn[] {
    return this.turns.filter(turn => turn.status === 'Pendiente').sort((a, b) => a.id - b.id);
  }

  get currentTurn(): Turn | undefined {
    return this.turns.find(turn => turn.status === 'En atención');
  }

  get servedCount(): number {
    return this.turns.filter(turn => turn.status === 'Atendido').length + 5;
  }

  get averageWait(): number {
    return 12;
  }

  requestTurn(): void {
    const name = this.customerName.trim();
    if (!name) {
      this.showNotice('Escribe tu nombre para solicitar el turno.', 'error');
      return;
    }
    const turn: Turn = {
      id: this.nextId++,
      name,
      service: this.selectedService,
      time: new Date().toLocaleTimeString('es-CO', { hour: '2-digit', minute: '2-digit', hour12: false }),
      status: 'Pendiente'
    };
    this.turns = [...this.turns, turn];
    this.customerName = '';
    this.showNotice(`¡Listo! Tu turno es el #${turn.id}.`, 'success');
  }

  callNext(): void {
    if (!this.waiting.length) {
      this.showNotice('No hay turnos pendientes por llamar.', 'error');
      return;
    }
    this.turns = this.turns.map(turn =>
      turn.status === 'En atención' ? { ...turn, status: 'Atendido' as const } : turn
    );
    const next = this.waiting[0];
    this.turns = this.turns.map(turn =>
      turn.id === next.id ? { ...turn, status: 'En atención' as const } : turn
    );
    this.showNotice(`Turno #${next.id}: ${next.name}, puede pasar.`, 'success');
  }

  finishCurrent(): void {
    if (!this.currentTurn) {
      this.showNotice('No hay un turno en atención.', 'error');
      return;
    }
    const id = this.currentTurn.id;
    this.turns = this.turns.map(turn =>
      turn.id === id ? { ...turn, status: 'Atendido' as const } : turn
    );
    this.showNotice(`El turno #${id} se marcó como atendido.`, 'success');
  }

  cancelTurn(id: number): void {
    const turn = this.turns.find(item => item.id === id);
    if (!turn) {
      this.showNotice('No encontramos ese turno.', 'error');
      return;
    }
    if (turn.status !== 'Pendiente') {
      this.showNotice('Solo se pueden cancelar turnos pendientes.', 'error');
      return;
    }
    if (!confirm(`¿Seguro que deseas cancelar el turno #${turn.id}?`)) return;

    this.turns = this.turns.map(item =>
      item.id === id ? { ...item, status: 'Cancelado' as const } : item
    );
    if (this.myTurn?.id === id) {
      this.myTurn = { ...turn, status: 'Cancelado' };
    }
    this.showNotice(`El turno #${id} fue cancelado.`, 'success');
  }
  showNotice(message: string, type: 'success' | 'error'): void {
    this.notice = message;
    this.noticeType = type;
  }

  clearNotice(): void {
    this.notice = '';
  }
}


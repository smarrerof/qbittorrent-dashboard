import {
  Component,
  inject,
  effect,
  ElementRef,
  viewChild,
  afterNextRender,
  OnDestroy,
} from '@angular/core';
import { toSignal } from '@angular/core/rxjs-interop';
import { DecimalPipe } from '@angular/common';
import { BehaviorSubject, of, switchMap } from 'rxjs';
import {
  Chart,
  BarController,
  BarElement,
  CategoryScale,
  LinearScale,
  Tooltip,
} from 'chart.js';
import { StatsService, DailySummary, TorrentDelta } from '../services/stats.service';

Chart.register(BarController, BarElement, CategoryScale, LinearScale, Tooltip);

@Component({
  selector: 'app-dashboard',
  imports: [DecimalPipe],
  template: `
    <div class="dashboard">
      <h1>qBittorrent Dashboard</h1>

      <div class="card">
        <h2>Upload diario (GB)</h2>
        <canvas #chartCanvas></canvas>
      </div>

      @if (selectedDate()) {
        <div class="card detail">
          <h2>{{ selectedDate() }} — {{ detail().length }} torrents</h2>
          <table>
            <thead>
              <tr>
                <th>Torrent</th>
                <th class="gb-col">GB</th>
              </tr>
            </thead>
            <tbody>
              @for (row of detail(); track row.name) {
                <tr>
                  <td>{{ row.name }}</td>
                  <td class="gb-col">{{ row.uploaded_gb | number: '1.2-2' }}</td>
                </tr>
              }
            </tbody>
          </table>
        </div>
      }
    </div>
  `,
  styles: `
    .dashboard {
      max-width: 900px;
      margin: 2rem auto;
      padding: 0 1rem;
      font-family: system-ui, sans-serif;
      display: flex;
      flex-direction: column;
      gap: 1.5rem;
    }
    h1 { font-size: 1.5rem; color: #1e293b; }
    .card {
      background: #fff;
      border: 1px solid #e2e8f0;
      border-radius: 8px;
      padding: 1.5rem;
    }
    h2 { font-size: 1rem; color: #64748b; margin: 0 0 1rem; }
    canvas { max-height: 380px; cursor: pointer; }
    table { width: 100%; border-collapse: collapse; font-size: 0.875rem; }
    th { text-align: left; padding: 0.5rem 0.75rem; color: #64748b; border-bottom: 1px solid #e2e8f0; }
    td { padding: 0.5rem 0.75rem; border-bottom: 1px solid #f1f5f9; color: #1e293b; }
    tr:last-child td { border-bottom: none; }
    tr:hover td { background: #f8fafc; }
    .gb-col { text-align: right; font-variant-numeric: tabular-nums; white-space: nowrap; }
  `,
})
export class DashboardComponent implements OnDestroy {
  private stats = inject(StatsService);
  private chartCanvas = viewChild.required<ElementRef<HTMLCanvasElement>>('chartCanvas');
  private chart: Chart | null = null;

  private selectedDate$ = new BehaviorSubject<string | null>(null);

  readonly summary = toSignal(this.stats.getSummary(), { initialValue: [] as DailySummary[] });
  readonly selectedDate = toSignal(this.selectedDate$, { initialValue: null });
  readonly detail = toSignal(
    this.selectedDate$.pipe(
      switchMap((date) => (date ? this.stats.getByDay(date) : of([]))),
    ),
    { initialValue: [] as TorrentDelta[] },
  );

  constructor() {
    afterNextRender(() => {
      this.chart = new Chart(this.chartCanvas().nativeElement, {
        type: 'bar',
        data: {
          labels: [],
          datasets: [
            {
              label: 'Upload (GB)',
              data: [],
              backgroundColor: 'rgba(59, 130, 246, 0.8)',
              borderColor: 'rgb(59, 130, 246)',
              borderWidth: 1,
              borderRadius: 4,
            },
          ],
        },
        options: {
          responsive: true,
          onClick: (_, elements) => {
            if (!elements.length) { this.selectedDate$.next(null); return; }
            const label = this.chart!.data.labels![elements[0].index] as string;
            this.selectedDate$.next(label === this.selectedDate$.value ? null : label);
          },
          plugins: {
            legend: { display: false },
            tooltip: { callbacks: { label: (c) => ` ${c.parsed.y} GB` } },
          },
          scales: {
            y: { beginAtZero: true, ticks: { callback: (v) => `${v} GB` } },
          },
        },
      });
      this.updateChart(this.summary());
    });

    effect(() => this.updateChart(this.summary()));
  }

  private updateChart(data: DailySummary[]): void {
    if (!this.chart || data.length === 0) return;
    this.chart.data.labels = data.map((d) => d.date);
    this.chart.data.datasets[0].data = data.map((d) => d.total_gb);
    this.chart.update();
  }

  ngOnDestroy(): void {
    this.chart?.destroy();
  }
}

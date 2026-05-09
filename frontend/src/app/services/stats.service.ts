import { Injectable, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { environment } from '../../environments/environment';

export interface DailySummary {
  date: string;
  total_gb: number;
}

export interface TorrentDelta {
  name: string;
  uploaded_gb: number;
}

@Injectable({ providedIn: 'root' })
export class StatsService {
  private http = inject(HttpClient);

  getSummary(from?: string, to?: string) {
    const params: Record<string, string> = {};
    if (from) params['from'] = from;
    if (to) params['to'] = to;
    return this.http.get<DailySummary[]>(`${environment.apiUrl}/api/stats/summary`, { params });
  }

  getByDay(date: string) {
    return this.http.get<TorrentDelta[]>(`${environment.apiUrl}/api/stats/by-day`, { params: { date } });
  }
}

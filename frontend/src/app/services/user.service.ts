import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable, map } from 'rxjs';
import { User } from './auth.service';

export interface ManagedUser extends User {
  created_at?: string;
}

@Injectable({
  providedIn: 'root'
})
export class UserService {
  private apiUrl = 'http://localhost:5000/api/users';

  constructor(private http: HttpClient) {}

  getUsers(): Observable<ManagedUser[]> {
    return this.http.get<{ users: ManagedUser[] }>(this.apiUrl)
      .pipe(map(response => response.users));
  }

  createUser(payload: { email: string; password: string; role: string }): Observable<ManagedUser> {
    return this.http.post<{ user: ManagedUser }>(this.apiUrl, payload)
      .pipe(map(response => response.user));
  }

  updateUser(id: number, payload: Partial<{ email: string; password: string; role: string }>): Observable<ManagedUser> {
    return this.http.put<{ user: ManagedUser }>(`${this.apiUrl}/${id}`, payload)
      .pipe(map(response => response.user));
  }

  deleteUser(id: number): Observable<void> {
    return this.http.delete<{ message: string }>(`${this.apiUrl}/${id}`)
      .pipe(map(() => void 0));
  }
}



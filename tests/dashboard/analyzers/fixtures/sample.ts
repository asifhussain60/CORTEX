import { Component, OnInit, Input, Output, EventEmitter } from '@angular/core';
import { Observable, Subject, BehaviorSubject } from 'rxjs';
import { map, filter, switchMap, debounceTime, takeUntil } from 'rxjs/operators';
import { UserService } from '../../services/user.service';
import { User } from '../../models/user.model';
import { Store } from '@ngrx/store';
import { loadUsers, selectUser } from '../../store/user.actions';
import { HttpClient } from '@angular/common/http';

@Component({
  selector: 'app-user-list',
  templateUrl: './user-list.component.html',
  styleUrls: ['./user-list.component.scss'],
  standalone: true
})
export class UserListComponent implements OnInit {
  @Input() showInactive: boolean = false;
  @Output() userSelected = new EventEmitter<User>();

  users$: Observable<User[]>;
  searchTerm$ = new BehaviorSubject<string>('');
  private destroy$ = new Subject<void>();

  constructor(
    private userService: UserService,
    private store: Store,
    private http: HttpClient
  ) {}

  ngOnInit(): void {
    this.store.dispatch(loadUsers());
    
    this.users$ = this.searchTerm$.pipe(
      debounceTime(300),
      switchMap(term => this.userService.searchUsers(term)),
      map(users => users.filter(u => this.showInactive || u.active)),
      takeUntil(this.destroy$)
    );
  }

  selectUser(user: User): void {
    this.store.dispatch(selectUser({ userId: user.id }));
    this.userSelected.emit(user);
  }

  private loadUserDetails(userId: number): Observable<User> {
    return this.http.get<User>(`/api/users/${userId}`);
  }

  ngOnDestroy(): void {
    this.destroy$.next();
    this.destroy$.complete();
  }
}

@Injectable({
  providedIn: 'root'
})
export class UserService {
  constructor(private http: HttpClient) {}

  searchUsers(term: string): Observable<User[]> {
    return this.http.get<User[]>('/api/users/search', { params: { q: term } });
  }

  getUsers(): Observable<User[]> {
    return this.http.get<User[]>('/api/users');
  }
}

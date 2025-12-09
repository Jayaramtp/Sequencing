import { Component, OnInit, ViewChild, ElementRef } from '@angular/core';
import { Router } from '@angular/router';
import { AuthService, User } from '../../services/auth.service';
import { ManagedUser, UserService } from '../../services/user.service';

@Component({
  selector: 'app-dashboard',
  templateUrl: './dashboard.component.html',
  styleUrls: ['./dashboard.component.css']
})
export class DashboardComponent implements OnInit {
  @ViewChild('userManagementSection') userManagementSection?: ElementRef;
  currentUser: User | null = null;
  users: ManagedUser[] = [];
  showUserManagement = false;
  isLoadingUsers = false;
  isSavingUser = false;
  userError = '';
  userMessage = '';
  newUser = {
    email: '',
    password: '',
    role: 'user'
  };
  editUserId: number | null = null;
  editForm = {
    email: '',
    password: '',
    role: 'user'
  };

  constructor(
    private authService: AuthService,
    private router: Router,
    private userService: UserService
  ) {}

  ngOnInit(): void {
    this.currentUser = this.authService.getCurrentUser();
    if (!this.currentUser) {
      this.router.navigate(['/login']);
      return;
    }

    // Small delay to ensure token is properly set after login
    if (this.isAdmin()) {
      this.showUserManagement = true;
      // Use setTimeout to ensure token is available
      setTimeout(() => {
        this.loadUsers();
      }, 100);
    }
  }

  logout(): void {
    this.authService.logout();
  }

  isAdmin(): boolean {
    return this.authService.isAdmin();
  }

  toggleUserManagement(): void {
    this.showUserManagement = !this.showUserManagement;
    if (this.showUserManagement && this.isAdmin()) {
      if (this.users.length === 0) {
        this.loadUsers();
      }
      // Scroll to user management section after a brief delay to ensure it's rendered
      setTimeout(() => {
        if (this.userManagementSection) {
          this.userManagementSection.nativeElement.scrollIntoView({ 
            behavior: 'smooth', 
            block: 'start' 
          });
        }
      }, 100);
    }
  }

  loadUsers(): void {
    if (!this.isAdmin()) {
      return;
    }

    this.isLoadingUsers = true;
    this.userError = '';
    this.userService.getUsers().subscribe({
      next: (users) => {
        this.users = users;
        this.isLoadingUsers = false;
      },
      error: (error) => {
        console.error('Error loading users:', error);
        const errorMessage = error.error?.error || error.message || 'Unable to load users right now.';
        this.userError = `Error: ${errorMessage} (Status: ${error.status || 'Unknown'})`;
        this.isLoadingUsers = false;
      }
    });
  }

  createUser(): void {
    if (!this.newUser.email || !this.newUser.password) {
      this.userError = 'Email and password are required.';
      return;
    }

    this.isSavingUser = true;
    this.userError = '';
    this.userMessage = '';
    this.userService.createUser({ ...this.newUser }).subscribe({
      next: (created) => {
        this.users = [created, ...this.users];
        this.userMessage = 'User created successfully.';
        this.resetNewUser();
        this.isSavingUser = false;
      },
      error: (error) => {
        console.error('Error creating user:', error);
        const errorMessage = error.error?.error || error.message || 'Unable to create user.';
        this.userError = `Error: ${errorMessage} (Status: ${error.status || 'Unknown'})`;
        this.isSavingUser = false;
      }
    });
  }

  startEdit(user: ManagedUser): void {
    this.editUserId = user.id;
    this.editForm = {
      email: user.email,
      password: '',
      role: user.role
    };
    this.userMessage = '';
    this.userError = '';
  }

  cancelEdit(): void {
    this.editUserId = null;
    this.editForm = {
      email: '',
      password: '',
      role: 'user'
    };
  }

  saveEdit(): void {
    if (!this.editUserId) {
      return;
    }

    const payload: Partial<{ email: string; password: string; role: string }> = {};
    const original = this.users.find(u => u.id === this.editUserId);

    if (!original) {
      this.userError = 'Unable to find the selected user.';
      return;
    }

    if (this.editForm.email && this.editForm.email !== original.email) {
      payload.email = this.editForm.email;
    }
    if (this.editForm.password) {
      payload.password = this.editForm.password;
    }
    if (this.editForm.role && this.editForm.role !== original.role) {
      payload.role = this.editForm.role;
    }

    if (Object.keys(payload).length === 0) {
      this.userError = 'No changes to save.';
      return;
    }

    this.isSavingUser = true;
    this.userError = '';
    this.userMessage = '';

    this.userService.updateUser(this.editUserId, payload).subscribe({
      next: (updated) => {
        this.users = this.users.map(user => user.id === updated.id ? updated : user);
        this.userMessage = 'User updated successfully.';
        this.isSavingUser = false;
        this.cancelEdit();
      },
      error: (error) => {
        this.userError = error.error?.error || 'Unable to update user.';
        this.isSavingUser = false;
      }
    });
  }

  deleteUser(userId: number): void {
    const target = this.users.find(user => user.id === userId);
    const confirmation = confirm(`Delete user ${target?.email ?? ''}?`);
    if (!confirmation) {
      return;
    }

    this.isSavingUser = true;
    this.userError = '';
    this.userMessage = '';

    this.userService.deleteUser(userId).subscribe({
      next: () => {
        this.users = this.users.filter(user => user.id !== userId);
        this.userMessage = 'User deleted successfully.';
        this.isSavingUser = false;
        if (this.editUserId === userId) {
          this.cancelEdit();
        }
      },
      error: (error) => {
        this.userError = error.error?.error || 'Unable to delete user.';
        this.isSavingUser = false;
      }
    });
  }

  trackByUserId(_index: number, user: ManagedUser): number {
    return user.id;
  }

  private resetNewUser(): void {
    this.newUser = {
      email: '',
      password: '',
      role: 'user'
    };
  }
}



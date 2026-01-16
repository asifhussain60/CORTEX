# Frontend Setup Instructions

## Prerequisites Verification

Before proceeding, ensure required tools are installed:

```powershell
node --version  # Should be v20.x or higher
npm --version   # Should be 10.x or higher
ng version      # Should show Angular CLI 19.x
```

**Current System Status:**
- ✅ Node.js: v24.11.1
- ✅ npm: 11.6.2
- ❌ Angular CLI: Not installed

### Install Angular CLI 19

```powershell
npm install -g @angular/cli@19

# Verify installation
ng version
```

---

## Step-by-Step Setup

### 1. Create Angular Application

```powershell
# Navigate to frontend directory
cd frontend

# Create new Angular app with routing and CSS
ng new cortex-sdd-frontend --routing --style=css --skip-git

# Move contents to current directory
Move-Item cortex-sdd-frontend/* . -Force
Remove-Item cortex-sdd-frontend -Recurse
```

### 2. Install Tailwind CSS

```powershell
# Install Tailwind CSS and dependencies
npm install -D tailwindcss postcss autoprefixer

# Initialize Tailwind configuration
npx tailwindcss init
```

### 3. Configure Tailwind CSS

Edit `tailwind.config.js`:
```javascript
/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./src/**/*.{html,ts}",
  ],
  theme: {
    extend: {},
  },
  plugins: [],
}
```

Edit `src/styles.css` (add at the top):
```css
@tailwind base;
@tailwind components;
@tailwind utilities;
```

### 4. Generate Core Modules and Structure

```powershell
# Generate core module (singleton services)
ng generate module core --flat false

# Generate shared module (reusable components)
ng generate module shared --flat false

# Generate feature modules
ng generate module features/tasks --routing
ng generate module features/auth --routing

# Generate core services
ng generate service core/auth/auth
ng generate service core/interceptors/auth --skip-tests
ng generate service core/interceptors/error --skip-tests
ng generate guard core/guards/auth

# Generate auth components
ng generate component features/auth/login
ng generate component features/auth/register

# Generate task components
ng generate component features/tasks/task-list
ng generate component features/tasks/task-form
ng generate component features/tasks/task-item

# Generate shared components
ng generate component shared/components/navbar
ng generate component shared/components/loading-spinner
ng generate component shared/components/error-message

# Generate task service
ng generate service features/tasks/services/task
```

### 5. Install Additional Dependencies

```powershell
# Install RxJS operators and utilities
npm install rxjs

# Install Angular HTTP client (included by default)
# Install testing utilities
npm install --save-dev @angular/common @angular/forms
```

### 6. Configure Routing

Create/edit `src/app/app-routing.module.ts`:
```typescript
import { NgModule } from '@angular/core';
import { RouterModule, Routes } from '@angular/router';
import { AuthGuard } from './core/guards/auth.guard';

const routes: Routes = [
  { path: '', redirectTo: '/tasks', pathMatch: 'full' },
  {
    path: 'auth',
    loadChildren: () => import('./features/auth/auth.module').then(m => m.AuthModule)
  },
  {
    path: 'tasks',
    loadChildren: () => import('./features/tasks/tasks.module').then(m => m.TasksModule),
    canActivate: [AuthGuard]
  },
  { path: '**', redirectTo: '/tasks' }
];

@NgModule({
  imports: [RouterModule.forRoot(routes)],
  exports: [RouterModule]
})
export class AppRoutingModule { }
```

### 7. Configure Environment

Create `src/environments/environment.ts`:
```typescript
export const environment = {
  production: false,
  apiUrl: 'https://localhost:7000/api'
};
```

Create `src/environments/environment.prod.ts`:
```typescript
export const environment = {
  production: true,
  apiUrl: 'https://your-production-api.com/api'
};
```

### 8. Update angular.json for Tailwind

Ensure `angular.json` has proper build configurations (should be automatic).

---

## Verification

Run these commands to verify setup:

```powershell
# Install dependencies
npm install

# Run development server
npm start
# Navigate to http://localhost:4200

# Run tests
npm test

# Build for production
npm run build
```

---

## Project Structure After Setup

```
frontend/
├── src/
│   ├── app/
│   │   ├── core/
│   │   │   ├── auth/
│   │   │   │   └── auth.service.ts
│   │   │   ├── guards/
│   │   │   │   └── auth.guard.ts
│   │   │   └── interceptors/
│   │   │       ├── auth.service.ts
│   │   │       └── error.service.ts
│   │   ├── features/
│   │   │   ├── auth/
│   │   │   │   ├── login/
│   │   │   │   ├── register/
│   │   │   │   └── auth.module.ts
│   │   │   └── tasks/
│   │   │       ├── components/
│   │   │       │   ├── task-list/
│   │   │       │   ├── task-form/
│   │   │       │   └── task-item/
│   │   │       ├── services/
│   │   │       │   └── task.service.ts
│   │   │       └── tasks.module.ts
│   │   ├── shared/
│   │   │   └── components/
│   │   │       ├── navbar/
│   │   │       ├── loading-spinner/
│   │   │       └── error-message/
│   │   ├── app.component.ts
│   │   ├── app.module.ts
│   │   └── app-routing.module.ts
│   ├── assets/
│   ├── environments/
│   │   ├── environment.ts
│   │   └── environment.prod.ts
│   ├── index.html
│   ├── main.ts
│   └── styles.css (with Tailwind imports)
├── angular.json
├── package.json
├── tailwind.config.js
└── tsconfig.json
```

---

## Next Steps

After setup is complete:
1. Implement authentication services (login, register, token storage)
2. Implement HTTP interceptors (add JWT token to requests)
3. Create task management components
4. Style components with Tailwind CSS
5. Write unit tests for services and components

---

**Setup Time Estimate:** 30-45 minutes  
**Prerequisites:** Node.js 20+, npm 10+, Angular CLI 19

# Quick Start Guide - Resume Phase 0

**Current Status:** Phase 0 partially complete - awaiting environment setup

---

## ⚡ What's Been Done

✅ **Project Structure**
- Created `cortex-sample-apps/Cortex-SDD/` with backend, frontend, docs directories
- All documentation files created and ready

✅ **Configuration Files**
- README.md (comprehensive guide)
- .gitignore (for .NET and Angular)
- docker-compose.yml (SQL Server)
- VS Code workspace configuration
- Environment verification script

✅ **Setup Guides**
- `backend/SETUP.md` - Complete .NET setup instructions
- `frontend/SETUP.md` - Complete Angular setup instructions
- `docs/PHASE-0-STATUS.md` - Current status report

---

## 🚀 To Resume (3 Quick Steps)

### Step 1: Install Prerequisites (15-30 min)

**Install .NET 9.0 SDK:**
1. Download: https://dotnet.microsoft.com/download/dotnet/9.0
2. Run installer
3. Verify: `dotnet --version`

**Install Angular CLI:**
```powershell
# If behind corporate proxy, configure npm first:
npm config set strict-ssl false

# Install Angular CLI
npm install -g @angular/cli@19

# Verify
ng version
```

**Start SQL Server (Optional - Docker):**
```powershell
cd c:\PROJECTS\CORTEX\cortex-sample-apps\Cortex-SDD
docker-compose up -d
```

### Step 2: Verify Environment (2 min)

```powershell
cd c:\PROJECTS\CORTEX\cortex-sample-apps\Cortex-SDD
.\verify-environment.ps1
```

Expected output: All green checkmarks ✅

### Step 3: Execute Setup Scripts (30-45 min)

**Backend:**
```powershell
cd backend
# Follow all commands in SETUP.md sequentially
```

**Frontend:**
```powershell
cd frontend
# Follow all commands in SETUP.md sequentially
```

---

## 📋 Phase 0 Remaining Tasks

After prerequisites are installed:

**Backend (30 min):**
1. Create solution and 7 projects
2. Add project references
3. Install 15+ NuGet packages
4. Configure User Secrets
5. Build solution
6. Create first health check test (TDD RED phase)

**Frontend (30 min):**
1. Create Angular app with routing
2. Install and configure Tailwind CSS
3. Generate 10+ modules/components/services
4. Configure routing and environments
5. Verify build and serve
6. Create first app initialization test (TDD RED phase)

---

## 🎯 Success Criteria

Phase 0 complete when:
- [ ] `dotnet build` succeeds (backend)
- [ ] `ng serve` works (frontend at http://localhost:4200)
- [ ] `dotnet test` runs (0 tests passing initially)
- [ ] `npm test` runs (default Angular tests pass)
- [ ] Tailwind CSS classes work in Angular components

---

## 📞 Need Help?

**Documentation:**
- Main plan: `cortex-brain/documents/planning/badmonolith-modernization-plan.md`
- Phase 0 status: `docs/PHASE-0-STATUS.md`
- Backend setup: `backend/SETUP.md`
- Frontend setup: `frontend/SETUP.md`

**Common Issues:**

**Q: npm certificate error?**
```powershell
npm config set strict-ssl false
# Or configure corporate proxy
npm config set proxy http://your-proxy:port
```

**Q: .NET SDK not found?**
- Restart terminal after installation
- Verify PATH includes .NET SDK directory

**Q: SQL Server not connecting?**
- Use docker-compose OR
- Install SQL Server Express OR  
- Use (localdb)\mssqllocaldb with Visual Studio

---

## ⏭️ After Phase 0

Once Phase 0 is complete:
1. Review `badmonolith-modernization-plan.md`
2. Start **Phase 1: Domain & Data Layer**
3. Command: `execute phase 1 of badmonolith-modernization-plan`

---

**Time Investment:** 1-2 hours total for Phase 0 completion  
**Next Phase:** Phase 1 - Domain & Data Layer (6-8 hours)

# CORTEX Audit Checks Reference

**Loaded on demand during active audit operations.**

---

## 29-Point Production Readiness Checks

| # | Check | Auto-Fix |
|---|-------|----------|
| 1 | **Stale imports** — refs to `cortex_intelligence`, `cortex_lens`, `cortex.brain` | ✅ Rewrite |
| 2 | **Empty stubs** — files with only `pass` or `...` | ✅ Delete or implement |
| 3 | **Duplicate orchestrators** — >85% similarity (CORE-035) | ✅ Merge canonical |
| 4 | **Low-value tests** — assert `True`, mock everything | ✅ Delete |
| 5 | **Broken file references** — YAML/docs → moved/deleted | ✅ Update paths |
| 6 | **Root-level clutter** — outside canonical dirs | ✅ Move or delete |
| 7 | **CORE rule violations** — type hints, docstrings, snake_case, AC markers | ✅ Add missing |
| 8 | **Scattered .db/.log** — outside `.cortex-runtime/` | ✅ Consolidate |
| 9 | **Deprecated file names** — `DEPRECATED-*`, `*.old`, `*.backup` | ✅ Delete |
| 10 | **Test-source mirror** — `tests/` ↔ `cortex/` mismatch | ✅ Fix mirror |
| 11 | **Orchestrator health** — 22 endpoints healthy | ✅ Activate fallback |
| 12 | **Markdown sprawl** — `.md` outside `.github/`, `docs/` | ✅ Archive/delete |
| 13 | **Prompt/agent coherence** — stale counts, deleted paths | ✅ Update inline |
| 14 | **Response header drift** — wrong icon/name/field | ✅ Restore canonical |
| 15 | **MCP tool name registry** — old names in docs | ✅ Update names |
| 16 | **Knowledge synthesis wiring** — dead YAML refs | ✅ Update paths |
| 17 | **LENS pipeline health** — 8 analyzers importable | ✅ Activate fallback |
| 18 | **Ghost directories** — `cortex.intelligence/`, `cortex.brain/` | ✅ Delete |
| 19 | **SQLite health** — schema valid, no orphans, 30-day retention | ✅ Cleanup + VACUUM |
| 20 | **Workflow Composer health** — gateway/composer/templates wired | 🟡 Report |
| 21 | **Challenge gate drift** — `enable_challenges=True` default | ✅ Set default |
| 22 | **Duplicate methods (F811)** — dead first definitions | ✅ Remove dead def |
| 23 | **Unused imports (F401)** — non-`__init__` files | ✅ `ruff --fix` |
| 24 | **OS artifacts** — `.DS_Store`, `Thumbs.db` | ✅ Vacuum cleanup |
| 25 | **THIN INDEX CONTRACT** — `cortex-master.yaml` ≤500L | ✅ Extract detail |
| 26 | **Duplicate classes (CORE-035)** — same class in 2+ files | ✅ Merge/delete |
| 27 | **Stale test dirs** — dissolved package mirrors | ✅ `rm -rf` |
| 28 | **AC marker persistence gap** — emission silently broken | 🟡 Trace + fix |
| 29 | **Intelligence layer health** — `IntelligenceFacade` importable | ✅ Verify |

---

## Hardening Checks #30–#41

| # | Check | Auto-Fix |
|---|-------|----------|
| 30 | **Windows boot wiring** — no hardcoded POSIX paths | ✅ pathlib |
| 31 | **Architecture runtime connectivity** — live chain proven | 🟡 Wire + report |
| 32 | **Stub/Mock eradication** — no TODO/FIXME in production | ✅ Delete/implement |
| 33 | **YAML Reader no-bypass** — no direct `yaml.safe_load` | ✅ Route through reader |
| 34 | **No Versioning** — no `version:` fields | ✅ Remove |
| 35 | **Repo hygiene** — no `*.backup`, `*.bak`, `*.old` | ✅ Delete |
| 36 | **Prompt determinism** — no hedging language | ✅ Rewrite imperative |
| 37 | **Response template golden snapshot** — hierarchy valid | ✅ Fix inversions |
| 38 | **Registry cohesion** — 0 orphans, 0 broken refs | ✅ Remove/fix |
| 39 | **Sync non-production markers** — frontmatter present | ✅ Inject |
| 40 | **Green Gate** — preflight runs all checks end-to-end | ✅ CORE-068 loop |
| 41 | **Drift Lock System** — locks emitted per gap close | ✅ Auto-emit |

---

## Detect Commands (Quick Reference)

```bash
# Check 1 — stale imports
grep -rn "cortex_intelligence\|cortex_lens\|cortex\.brain" cortex/ --include="*.py"

# Check 22 — duplicate methods
python3 -m ruff check cortex/ --select=F811 --output-format=concise

# Check 23 — unused imports
python3 -m ruff check cortex/ --select=F401 --output-format=concise

# Check 25 — master plan size
wc -l cortex-registry/cortex-master.yaml

# Check 26 — duplicate classes
python3 -c "import ast,pathlib,collections; locs=collections.defaultdict(list); [locs[n.name].append(str(f)) for f in pathlib.Path('cortex').rglob('*.py') if '__pycache__' not in str(f) for n in ast.walk(ast.parse(f.read_text())) if isinstance(n,ast.ClassDef)]; dups={k:v for k,v in locs.items() if len(v)>1}; print(f'DUPLICATES={len(dups)}')"
```

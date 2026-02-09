Reverse-engineering a real codebase into UML + object relationships + actual domain knowledge is less “run a magic tool” and more “build a pipeline that triangulates truth from code, runtime, and data.” Here’s the best way to do it for a C# / .NET MVC + Angular + SQL/Oracle stack, without wasting weeks generating pretty-but-useless diagrams.

The winning approach: three lenses, one model
1) Static structure (what the code says)

Goal: classes, interfaces, dependencies, call graph hints, layering.

C# / .NET

Parse the solution with Roslyn (this is the grown-up way). Extract:

type graph (inheritance, interface impl)

composition/aggregation (fields, properties)

references between assemblies/namespaces

method call edges (best-effort; dynamic dispatch complicates)

Generate UML-ish class diagrams selectively, not for the whole solution. Whole-solution class diagrams become “spaghetti art” fast.

Identify architectural boundaries:

MVC: Controllers → Services → Repositories → DbContext (or DAL)

.NET layers by assembly naming + dependency direction (enforce “no upward references”)

Angular

Parse TypeScript AST (or use tooling) to extract:

module boundaries, component/service dependencies

DI graph (providers)

routing map → feature areas (this is often closer to domain than folder names)

Don’t try to UML every component. Use it to map feature slices and state/data flows.

2) Runtime truth (what actually happens)

Goal: confirm real call paths, object lifetimes, and cross-layer flows that static analysis misses.

Instrument / trace:

.NET: OpenTelemetry traces (or APM) to capture request → controller → service → db calls

Log correlation IDs; capture endpoint, service method, SQL text hash, latency

Dependency injection (DI) container graph:

Export registrations (interfaces → concrete types) at startup

This is gold for “what implementations are actually used”

This is how you avoid diagrams based on dead code, old interfaces, or “intended architecture.”

3) Data model (what the domain really is)

Goal: domain entities, relationships, cardinality, aggregates, invariants (as much as code+DB reveals).

Reverse engineer the DB (SQL Server/Oracle):

ERD from foreign keys, unique constraints, check constraints

stored procs/views as “domain operations” (often where business logic hides)

Map ORM models ↔ tables:

Entity Framework: mappings, navigation properties, fluent config

Legacy: hand-written SQL → infer entity boundaries via query patterns

Read the “names”:

table/column names, enum tables, reference data tables

these often encode domain language more reliably than code comments

Then unify this into a single Domain Knowledge Graph:

nodes: types, tables, endpoints, UI routes

edges: “calls”, “reads/writes”, “maps to”, “depends on”, “contains”

attributes: namespaces, assemblies, module, ownership, last changed, usage frequency

That graph becomes the source-of-truth; UML is just one view of it.

Practical workflow (what I’d do on a real team)
Step 0 — Stop the bleeding: define the outputs you want

You want usable artifacts, not “a 600-page PDF class diagram.”
Target these:

C4-style maps (Context → Container → Component) for “how it hangs together”

3–10 domain diagrams (bounded contexts / modules)

Key sequence diagrams for critical flows (top 10 endpoints or business processes)

ERD with mappings to domain entities

Glossary (ubiquitous language): nouns (entities), verbs (use cases), rules (invariants)

Step 1 — Discover boundaries fast

List assemblies/projects and dependencies

List Angular routes and lazy-loaded modules

List DB schemas and top tables by usage (from query logs if possible)

This produces your first “map of the city.”

Step 2 — Extract relationships automatically (but only keep what matters)

From C#: type graph + DI graph + controller/service/repo call edges

From Angular: route → component → service → API client mapping

From DB: FK graph + view/proc dependencies

Now you have raw material.

Step 3 — Build “domain slices”

Pick a business capability (e.g., Claims, Billing, Scheduling) and trace it end-to-end:

Angular route/module → API endpoint → service → repository → tables/procs
For each slice, create:

a small class diagram (only the relevant types)

a sequence diagram (actual call chain)

a data diagram (tables + relationships used)

Repeat until you’ve covered the core capabilities.

Step 4 — Validate with humans (because code lies by omission)

Interview product/SMEs with your diagrams in hand:

“Which of these entities are real business concepts vs technical artifacts?”

“Which relationships are actually enforced vs ‘we hope’?”

“Where do rules live: UI, API, DB, batch jobs?”

Update glossary + bounded contexts accordingly.

Tooling that actually works (stack-specific)
C#/.NET

Roslyn for extraction (custom or existing analyzers)

NDepend for dependency graphs and architectural rule checks (very effective for .NET layering)

Visual Studio Architecture / DGML (still useful for dependency graphs)

OpenTelemetry + Jaeger/Zipkin/APM for runtime traces

Angular

Compodoc (quick DI + module/component documentation)

Dependency Cruiser (TS dependency rules/graphs)

Route map extraction (Angular Router config)

DB (SQL Server / Oracle)

ERD tools (Oracle SQL Developer Data Modeler for Oracle; many options for SQL Server)

Query logging / AWR (Oracle) / Query Store (SQL Server) to see actual usage

Dependency extraction for views/procs/packages

Cross-cutting diagram outputs

PlantUML (best “diagram as code” for versioning)

Structurizr (C4 diagrams; excellent for architecture-as-code)

Mermaid (good for lightweight docs, less precise for UML)

The trap to avoid

Auto-generated full UML of the entire system is almost always garbage.
It’s technically “accurate” and practically useless. The best reverse-engineering is curated: generate everything, keep only what answers questions.

If you want a “best single strategy”

Build a graph-based model (types + endpoints + routes + tables + runtime traces) and generate:

C4 maps (architecture)

curated UML per domain slice (structure)

sequence diagrams from traces (behavior)

ERD + entity mappings (data)

glossary (language)

That’s how you get domain knowledge, not just diagrams.


Best way: treat it like building a knowledge graph + a few “truthy” diagrams, not like drawing UML by hand from vibes. Reverse-engineering succeeds when you automate extraction, then curate the few models that matter.

1) Start with an automated structural map (fast, low drama)

C# / .NET

Build + index the solution: restore, build, run tests. This ensures analyzers see real types.

Use Roslyn-based analysis (or tools built on it) to extract:

Class/interface inheritance

Method call graph (at least per assembly)

Dependency graph between projects/namespaces

Attributes/annotations (often encode domain meaning)

Practical tools:

NDepend (excellent dependency graphs, coupling, layering, cycle detection; great “architecture x-ray”)

ReSharper / Rider: diagrams, type hierarchy, call hierarchy, “find usages” at scale

dotnet-depends / dependency graph outputs (quick project-level view)

Angular / TypeScript

Generate dependency/call/module graphs:

Madge (module dependency graph)

Compodoc (Angular docs + dependency views)

Extract:

Modules → components/services relationships

Injectable service usage

Route graph (often a domain workflow map)

2) Extract “domain nouns” from the edges, not just the nodes

UML class diagrams alone are usually too literal. Domain knowledge is hiding in:

Database schema (tables, columns, constraints, FK graph)

API contracts (OpenAPI/Swagger, controllers, routes, DTOs)

Business rules (validation layers, “specification” classes, policy engines, stored procedures/packages)

Workflows (state machines, status fields, routing, background jobs)

So do this early:

DB-first ERD:

For SQL Server: SSMS database diagrams (basic), or better: SchemaSpy, dbdiagram.io, Redgate SQL Doc

For Oracle: SQL Developer Data Modeler, SchemaSpy (works with Oracle too)

Then map Entities ↔ Tables ↔ DTOs ↔ API endpoints. That mapping is where “domain truth” lives.

3) Build a “thin UML set” that people actually use

Instead of 200-class diagrams, generate/maintain 5–8 diagrams max, each answering a question:

Context diagram: system boundaries + integrations (Oracle/other services/auth/jobs)

Container diagram: Angular app, .NET services, DB(s), queues, batch jobs

Component diagram: major modules (Auth, Orders, Billing…) and their dependencies

Key domain model: only core aggregates/entities (20–40 types, not 400)

Sequence diagram: top 3 user flows end-to-end (UI → API → DB → external)

State diagram: for key lifecycle entities (OrderStatus, CaseStatus…)

ERD: for core schema areas

Deployment diagram (optional): environments, hosting, network boundaries

4) Use “runtime truth” to validate the static analysis

Static graphs lie by omission (reflection, DI, dynamic SQL). Add runtime evidence:

ASP.NET MVC / Web API

Enable request logging and inspect routing + middleware pipeline

OpenTelemetry tracing (or Application Insights) to capture call chains

DI container inspection

Dump service registrations at startup → actual wiring graph

SQL observation

SQL Server Extended Events / Profiler; Oracle tracing/AWR (careful in prod)

Identify top queries and which endpoints trigger them

5) Produce a knowledge graph you can query (this is the power move)

If you want “ask anything about the codebase” capability, store extracted facts as triples:

Nodes: Type, Method, Route, Table, Column, StoredProc, Module, Component

Edges: calls, depends_on, maps_to, reads, writes, returns, validates, owns

Implementation options:

Neo4j (classic; great for relationship queries)

Datomic / RDF if you’re feeling philosophical

Or simplest: JSON + SQLite with good indexing

Example queries you’ll want:

“Which endpoints write to TABLE_X?”

“Which UI components call endpoint /api/orders?”

“What classes enforce rule ‘cannot close case if balance > 0’?”

“Where is OrderStatus transitioned to ‘Approved’?”

6) Toolchain suggestion by stack (pragmatic picks)

C#/.NET

NDepend (architecture + dependency truth)

Rider/ReSharper (navigation + diagrams)

Roslyn analyzer script (custom extraction)

PlantUML / Mermaid for curated diagrams

Angular

Compodoc (docs + graph)

Madge (module graph)

ESLint rules + TS compiler API for extraction if needed

SQL Server / Oracle

SchemaSpy (ERD + HTML docs)

Oracle SQL Developer Data Modeler (best native)

Store schema metadata + FK graph into your knowledge graph

7) A recommended workflow that actually works

Inventory: solutions/projects, apps, DBs, integrations, scheduled jobs

Auto-extract: dependency graphs + schema ERD + route map

Identify bounded contexts: cluster by dependency + schema areas + namespaces

Curate diagrams (thin set)

Add runtime traces for top flows

Build the queryable knowledge graph

Write a “Domain Glossary”: nouns + lifecycles + invariants + owners
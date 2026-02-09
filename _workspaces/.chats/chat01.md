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

Reverse Engineering KSESSIONS for Use‑Case & UML Discovery

This report outlines how CORTEX should analyse the KSESSIONS repository (branch DEVELOPMENT) to reverse engineer it into meaningful use cases, UML object relationships, and domain knowledge. The goal is to build a knowledge graph of the system so that agents can reason about the codebase and generate high‑level documentation or automation tasks.

1 Repository overview

The KSESSIONS application is a full‑stack platform built with ASP.NET MVC/Web API, AngularJS and SQL Server. It uses a layered architecture with presentation, business, data and domain layers and follows patterns like the repository pattern and DTOs. Authentication is handled with Auth0/JWT and dependency injection is managed via Ninject. A recent Etymology module extends the system with an Angular‑driven UI, RESTful API endpoints and a new database schema for linguistic analysis.

Key components
Layer/component	Purpose
Presentation (Sessions.Spa)	Controllers and Angular components serve user interfaces and handle HTTP requests.
Business layer (Sessions.Business)	Contains services, business logic and orchestrates operations.
Data layer (Sessions.Data)	Implements repository interfaces using Dapper to execute stored procedures and SQL queries.
Domain layer (Sessions.Domain)	Defines DTOs and entities such as AhadeesDto.
Authentication	Uses [Authorize] attributes and JWT to secure controllers.
Etymology subsystem	Adds endpoints /api/etymology/*, Angular UI and a new schema for roots and derivatives.
Documentation	Extensive guides cover architecture, quick‑reference commands, recent changes and implementation successes.
2 Reverse‑engineering workflow for CORTEX
2.1 Inventory & code extraction

Clone and build: Use ksrun for full‑stack development or ksiis <port> for API testing. A successful build ensures all controllers and repositories compile and exposes the dependency graph.

Static analysis: Use Roslyn analyzers (for C#) and the TypeScript compiler API (for Angular) to extract:

Class hierarchies, interfaces, inheritance and dependencies (Roslyn).

Controller routes and action methods with their HTTP verbs and DTOs.

Repository interfaces and implementations (e.g., IAhadeesRepository and AhadeesRepository), mapping methods to stored procedures and tables.

Angular modules, components and services to map UI flows to backend endpoints.

Database schema extraction: Generate an ER diagram from the SQL Server database. The Etymology subsystem uses Roots and Derivatives tables with performance indexes, while the Ahadees module uses the Ahadees table and sp_SaveAhadeesNew stored procedure. Tools like SchemaSpy or SQL Server Management Studio diagramming can provide the foreign‑key relationships.

Configuration inspection: Examine Web.config, Ninject bindings, startup scripts and package manifests. Security improvements include disabling debug mode, enabling security headers and enforcing HTTPS.

2.2 Deriving use cases

CORTEX should derive use cases by tracing user‑facing flows from the front‑end through the API to the data layer:

Identify top routes: Extract Angular route definitions and map them to controllers. For example, the Etymology module defines routes for search, root management and derivative management with CRUD operations.

Define actors and triggers: Use authentication attributes and naming conventions to determine who can perform each action (e.g., admin vs. user). Token management endpoints support generating, validating and analyzing tokens.

Map data interactions: Link each API endpoint to repository methods and stored procedures. For example, saving Ahadees goes through IAhadeesRepository.SaveAhadees and sp_SaveAhadeesNew, which validates and cleans text before saving.

Document success and error flows: For each use case, describe the normal sequence (e.g., Save Ahadees) and error scenarios (e.g., unauthorized access, validation failure). This ensures complete test coverage.

2.3 Constructing UML diagrams

Generate a minimal set of diagrams to avoid information overload:

Context diagram: Show system boundaries—web UI, API layer, database, authentication provider and external integrations.

Container diagram: Depict the major application containers (frontend, API, data layer, domain layer) and the flows between them.

Component diagram: Show major services (e.g., token service, Ahadees repository, Etymology service) and their dependencies. Indicate how controllers depend on services and repositories via constructor injection.

Class diagram: Limit to core domain models (e.g., AhadeesDto, AddSessionTokenRequest, Roots and Derivatives entities). Show relationships between DTOs, repositories and stored procedures.

Sequence diagrams: Create one for each key use case (e.g., Save Ahadees, Generate Token, Search Etymology) to illustrate the request flow from the UI to the database.

State diagrams (optional): Model lifecycle transitions where appropriate (e.g., status changes for sessions or tokens).

2.4 Building a knowledge graph

To support agent reasoning, store extracted facts (nodes and relationships) in a graph database. Nodes can represent types, methods, endpoints, tables, stored procedures and UI components; edges can represent calls, reads, writes, owns or maps_to relationships. Example queries include:

Query	Purpose
“Which endpoints write to Ahadees table?”	Identifies data ownership and coupling.
“Which Angular component calls /api/etymology/search?”	Maps UI interactions to backend logic.
“Where are validation rules for AhadeesDto implemented?”	Locates business rules and error handling.

By storing this graph, CORTEX can generate documentation, detect architectural violations and assist developers with context‑aware recommendations.

3 Extracting domain best practices & coding styles
3.1 Established patterns

Documentation emphasises several patterns and best practices:

Layer separation: Presentation, business, data and domain layers are clearly separated, enforcing single responsibility.

Repository pattern: Interfaces such as IAhadeesRepository define contracts, while concrete repositories handle SQL operations. This abstracts data access and facilitates testing.

Dependency injection: Ninject is used to register and inject services, repositories and DbConnections. The TokenController constructor shows typical DI for repository, token service, cache and analytics dependencies.

DTO usage: Lightweight data transfer objects (e.g., AhadeesDto) separate domain models from persistence models.

RESTful APIs: Controllers expose CRUD endpoints following REST conventions, using [HttpGet], [HttpPost], [HttpPut] and [HttpDelete] attributes and returning appropriate status codes. Token endpoints include generate, validate, analytics and popular actions.

Security hygiene: Web.config is hardened—debug mode disabled, custom errors enabled, cookies secured, and headers like X‑Content‑Type‑Options and Content‑Security‑Policy added. JWT tokens use long expiration in development and shorter expiration in production.

Testing strategy: The architecture guide recommends unit, API and integration testing using frameworks like xUnit and Playwright. The Implementation Success Summary highlights that following patterns reduces new API implementation time from hours to minutes.

Error handling: Controllers validate input, check authentication and return meaningful HTTP responses (e.g., 400 Bad Request, 401 Unauthorized, 500 Internal Server Error).

Documentation and quick reference: Guides like KSESSIONS-ARCHITECTURE-GUIDE.md and KSESSIONS-QUICK-REFERENCE.md provide step‑by‑step instructions, templates, troubleshooting tips and patterns. Developers are encouraged to follow these to avoid common pitfalls.

3.2 Coding style guidelines

While KSESSIONS does not include a formal StyleCop configuration, patterns emerge from the documentation and code:

Professional naming: Variables and methods use descriptive, camelCase or PascalCase names. The Etymology summary notes “professional naming and structure throughout”.

Consistent formatting: Indentation and spacing follow standard C# conventions, and Angular code uses consistent bracket and semicolon placement.

Comprehensive comments: Complex logic (e.g., text sanitization in AhadeesRepository.ValidateAndCleanForJson) is well commented.

Separation of concerns: Controllers remain thin, delegating business logic to services and data operations to repositories.

Parameter validation: Data annotations and explicit validation in controllers ensure that required fields are present before persisting or processing.

Modular Angular design: The Etymology module uses reusable components, service layer abstraction and proper state management.

3.3 Security best practices

Security documentation emphasises:

Updating dependencies: Upgrading vulnerable packages like Bootstrap, CodeMirror and FontAwesome to secure versions.

Configuring secure headers: Adding headers such as X-Content-Type-Options, X-Frame-Options, X-XSS-Protection and Content-Security-Policy.

Disabling debug & error exposure: Setting debug="false" and enabling custom errors to prevent information leakage.

Secure cookies and HTTPS: Enforcing SSL and HSTS, requiring requireSSL="true" and adding Strict-Transport-Security in production.

Monitoring and maintenance: Monthly package updates, header verification and automated security scanning.

4 Practical steps for CORTEX implementation

Automate extraction using CORTEX’s total-recall agent: run inventory on the repository to detect project structure, languages and build commands.

Use connectors to fetch documentation and code: the GitHub connector can retrieve architecture guides, quick references and source files for analysis.

Generate the knowledge graph: store extracted entities and relationships; update with runtime traces by capturing API calls and DB queries.

Create diagrams: use PlantUML or Mermaid to generate diagrams automatically from the knowledge graph, then allow human curation.

Incorporate best practices: configure CORTEX’s intelligence layer to flag deviations from patterns (e.g., missing dependency injection, lack of stored procedure mapping, insecure headers). Provide suggestions using domain rules and templates derived from the repository’s documentation and examples.

Support continuous learning: After initial reverse engineering, use the Etymology and Ahadees modules as reference models for new features. Encourage contributions to update documentation and pattern libraries when new modules are added.

Conclusion

The KSESSIONS repository offers rich documentation and a well‑structured codebase that follow established patterns. By automating extraction of code structure, API flows and database schemas, CORTEX can construct a comprehensive knowledge graph. From this graph it can generate use‑case descriptions, UML diagrams and enforce domain best practices. Leveraging the existing architecture guide, security improvements and implementation summaries, CORTEX can provide intelligent guidance to developers and ensure future features remain consistent, secure and maintainable.

In short, the report explains that KSESSIONS is a layered ASP.NET/Angular application with clear separation between presentation, business, data and domain tiers. It outlines a workflow for CORTEX that starts by cloning and building the solution, then uses static analyzers to extract classes, controllers, repositories and Angular components. It describes mapping API routes to use‑cases, generating concise UML diagrams, and building a knowledge graph to answer questions like which endpoints write to certain tables. The report also distills key architectural patterns—repository abstraction, dependency injection, DTO usage, RESTful conventions—and highlights coding style practices and security hardening measures drawn from the project’s extensive documentation.



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

If you share:

repo structure (project list) and

whether you use EF/EF Core, Dapper, or raw ADO.NET, and

whether Oracle logic lives in packages/procs/views
…I can give you a concrete extraction plan (and even a Roslyn-based skeleton) that fits your exact layout.
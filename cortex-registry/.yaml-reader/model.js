// ============================================================================
// CORTEX Registry Explorer - Schema Inference & Normalization
// Pure offline JavaScript - no network dependencies
// ============================================================================

/**
 * Schema Inference Engine
 * Detects common registry patterns and normalizes to entity model
 */
class SchemaInference {
    /**
     * Infer schema type from YAML data structure
     * @param {Object} data - Parsed YAML data
     * @returns {Object} - { type, confidence, entities, graph }
     */
    static infer(data) {
        if (!data || typeof data !== 'object') {
            return { type: 'unknown', confidence: 0, entities: [], graph: null };
        }

        // Try each schema detector in priority order
        const detectors = [
            this.detectRegistrySchema,
            this.detectWorkflowSchema,
            this.detectEntityCollection,
            this.detectDependencyGraph
        ];

        for (const detector of detectors) {
            const result = detector.call(this, data);
            if (result.confidence > 0.6) {
                return result;
            }
        }

        // Fallback: generic object
        return {
            type: 'generic',
            confidence: 0.5,
            entities: this.extractGenericEntities(data),
            graph: null
        };
    }

    /**
     * Detect CORTEX Registry Schema
     * Pattern: metadata + phase_status structure
     */
    static detectRegistrySchema(data) {
        const hasMetadata = data.metadata && typeof data.metadata === 'object';
        const hasPhaseStatus = data.phase_status && typeof data.phase_status === 'object';
        
        if (!hasMetadata && !hasPhaseStatus) {
            return { type: 'registry', confidence: 0 };
        }

        const confidence = (hasMetadata ? 0.5 : 0) + (hasPhaseStatus ? 0.5 : 0);
        
        // Extract entities from all phase status sections
        const entities = [];
        const graph = { nodes: [], links: [] };

        if (hasPhaseStatus) {
            for (const [section, items] of Object.entries(data.phase_status)) {
                if (Array.isArray(items)) {
                    items.forEach(item => {
                        // Skip null/undefined items
                        if (!item || typeof item !== 'object') return;
                        
                        const entity = this.normalizeEntity(item, 'phase', section);
                        if (!entity) return; // Skip if normalization failed
                        
                        entities.push(entity);
                        
                        // Add to graph
                        graph.nodes.push({
                            id: entity.id,
                            label: entity.label,
                            type: 'phase',
                            status: section
                        });

                        // Extract dependencies
                        this.extractDependencies(entity, graph);
                    });
                }
            }
        }

        return {
            type: 'registry',
            confidence,
            entities,
            graph: graph.nodes.length > 0 ? graph : null,
            metadata: data.metadata || {}
        };
    }

    /**
     * Detect Workflow Schema
     * Pattern: steps/stages/transitions
     */
    static detectWorkflowSchema(data) {
        const hasSteps = data.steps && Array.isArray(data.steps);
        const hasStages = data.stages && Array.isArray(data.stages);
        const hasWorkflow = data.workflow && typeof data.workflow === 'object';

        if (!hasSteps && !hasStages && !hasWorkflow) {
            return { type: 'workflow', confidence: 0 };
        }

        const steps = hasSteps ? data.steps : 
                     hasStages ? data.stages :
                     hasWorkflow && data.workflow.steps ? data.workflow.steps : [];

        const entities = steps.map((step, idx) => 
            this.normalizeEntity(step, 'workflow-step', `step-${idx + 1}`)
        );

        // Build workflow graph
        const graph = this.buildWorkflowGraph(steps);

        return {
            type: 'workflow',
            confidence: 0.8,
            entities,
            graph
        };
    }

    /**
     * Detect Entity Collection
     * Pattern: Array of objects with id/name/title
     */
    static detectEntityCollection(data) {
        // Check if root is array
        if (Array.isArray(data)) {
            const hasIdentity = data.every(item => 
                item && (item.id || item.name || item.title)
            );
            if (hasIdentity) {
                return {
                    type: 'collection',
                    confidence: 0.9,
                    entities: data.map(item => this.normalizeEntity(item, 'item')),
                    graph: this.buildDependencyGraph(data)
                };
            }
        }

        // Check for collection properties
        for (const [key, value] of Object.entries(data)) {
            if (Array.isArray(value) && value.length > 0) {
                const hasIdentity = value.every(item =>
                    item && typeof item === 'object' && (item.id || item.name || item.title)
                );
                if (hasIdentity) {
                    return {
                        type: 'collection',
                        confidence: 0.8,
                        entities: value.map(item => this.normalizeEntity(item, key)),
                        graph: this.buildDependencyGraph(value),
                        collectionName: key
                    };
                }
            }
        }

        return { type: 'collection', confidence: 0 };
    }

    /**
     * Detect Dependency Graph
     * Pattern: Objects with depends_on/requires/uses fields
     */
    static detectDependencyGraph(data) {
        const entities = [];
        const hasDependencies = this.scanForDependencies(data, entities);

        if (!hasDependencies) {
            return { type: 'graph', confidence: 0 };
        }

        return {
            type: 'graph',
            confidence: 0.7,
            entities,
            graph: this.buildDependencyGraph(entities)
        };
    }

    /**
     * Normalize entity to standard format
     */
    static normalizeEntity(item, kind, status = null) {
        if (!item || typeof item !== 'object') {
            return null;
        }

        const id = item.id || item.name || item.title || `${kind}-${Math.random().toString(36).substr(2, 9)}`;
        const label = item.title || item.name || item.id || id;
        
        return {
            id,
            label,
            kind,
            status: status || item.status || item.state || 'unknown',
            summary: this.extractSummary(item),
            description: item.description || item.desc || '',
            owner: item.owner || item.assignee || item.author || '',
            tags: this.extractTags(item),
            dependencies: this.extractDependencyList(item),
            metrics: this.extractMetrics(item),
            raw: item
        };
    }

    /**
     * Extract human-readable summary
     */
    static extractSummary(item) {
        // Priority: description > summary > details > first 100 chars of any text field
        if (item.description) return item.description.substring(0, 150);
        if (item.summary) return item.summary;
        if (item.details) return item.details.substring(0, 150);
        
        // Try to build from available fields
        const parts = [];
        if (item.title) parts.push(item.title);
        if (item.type) parts.push(`(${item.type})`);
        if (item.duration) parts.push(`Duration: ${item.duration}`);
        
        return parts.join(' ') || 'No description available';
    }

    /**
     * Extract tags from various field patterns
     */
    static extractTags(item) {
        const tags = new Set();
        
        if (Array.isArray(item.tags)) {
            item.tags.forEach(t => tags.add(t));
        }
        if (Array.isArray(item.labels)) {
            item.labels.forEach(l => tags.add(l));
        }
        if (item.type) tags.add(item.type);
        if (item.category) tags.add(item.category);
        
        return Array.from(tags);
    }

    /**
     * Extract dependency list
     */
    static extractDependencyList(item) {
        const deps = [];
        
        if (Array.isArray(item.depends_on)) deps.push(...item.depends_on);
        if (Array.isArray(item.dependencies)) deps.push(...item.dependencies);
        if (Array.isArray(item.requires)) deps.push(...item.requires);
        if (Array.isArray(item.uses)) deps.push(...item.uses);
        if (item.consolidates) deps.push(...(Array.isArray(item.consolidates) ? item.consolidates : [item.consolidates]));
        
        return deps;
    }

    /**
     * Extract metrics
     */
    static extractMetrics(item) {
        const metrics = {};
        
        if (item.metrics && typeof item.metrics === 'object') {
            return item.metrics;
        }
        
        // Common metric fields
        const metricFields = ['tests', 'coverage', 'duration', 'velocity', 'stages', 'files_created'];
        metricFields.forEach(field => {
            if (item[field] !== undefined) {
                metrics[field] = item[field];
            }
        });
        
        return metrics;
    }

    /**
     * Build workflow graph
     */
    static buildWorkflowGraph(steps) {
        const nodes = [];
        const links = [];

        steps.forEach((step, idx) => {
            const id = step.id || `step-${idx + 1}`;
            nodes.push({
                id,
                label: step.name || step.title || id,
                type: 'workflow-step',
                order: idx
            });

            // Link to next step
            if (idx < steps.length - 1) {
                const nextId = steps[idx + 1].id || `step-${idx + 2}`;
                links.push({
                    source: id,
                    target: nextId,
                    type: 'sequence'
                });
            }

            // Explicit transitions
            if (Array.isArray(step.transitions)) {
                step.transitions.forEach(targetId => {
                    links.push({
                        source: id,
                        target: targetId,
                        type: 'transition'
                    });
                });
            }
        });

        return { nodes, links };
    }

    /**
     * Build dependency graph
     */
    static buildDependencyGraph(entities) {
        const nodes = [];
        const links = [];
        const nodeIds = new Set();

        entities.forEach(entity => {
            const e = entity.raw || entity;
            const id = entity.id || e.id || e.name || e.title;
            
            if (id && !nodeIds.has(id)) {
                nodeIds.add(id);
                nodes.push({
                    id,
                    label: entity.label || e.title || e.name || id,
                    type: entity.kind || 'node'
                });
            }

            // Add dependency links
            const deps = entity.dependencies || this.extractDependencyList(e);
            deps.forEach(dep => {
                links.push({
                    source: id,
                    target: dep,
                    type: 'depends-on'
                });
            });
        });

        return nodes.length > 0 ? { nodes, links } : null;
    }

    /**
     * Scan for dependencies recursively
     */
    static scanForDependencies(obj, entities, path = []) {
        let found = false;

        if (!obj || typeof obj !== 'object') return false;

        if (Array.isArray(obj)) {
            obj.forEach((item, idx) => {
                if (this.scanForDependencies(item, entities, [...path, idx])) {
                    found = true;
                }
            });
        } else {
            // Check if this object has dependencies
            const hasDeps = obj.depends_on || obj.dependencies || obj.requires || obj.uses;
            if (hasDeps) {
                entities.push(this.normalizeEntity(obj, 'component'));
                found = true;
            }

            // Recurse into nested objects
            for (const [key, value] of Object.entries(obj)) {
                if (this.scanForDependencies(value, entities, [...path, key])) {
                    found = true;
                }
            }
        }

        return found;
    }

    /**
     * Extract generic entities from unknown structure
     */
    static extractGenericEntities(data) {
        const entities = [];

        const extract = (obj, path = []) => {
            if (!obj || typeof obj !== 'object') return;

            if (Array.isArray(obj)) {
                obj.forEach((item, idx) => {
                    if (item && typeof item === 'object') {
                        if (item.id || item.name || item.title) {
                            entities.push(this.normalizeEntity(item, path.join('.') || 'item'));
                        } else {
                            extract(item, [...path, idx]);
                        }
                    }
                });
            } else {
                for (const [key, value] of Object.entries(obj)) {
                    if (value && typeof value === 'object') {
                        extract(value, [...path, key]);
                    }
                }
            }
        };

        extract(data);
        return entities;
    }

    /**
     * Extract dependencies from entity and add to graph
     */
    static extractDependencies(entity, graph) {
        entity.dependencies.forEach(dep => {
            graph.links.push({
                source: entity.id,
                target: dep,
                type: 'depends-on'
            });

            // Ensure target node exists
            if (!graph.nodes.find(n => n.id === dep)) {
                graph.nodes.push({
                    id: dep,
                    label: dep,
                    type: 'unknown',
                    status: 'external'
                });
            }
        });
    }
}

/**
 * Narrative Generator
 * Converts entities to human-readable text (deterministic, no AI)
 */
class NarrativeGenerator {
    /**
     * Generate executive summary from inferred schema
     */
    static generateExecutiveSummary(schemaResult) {
        const { type, entities, metadata } = schemaResult;
        const parts = [];

        // Opening
        if (type === 'registry' && metadata) {
            parts.push(`This registry contains ${metadata.total_phases || entities.length} phases`);
            if (metadata.completed) parts.push(`with ${metadata.completed} completed`);
            if (metadata.active) parts.push(`${metadata.active} active`);
            if (metadata.planned) parts.push(`and ${metadata.planned} planned`);
            parts.push('.');
        } else if (type === 'workflow') {
            parts.push(`This workflow consists of ${entities.length} sequential steps.`);
        } else if (type === 'collection') {
            parts.push(`This collection contains ${entities.length} ${schemaResult.collectionName || 'items'}.`);
        } else {
            parts.push(`This document contains ${entities.length} entities.`);
        }

        // Status breakdown
        const statusCounts = this.countByStatus(entities);
        if (Object.keys(statusCounts).length > 0) {
            const statusParts = Object.entries(statusCounts)
                .map(([status, count]) => `${count} ${status}`)
                .join(', ');
            parts.push(` Status breakdown: ${statusParts}.`);
        }

        // Relationships
        if (schemaResult.graph && schemaResult.graph.links.length > 0) {
            parts.push(` There are ${schemaResult.graph.links.length} documented relationships between components.`);
        }

        return parts.join('');
    }

    /**
     * Generate entity card narrative
     */
    static generateEntityNarrative(entity) {
        const parts = [];

        // Core identity
        parts.push(`${entity.label} is a ${entity.kind}`);
        if (entity.owner) parts.push(` owned by ${entity.owner}`);
        parts.push('.');

        // Dependencies
        if (entity.dependencies.length > 0) {
            parts.push(` It depends on ${entity.dependencies.slice(0, 3).join(', ')}`);
            if (entity.dependencies.length > 3) {
                parts.push(` and ${entity.dependencies.length - 3} others`);
            }
            parts.push('.');
        }

        // Metrics
        const metrics = Object.entries(entity.metrics).slice(0, 2);
        if (metrics.length > 0) {
            const metricStr = metrics.map(([k, v]) => `${k}: ${v}`).join(', ');
            parts.push(` Metrics: ${metricStr}.`);
        }

        return parts.join('');
    }

    /**
     * Count entities by status
     */
    static countByStatus(entities) {
        const counts = {};
        entities.forEach(e => {
            counts[e.status] = (counts[e.status] || 0) + 1;
        });
        return counts;
    }

    /**
     * Count entities by type/kind
     */
    static countByType(entities) {
        const counts = {};
        entities.forEach(e => {
            counts[e.kind] = (counts[e.kind] || 0) + 1;
        });
        return counts;
    }

    /**
     * Extract top tags
     */
    static getTopTags(entities, limit = 10) {
        const tagCounts = {};
        entities.forEach(e => {
            e.tags.forEach(tag => {
                tagCounts[tag] = (tagCounts[tag] || 0) + 1;
            });
        });

        return Object.entries(tagCounts)
            .sort((a, b) => b[1] - a[1])
            .slice(0, limit)
            .map(([tag, count]) => ({ tag, count }));
    }
}

// Export for use in app.js
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { SchemaInference, NarrativeGenerator };
}

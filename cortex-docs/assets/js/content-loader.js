/**
 * CORTEX Content Loader
 * Client-side JSON → DOM rendering
 * No server-side build required
 */

class ContentLoader {
    constructor(contentJsonPath) {
        this.contentJsonPath = contentJsonPath;
        this.contentData = null;
        this.currentRole = null;
    }

    async init() {
        try {
            const response = await fetch(this.contentJsonPath);
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }
            this.contentData = await response.json();
            console.log(`✅ Loaded ${this.contentData.categories.length} categories`);
            return this.contentData;
        } catch (error) {
            console.error('❌ Failed to load content:', error);
            throw error;
        }
    }

    getRoleConfig(roleId) {
        return this.contentData?.roles?.[roleId] || null;
    }

    getFilteredContent(roleId) {
        if (!this.contentData) {
            console.warn('Content data not loaded');
            return [];
        }

        const roleConfig = this.getRoleConfig(roleId);
        if (!roleConfig) {
            console.warn(`Role ${roleId} not found`);
            return this.contentData.categories; // Return all
        }

        // Filter categories based on role visibility
        return this.contentData.categories
            .map(category => {
                const filteredFiles = category.files.filter(file => 
                    file.roles.includes(roleId)
                );

                if (filteredFiles.length === 0) {
                    return null;
                }

                return {
                    ...category,
                    files: filteredFiles,
                    file_count: filteredFiles.length
                };
            })
            .filter(cat => cat !== null);
    }

    renderContent(roleId, containerSelector) {
        const container = document.querySelector(containerSelector);
        if (!container) {
            console.error(`Container ${containerSelector} not found`);
            return;
        }

        const filteredContent = this.getFilteredContent(roleId);
        const roleConfig = this.getRoleConfig(roleId);

        // Role guidance banner
        let html = '';
        if (roleConfig) {
            html += `
                <div class="role-guidance fade-in mb-8">
                    <strong class="font-display text-xl block mb-2">${roleConfig.icon} ${roleConfig.label}</strong>
                    <p class="font-body text-secondary">
                        Focus: ${roleConfig.focus}
                    </p>
                </div>
            `;
        }

        // Render categories in grid
        html += '<div class="cortex-grid">';
        
        filteredContent.forEach((category, index) => {
            html += `
                <div class="glass-card-concept col-span-12 lg:col-span-6 fade-in" style="animation-delay: ${index * 0.1}s;">
                    <h2 class="font-display text-xl mb-4" style="color: var(--accent-primary);">
                        ${category.title}
                    </h2>
                    <p class="font-body text-secondary mb-6 text-sm">
                        ${category.file_count} document${category.file_count !== 1 ? 's' : ''}
                    </p>
                    <div class="category-files">
                        ${this._renderFiles(category.files)}
                    </div>
                </div>
            `;
        });
        
        html += '</div>';

        container.innerHTML = html;
        this.currentRole = roleId;
    }

    _renderFiles(files) {
        return files.map(file => `
            <div class="file-item mb-6 pb-6" style="border-bottom: 1px solid var(--glass-border);">
                <h3 class="font-display text-lg mb-2">
                    <a href="#${file.category}/${file.slug}" 
                       class="hover:text-accent-primary transition-colors"
                       style="color: inherit; text-decoration: none;"
                       onclick="window.cortexLoader.loadDocument(this.getAttribute('href')); return false;">
                        ${file.title}
                    </a>
                </h3>
                <p class="font-body text-secondary text-sm leading-relaxed">
                    ${file.excerpt}
                </p>
                ${file.word_count ? `
                    <div style="margin-top: 0.5rem; font-size: 0.8rem; color: var(--accent-secondary);">
                        ${file.word_count} words
                        ${file.last_verified ? ` • Verified ${file.last_verified}` : ''}
                    </div>
                ` : ''}
            </div>
        `).join('');
    }

    loadDocument(category, slug) {
        if (!this.contentData) {
            console.error('Content data not loaded');
            return;
        }

        // Find the document
        const categoryData = this.contentData.categories.find(cat => cat.id === category);
        if (!categoryData) {
            console.error(`Category ${category} not found`);
            return;
        }

        const file = categoryData.files.find(f => f.slug === slug);
        if (!file) {
            console.error(`Document ${slug} not found in ${category}`);
            return;
        }

        // Render full document
        const container = document.querySelector('#content-area');
        if (!container) return;

        container.innerHTML = `
            <div class="fade-in">
                <button onclick="window.cortexLoader.renderContent('${this.currentRole}', '#content-area')" 
                        class="btn-primary" style="margin-bottom: 2rem;">
                    ← Back to ${this.getRoleConfig(this.currentRole)?.label || 'Overview'}
                </button>
                <div class="glass-card">
                    <span class="truth-badge implemented">Documented</span>
                    <h1 style="margin-bottom: 1rem;">${file.title}</h1>
                    <div style="color: var(--text-secondary); margin-bottom: 2rem; font-size: 0.9rem;">
                        Category: ${categoryData.title}
                        ${file.word_count ? ` • ${file.word_count} words` : ''}
                        ${file.last_verified ? ` • Verified ${file.last_verified}` : ''}
                    </div>
                    <div class="document-content">
                        ${file.content_html}
                    </div>
                </div>
            </div>
        `;

        // Scroll to top
        window.scrollTo({ top: 0, behavior: 'smooth' });
    }

    getCategoryCount(roleId) {
        return this.getFilteredContent(roleId).length;
    }

    getDocumentCount(roleId) {
        return this.getFilteredContent(roleId)
            .reduce((sum, cat) => sum + cat.file_count, 0);
    }
}

// Global instance
window.cortexLoader = null;

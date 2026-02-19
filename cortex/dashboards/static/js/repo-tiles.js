/**
 * Repository Tiles Component for CORTEX LENS Dashboard
 * 
 * Alpine.js component for displaying repository browser with searchable tiles.
 * 
 * Author: Asif Hussain
 * Orchestrator: LENSVisualizationOrchestrator
 * AC-ID: LENS-013
 */

/**
 * Creates a repository tiles Alpine.js component.
 * 
 * @param {string} apiEndpoint - API endpoint for fetching repositories
 * @returns {Object} Alpine.js component data and methods
 */
function repositoryTiles(apiEndpoint = '/api/repositories/list') {
  return {
    // State
    repositories: [],
    filteredRepositories: [],
    searchQuery: '',
    sortBy: 'name',
    sortOrder: 'asc',
    loading: true,
    error: null,
    selectedTags: [],
    
    // Initialization
    async init() {
      await this.loadRepositories();
    },
    
    /**
     * Load repositories from API.
     */
    async loadRepositories() {
      this.loading = true;
      this.error = null;
      
      try {
        const response = await fetch(apiEndpoint);
        if (!response.ok) {
          throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }
        
        const data = await response.json();
        this.repositories = data.repositories || [];
        this.applyFilters();
      } catch (error) {
        console.error('Error loading repositories:', error);
        this.error = error.message;
      } finally {
        this.loading = false;
      }
    },
    
    /**
     * Apply search and sort filters to repositories.
     */
    applyFilters() {
      let filtered = [...this.repositories];
      
      // Apply search filter
      if (this.searchQuery) {
        const query = this.searchQuery.toLowerCase();
        filtered = filtered.filter(repo => 
          repo.name.toLowerCase().includes(query) ||
          (repo.description && repo.description.toLowerCase().includes(query)) ||
          (repo.language && repo.language.toLowerCase().includes(query))
        );
      }
      
      // Apply tag filter
      if (this.selectedTags.length > 0) {
        filtered = filtered.filter(repo => 
          repo.tags && repo.tags.some(tag => this.selectedTags.includes(tag))
        );
      }
      
      // Apply sorting
      filtered.sort((a, b) => {
        let aVal = a[this.sortBy];
        let bVal = b[this.sortBy];
        
        // Handle different data types
        if (typeof aVal === 'string') {
          aVal = aVal.toLowerCase();
          bVal = bVal.toLowerCase();
        }
        
        if (this.sortOrder === 'asc') {
          return aVal > bVal ? 1 : aVal < bVal ? -1 : 0;
        } else {
          return aVal < bVal ? 1 : aVal > bVal ? -1 : 0;
        }
      });
      
      this.filteredRepositories = filtered;
    },
    
    /**
     * Handle search input change.
     */
    onSearchChange() {
      this.applyFilters();
    },
    
    /**
     * Change sort criteria.
     * 
     * @param {string} field - Field to sort by
     */
    setSortBy(field) {
      if (this.sortBy === field) {
        // Toggle sort order
        this.sortOrder = this.sortOrder === 'asc' ? 'desc' : 'asc';
      } else {
        this.sortBy = field;
        this.sortOrder = 'asc';
      }
      this.applyFilters();
    },
    
    /**
     * Toggle tag filter.
     * 
     * @param {string} tag - Tag to toggle
     */
    toggleTag(tag) {
      const index = this.selectedTags.indexOf(tag);
      if (index > -1) {
        this.selectedTags.splice(index, 1);
      } else {
        this.selectedTags.push(tag);
      }
      this.applyFilters();
    },
    
    /**
     * Clear all filters.
     */
    clearFilters() {
      this.searchQuery = '';
      this.selectedTags = [];
      this.sortBy = 'name';
      this.sortOrder = 'asc';
      this.applyFilters();
    },
    
    /**
     * Open dashboard for a repository.
     * 
     * @param {Object} repository - Repository object
     */
    openDashboard(repository) {
      // Navigate to repository-specific dashboard
      window.location.href = `/cortex?repo=${encodeURIComponent(repository.path)}`;
    },
    
    /**
     * Format date for display.
     * 
     * @param {string} dateStr - ISO date string
     * @returns {string} Formatted date
     */
    formatDate(dateStr) {
      if (!dateStr) return 'N/A';
      
      const date = new Date(dateStr);
      const now = new Date();
      const diffMs = now - date;
      const diffDays = Math.floor(diffMs / (1000 * 60 * 60 * 24));
      
      if (diffDays === 0) return 'Today';
      if (diffDays === 1) return 'Yesterday';
      if (diffDays < 7) return `${diffDays} days ago`;
      if (diffDays < 30) return `${Math.floor(diffDays / 7)} weeks ago`;
      if (diffDays < 365) return `${Math.floor(diffDays / 30)} months ago`;
      return `${Math.floor(diffDays / 365)} years ago`;
    },
    
    /**
     * Format file count for display.
     * 
     * @param {number} count - File count
     * @returns {string} Formatted count
     */
    formatFileCount(count) {
      if (count >= 1000) {
        return `${(count / 1000).toFixed(1)}k`;
      }
      return count.toString();
    },
    
    /**
     * Get language badge color.
     * 
     * @param {string} language - Programming language
     * @returns {string} Tailwind color class
     */
    getLanguageColor(language) {
      const colors = {
        'Python': 'bg-blue-500',
        'JavaScript': 'bg-yellow-500',
        'TypeScript': 'bg-blue-600',
        'Java': 'bg-red-500',
        'Go': 'bg-cyan-500',
        'Rust': 'bg-orange-500',
        'C++': 'bg-pink-500',
        'Ruby': 'bg-red-600',
        'PHP': 'bg-purple-500',
        'Swift': 'bg-orange-600',
      };
      return colors[language] || 'bg-gray-500';
    },
    
    /**
     * Get all unique tags from repositories.
     * 
     * @returns {Array<string>} Array of unique tags
     */
    get allTags() {
      const tags = new Set();
      this.repositories.forEach(repo => {
        if (repo.tags) {
          repo.tags.forEach(tag => tags.add(tag));
        }
      });
      return Array.from(tags).sort();
    },
    
    /**
     * Get repository count.
     * 
     * @returns {number} Number of filtered repositories
     */
    get repositoryCount() {
      return this.filteredRepositories.length;
    }
  };
}

/**
 * Example repository data structure:
 * 
 * {
 *   name: "CORTEX",
 *   path: "/Users/asifhussain/PROJECTS/CORTEX",
 *   description: "Cognitive Real-Time Execution System",
 *   language: "Python",
 *   fileCount: 1247,
 *   lastModified: "2026-01-29T10:30:00Z",
 *   tags: ["ai", "automation", "orchestration"],
 *   stats: {
 *     lines: 125000,
 *     functions: 2500,
 *     classes: 350,
 *     testCoverage: 92.5
 *   }
 * }
 * 
 * // Usage in Alpine.js:
 * <div x-data="repositoryTiles('/api/repositories/list')">
 *   <!-- Search and Filters -->
 *   <div class="mb-6">
 *     <input 
 *       x-model="searchQuery"
 *       @input="onSearchChange"
 *       type="text"
 *       placeholder="Search repositories..."
 *       class="w-full px-4 py-2 rounded-lg"
 *     />
 *   </div>
 *   
 *   <!-- Repository Tiles Grid -->
 *   <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
 *     <template x-for="repo in filteredRepositories" :key="repo.path">
 *       <div 
 *         @click="openDashboard(repo)"
 *         class="glass-card cursor-pointer hover:scale-105 transition-transform"
 *       >
 *         <h3 x-text="repo.name" class="text-xl font-bold"></h3>
 *         <p x-text="repo.description" class="text-sm text-gray-600"></p>
 *         <div class="mt-2">
 *           <span x-text="repo.language" class="badge badge-primary"></span>
 *         </div>
 *       </div>
 *     </template>
 *   </div>
 * </div>
 */

// Export for use in modules
if (typeof module !== 'undefined' && module.exports) {
  module.exports = { repositoryTiles };
}

/**
 * CORTEX Gantt Chart Visualization
 * Interactive Gantt chart using Frappe Gantt library
 * Displays CORTEX 4.0 development timeline with progress tracking
 */

class GanttChartVisualization {
    constructor() {
        this.data = null;
        this.gantt = null;
        this.allTasks = [];
        this.filteredTasks = [];
        this.currentViewMode = 'Month';
    }
    
    async init() {
        console.log('Initializing Gantt Chart Visualization...');
        
        // Setup controls
        this.setupControls();
        
        // Load data
        await this.loadData();
        
        // Render chart
        this.renderGantt();
        
        // Render statistics
        this.renderStatistics();
        
        // Render milestone progress
        this.renderMilestoneProgress();
        
        console.log('Gantt Chart initialized successfully');
    }
    
    setupControls() {
        // View mode selector
        document.getElementById('viewMode').addEventListener('change', (e) => {
            this.currentViewMode = e.target.value;
            this.updateGanttView();
        });
        
        // Status filter
        document.getElementById('filterStatus').addEventListener('change', (e) => {
            this.filterByStatus(e.target.value);
        });
        
        // Milestone filter
        document.getElementById('filterMilestone').addEventListener('change', (e) => {
            this.filterByMilestone(e.target.value);
        });
        
        // Reset filters
        document.getElementById('resetFilters').addEventListener('click', () => {
            this.resetFilters();
        });
        
        // Export CSV
        document.getElementById('exportCSV').addEventListener('click', () => {
            this.exportToCSV();
        });
        
        // Print view
        document.getElementById('printView').addEventListener('click', () => {
            window.print();
        });
        
        // Close task detail
        document.getElementById('closeTaskDetail').addEventListener('click', () => {
            this.closeTaskDetail();
        });
    }
    
    async loadData() {
        try {
            const response = await fetch('../assets/data/gantt-data.json');
            this.data = await response.json();
            this.allTasks = this.data.tasks || [];
            this.filteredTasks = [...this.allTasks];
            console.log('Loaded Gantt data:', this.data);
            
            // Populate milestone filter
            this.populateMilestoneFilter();
        } catch (error) {
            console.error('Error loading Gantt data:', error);
            this.data = this.getMockData();
            this.allTasks = this.data.tasks || [];
            this.filteredTasks = [...this.allTasks];
        }
    }
    
    getMockData() {
        const today = new Date();
        const oneMonthLater = new Date(today.getTime() + 30 * 24 * 60 * 60 * 1000);
        const threeMonthsLater = new Date(today.getTime() + 90 * 24 * 60 * 60 * 1000);
        
        return {
            tasks: [
                {
                    id: 'milestone-0',
                    name: 'CORTEX 3.1 Release',
                    start: today.toISOString().split('T')[0],
                    end: oneMonthLater.toISOString().split('T')[0],
                    progress: 0,
                    type: 'milestone',
                    custom_class: 'milestone-bar'
                },
                {
                    id: 'feature-0-0',
                    name: 'Multi-Agent Orchestration',
                    start: today.toISOString().split('T')[0],
                    end: oneMonthLater.toISOString().split('T')[0],
                    progress: 60,
                    type: 'task',
                    dependencies: 'milestone-0',
                    custom_class: 'status-in-progress',
                    milestone: 'CORTEX 3.1 Release',
                    status: 'in-progress'
                }
            ],
            statistics: {
                total_tasks: 2,
                completed_tasks: 0,
                in_progress_tasks: 1,
                pending_tasks: 1,
                average_progress: 30
            }
        };
    }
    
    populateMilestoneFilter() {
        const milestones = new Set();
        this.allTasks.forEach(task => {
            if (task.milestone) {
                milestones.add(task.milestone);
            }
        });
        
        const select = document.getElementById('filterMilestone');
        milestones.forEach(milestone => {
            const option = document.createElement('option');
            option.value = milestone;
            option.textContent = milestone;
            select.appendChild(option);
        });
    }
    
    renderGantt() {
        if (!this.filteredTasks || this.filteredTasks.length === 0) {
            document.querySelector('.gantt-wrapper').innerHTML = '<p style="padding: 40px; text-align: center; color: rgba(255,255,255,0.6);">No tasks to display. Adjust filters or check data source.</p>';
            return;
        }
        
        const ganttContainer = document.getElementById('ganttChart');
        
        try {
            this.gantt = new Frappe.Gantt(ganttContainer, this.filteredTasks, {
                view_mode: this.currentViewMode,
                bar_height: 30,
                bar_corner_radius: 3,
                arrow_curve: 5,
                padding: 18,
                view_modes: ['Week', 'Month', 'Quarter', 'Year'],
                date_format: 'YYYY-MM-DD',
                custom_popup_html: (task) => {
                    return this.getTaskPopupHTML(task);
                },
                on_click: (task) => {
                    this.showTaskDetail(task);
                },
                on_date_change: (task, start, end) => {
                    console.log('Task date changed:', task.name, start, end);
                },
                on_progress_change: (task, progress) => {
                    console.log('Task progress changed:', task.name, progress);
                },
                on_view_change: (mode) => {
                    console.log('View mode changed:', mode);
                }
            });
        } catch (error) {
            console.error('Error creating Gantt chart:', error);
            document.querySelector('.gantt-wrapper').innerHTML = '<p style="padding: 40px; text-align: center; color: rgba(255,255,255,0.6);">Error rendering Gantt chart. Please check console for details.</p>';
        }
    }
    
    getTaskPopupHTML(task) {
        const startDate = new Date(task.start).toLocaleDateString();
        const endDate = new Date(task.end).toLocaleDateString();
        const duration = Math.ceil((new Date(task.end) - new Date(task.start)) / (1000 * 60 * 60 * 24));
        
        return `
            <div class="gantt-popup">
                <div class="popup-header">${task.name}</div>
                <div class="popup-body">
                    <div class="popup-row">
                        <span class="popup-label">Timeline:</span>
                        <span>${startDate} → ${endDate}</span>
                    </div>
                    <div class="popup-row">
                        <span class="popup-label">Duration:</span>
                        <span>${duration} days</span>
                    </div>
                    <div class="popup-row">
                        <span class="popup-label">Progress:</span>
                        <span>${task.progress}%</span>
                    </div>
                    ${task.milestone ? `
                    <div class="popup-row">
                        <span class="popup-label">Milestone:</span>
                        <span>${task.milestone}</span>
                    </div>
                    ` : ''}
                    ${task.status ? `
                    <div class="popup-row">
                        <span class="popup-label">Status:</span>
                        <span class="status-badge status-${task.status}">${task.status.replace('-', ' ')}</span>
                    </div>
                    ` : ''}
                </div>
                <div class="popup-footer">Click for details</div>
            </div>
        `;
    }
    
    showTaskDetail(task) {
        document.getElementById('taskDetailName').textContent = task.name;
        document.getElementById('taskDetailType').textContent = task.type === 'milestone' ? 'Milestone' : 'Feature';
        document.getElementById('taskDetailMilestone').textContent = task.milestone || 'N/A';
        
        const startDate = new Date(task.start).toLocaleDateString();
        const endDate = new Date(task.end).toLocaleDateString();
        document.getElementById('taskDetailTimeline').textContent = `${startDate} → ${endDate}`;
        
        document.getElementById('taskDetailStatus').textContent = task.status ? task.status.replace('-', ' ') : 'Unknown';
        
        const progressBar = document.querySelector('#taskDetailProgress .progress-bar-fill');
        progressBar.style.width = `${task.progress}%`;
        progressBar.textContent = `${task.progress}%`;
        
        document.getElementById('taskDetailDeps').textContent = task.dependencies || 'None';
        
        document.getElementById('taskDetail').style.display = 'block';
    }
    
    closeTaskDetail() {
        document.getElementById('taskDetail').style.display = 'none';
    }
    
    updateGanttView() {
        if (this.gantt) {
            this.gantt.change_view_mode(this.currentViewMode);
        }
    }
    
    filterByStatus(status) {
        if (status === 'all') {
            this.filteredTasks = [...this.allTasks];
        } else {
            this.filteredTasks = this.allTasks.filter(task => task.status === status);
        }
        this.renderGantt();
    }
    
    filterByMilestone(milestone) {
        if (milestone === 'all') {
            this.filteredTasks = [...this.allTasks];
        } else {
            this.filteredTasks = this.allTasks.filter(task => 
                task.milestone === milestone || task.type === 'milestone'
            );
        }
        this.renderGantt();
    }
    
    resetFilters() {
        document.getElementById('viewMode').value = 'Month';
        document.getElementById('filterStatus').value = 'all';
        document.getElementById('filterMilestone').value = 'all';
        
        this.currentViewMode = 'Month';
        this.filteredTasks = [...this.allTasks];
        this.renderGantt();
    }
    
    renderStatistics() {
        if (!this.data || !this.data.statistics) return;
        
        const stats = this.data.statistics;
        
        document.getElementById('totalTasks').textContent = stats.total_tasks || 0;
        document.getElementById('completedTasks').textContent = stats.completed_tasks || 0;
        document.getElementById('inProgressTasks').textContent = stats.in_progress_tasks || 0;
        document.getElementById('avgProgress').textContent = `${stats.average_progress || 0}%`;
    }
    
    renderMilestoneProgress() {
        const container = document.getElementById('milestoneProgress');
        
        // Group tasks by milestone
        const milestones = {};
        this.allTasks.forEach(task => {
            if (task.type === 'milestone') {
                milestones[task.name] = {
                    milestone: task,
                    features: []
                };
            }
        });
        
        this.allTasks.forEach(task => {
            if (task.type === 'task' && task.milestone) {
                if (milestones[task.milestone]) {
                    milestones[task.milestone].features.push(task);
                }
            }
        });
        
        // Render progress bars for each milestone
        container.innerHTML = '';
        Object.keys(milestones).forEach(milestoneName => {
            const milestoneData = milestones[milestoneName];
            const features = milestoneData.features;
            
            if (features.length === 0) return;
            
            const avgProgress = features.reduce((sum, f) => sum + f.progress, 0) / features.length;
            
            const milestoneDiv = document.createElement('div');
            milestoneDiv.className = 'milestone-progress-item';
            milestoneDiv.innerHTML = `
                <div class="milestone-progress-header">
                    <span class="milestone-name">${milestoneName}</span>
                    <span class="milestone-percentage">${Math.round(avgProgress)}%</span>
                </div>
                <div class="progress-bar-container">
                    <div class="progress-bar-fill" style="width: ${avgProgress}%"></div>
                </div>
                <div class="milestone-features-count">${features.length} features</div>
            `;
            
            container.appendChild(milestoneDiv);
        });
    }
    
    exportToCSV() {
        if (!this.allTasks || this.allTasks.length === 0) {
            alert('No data to export');
            return;
        }
        
        // CSV header
        let csv = 'Task Name,Type,Start Date,End Date,Progress,Status,Milestone,Dependencies\n';
        
        // CSV rows
        this.allTasks.forEach(task => {
            const row = [
                `"${task.name}"`,
                task.type,
                task.start,
                task.end,
                task.progress,
                task.status || 'N/A',
                task.milestone || 'N/A',
                task.dependencies || 'None'
            ];
            csv += row.join(',') + '\n';
        });
        
        // Create download link
        const blob = new Blob([csv], { type: 'text/csv' });
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `cortex-gantt-${new Date().toISOString().split('T')[0]}.csv`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        window.URL.revokeObjectURL(url);
    }
}

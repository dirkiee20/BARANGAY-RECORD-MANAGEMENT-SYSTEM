// Dashboard JavaScript - Handles dynamic updates and interactivity
class DashboardManager {
    constructor() {
        this.refreshInterval = null;
        this.isLoading = false;
        this.init();
    }

    init() {
        this.bindEvents();
        this.startAutoRefresh();
        this.loadInitialData();
    }

    bindEvents() {
        // Refresh button
        const refreshBtn = document.querySelector('.btn[onclick="refreshDashboard()"]');
        if (refreshBtn) {
            refreshBtn.addEventListener('click', (e) => this.handleRefresh(e));
        }

        // New Record button
        const newRecordBtn = document.getElementById('newRecordBtn');
        if (newRecordBtn) {
            newRecordBtn.addEventListener('click', () => this.showNewRecordModal());
        }

        // Search functionality
        const searchInput = document.querySelector('.search');
        if (searchInput) {
            searchInput.addEventListener('input', (e) => this.handleSearch(e.target.value));
        }

        // Action buttons
        this.bindActionButtons();
    }

    async handleRefresh(e) {
        e.preventDefault();
        if (this.isLoading) return;

        const btn = e.target;
        const originalText = btn.innerHTML;
        
        this.showLoadingState(btn);
        await this.fetchDashboardData();
        this.hideLoadingState(btn, originalText);
    }

    showLoadingState(btn) {
        this.isLoading = true;
        btn.innerHTML = '⏳ Loading...';
        btn.disabled = true;
        btn.classList.add('loading');
    }

    hideLoadingState(btn, originalText) {
        this.isLoading = false;
        btn.innerHTML = originalText;
        btn.disabled = false;
        btn.classList.remove('loading');
    }

    async loadInitialData() {
        await this.fetchDashboardData();
    }

    async fetchDashboardData() {
        try {
            this.showGlobalLoading();
            
            const response = await fetch('/api/dashboard-stats');
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            const data = await response.json();
            this.updateDashboard(data);
            
        } catch (error) {
            console.error('Error fetching dashboard data:', error);
            this.showError('Failed to load dashboard data');
        } finally {
            this.hideGlobalLoading();
        }
    }

    updateDashboard(data) {
        this.updateStatistics(data.stats);
        this.updateRecentResidents(data.recent_residents);
        this.updateOpenBlotters(data.open_blotters);
        this.updateClearanceSummary(data.clearance_summary);
        
        // Update charts if they exist
        if (window.dashboardCharts) {
            this.updateCharts(data);
        }
    }

    updateStatistics(stats) {
        const statElements = {
            'total_residents': document.querySelector('.stat-card:nth-child(1) .stat-value'),
            'total_households': document.querySelector('.stat-card:nth-child(2) .stat-value'),
            'active_blotters': document.querySelector('.stat-card:nth-child(3) .stat-value'),
            'clearances_issued_month': document.querySelector('.stat-card:nth-child(4) .stat-value')
        };

        Object.keys(statElements).forEach(key => {
            if (statElements[key] && stats[key] !== undefined) {
                statElements[key].textContent = this.formatNumber(stats[key]);
            }
        });

        // Update weekly indicators
        const weeklyElements = {
            'new_residents_week': document.querySelector('.stat-card:nth-child(1) .stat-sub'),
            'new_households_week': document.querySelector('.stat-card:nth-child(2) .stat-sub'),
            'blotters_due_today': document.querySelector('.stat-card:nth-child(3) .stat-sub'),
        };

        if (weeklyElements.new_residents_week) {
            weeklyElements.new_residents_week.textContent = `+${stats.new_residents_week || 0} this week`;
        }
        if (weeklyElements.new_households_week) {
            weeklyElements.new_households_week.textContent = `+${stats.new_households_week || 0} this week`;
        }
        if (weeklyElements.blotters_due_today) {
            weeklyElements.blotters_due_today.textContent = `${stats.blotters_due_today || 0} due today`;
        }
    }

    updateRecentResidents(residents) {
        const tbody = document.querySelector('.panel:nth-child(1) .table tbody');
        if (!tbody) return;

        tbody.innerHTML = '';
        
        if (residents.length === 0) {
            tbody.innerHTML = `
                <tr>
                    <td colspan="5" style="text-align: center; color: var(--muted);">No residents found</td>
                </tr>
            `;
            return;
        }

        residents.forEach(resident => {
            const row = document.createElement('tr');
            const address = resident.address || 'N/A';
            row.innerHTML = `
                <td>${resident.first_name} ${resident.last_name}</td>
                <td class="address-cell" title="${address}">${address}</td>
                <td>${resident.age || 'N/A'}</td>
                <td><span class="badge success">${resident.status || 'Active'}</span></td>
                <td class="actions">
                    <button class="icon-btn" onclick="dashboardManager.viewResident(${resident.id})">⋯</button>
                </td>
            `;
            tbody.appendChild(row);
        });
    }

    updateOpenBlotters(blotters) {
        const list = document.querySelector('.panel:nth-child(2) .list');
        if (!list) return;

        list.innerHTML = '';
        
        if (blotters.length === 0) {
            list.innerHTML = `
                <li>
                    <div>
                        <div class="list-title">No Open Cases</div>
                        <div class="list-sub">All cases are currently resolved</div>
                    </div>
                    <span class="badge success">Good!</span>
                </li>
            `;
            return;
        }

        blotters.forEach(blotter => {
            const li = document.createElement('li');
            const reporterName = blotter.reported_by ? 
                `${blotter.reported_by.first_name} ${blotter.reported_by.last_name}` : 
                'Anonymous';
            
            li.innerHTML = `
                <div>
                    <div class="list-title">${blotter.case_title}</div>
                    <div class="list-sub">
                        Reported by: ${reporterName}
                        ${blotter.location ? ` · ${blotter.location}` : ''}
                    </div>
                </div>
                <span class="badge warning">
                    ${this.isDueToday(blotter.hearing_date) ? 'Due today' : 'Open'}
                </span>
            `;
            list.appendChild(li);
        });
    }

    updateClearanceSummary(summary) {
        const clearanceList = document.querySelector('.panel:nth-child(3) .list');
        if (!clearanceList) return;

        const items = clearanceList.querySelectorAll('li');
        
        if (items.length >= 2) {
            // Update first item (Barangay Clearance)
            const firstItem = items[0];
            const firstSub = firstItem.querySelector('.list-sub');
            const firstBadge = firstItem.querySelector('.badge');
            
            if (firstSub) {
                firstSub.textContent = `Pending: ${summary.pending} · Processed today: ${summary.processed_today}`;
            }
            if (firstBadge) {
                firstBadge.textContent = summary.pending > 0 ? 'Pending' : 'All Clear';
                firstBadge.className = `badge ${summary.pending > 0 ? 'info' : 'success'}`;
            }

            // Update second item (Indigency Certificate)
            const secondItem = items[1];
            const secondSub = secondItem.querySelector('.list-sub');
            const secondBadge = secondItem.querySelector('.badge');
            
            if (secondSub) {
                secondSub.textContent = `Pending: ${summary.pending} · Processed today: ${summary.processed_today}`;
            }
            if (secondBadge) {
                secondBadge.textContent = summary.processed_today > 0 ? 'On track' : 'No activity';
                secondBadge.className = `badge ${summary.processed_today > 0 ? 'success' : ''}`;
            }
        }
    }

    bindActionButtons() {
        // View all buttons
        document.addEventListener('click', (e) => {
            if (e.target.textContent.includes('View all')) {
                const section = e.target.closest('.panel').querySelector('h3').textContent;
                if (section.includes('Residents')) {
                    window.location.href = '/residents';
                } else if (section.includes('Blotters')) {
                    window.location.href = '/blotter';
                }
            }
            
            if (e.target.textContent.includes('Manage')) {
                window.location.href = '/clearances';
            }
        });
    }

    handleSearch(query) {
        // Implement search functionality
        if (query.length < 2) return;
        
        // Search through residents and blotters
        this.searchRecords(query);
    }

    async searchRecords(query) {
        try {
            const response = await fetch(`/api/search?q=${encodeURIComponent(query)}`);
            if (response.ok) {
                const results = await response.json();
                this.displaySearchResults(results);
            }
        } catch (error) {
            console.error('Search error:', error);
        }
    }

    displaySearchResults(results) {
        // Create and show search results modal or dropdown
        console.log('Search results:', results);
    }

    startAutoRefresh() {
        this.refreshInterval = setInterval(() => {
            if (!document.hidden && !this.isLoading) {
                this.fetchDashboardData();
            }
        }, 5 * 60 * 1000); // 5 minutes
    }

    stopAutoRefresh() {
        if (this.refreshInterval) {
            clearInterval(this.refreshInterval);
            this.refreshInterval = null;
        }
    }

    showGlobalLoading() {
        const loadingOverlay = document.createElement('div');
        loadingOverlay.className = 'loading-overlay';
        loadingOverlay.innerHTML = `
            <div class="loading-spinner">
                <div class="spinner"></div>
                <p>Loading...</p>
            </div>
        `;
        document.body.appendChild(loadingOverlay);
    }

    hideGlobalLoading() {
        const loadingOverlay = document.querySelector('.loading-overlay');
        if (loadingOverlay) {
            loadingOverlay.remove();
        }
    }

    showError(message) {
        const errorDiv = document.createElement('div');
        errorDiv.className = 'error-message';
        errorDiv.textContent = message;
        document.body.appendChild(errorDiv);
        
        setTimeout(() => {
            errorDiv.remove();
        }, 5000);
    }

    formatNumber(num) {
        return new Intl.NumberFormat().format(num);
    }

    isDueToday(hearingDate) {
        if (!hearingDate) return false;
        const today = new Date().toDateString();
        const hearing = new Date(hearingDate).toDateString();
        return today === hearing;
    }

    viewResident(id) {
        window.location.href = `/residents/${id}`;
    }

    updateCharts(data) {
        // Update Chart.js charts if they exist
        if (window.dashboardCharts && window.dashboardCharts.updateData) {
            window.dashboardCharts.updateData(data);
        }
    }

    // New Record Form Methods
    showNewRecordModal() {
        console.log('showNewRecordModal called');
        const modal = document.getElementById('newRecordModal');
        if (modal) {
            console.log('Modal found, showing...');
            modal.style.display = 'block';
            this.loadRecordTypes();
            this.bindFormEvents();
        } else {
            console.error('Modal not found!');
        }
    }

    hideNewRecordModal() {
        const modal = document.getElementById('newRecordModal');
        if (modal) {
            modal.style.display = 'none';
            this.resetNewRecordForm();
        }
    }

    bindFormEvents() {
        // Bind record type change event
        const recordTypeSelect = document.getElementById('recordType');
        if (recordTypeSelect) {
            recordTypeSelect.addEventListener('change', (e) => {
                this.showRecordTypeFields(e.target.value);
            });
        }

        // Bind form submission
        const form = document.getElementById('newRecordForm');
        if (form) {
            form.addEventListener('submit', (e) => this.handleNewRecordSubmit(e));
        }

        // Bind close button
        const closeBtn = document.getElementById('closeModal');
        if (closeBtn) {
            closeBtn.addEventListener('click', () => this.hideNewRecordModal());
        }

        // Close modal when clicking outside
        const modal = document.getElementById('newRecordModal');
        if (modal) {
            modal.addEventListener('click', (e) => {
                if (e.target === modal) {
                    this.hideNewRecordModal();
                }
            });
        }

        // Bind profile picture uploader
        const uploader = document.querySelector('.profile-uploader');
        if (uploader) {
            const fileInput = document.getElementById('profilePicture');
            const preview = document.getElementById('profilePreview');

            uploader.addEventListener('click', () => fileInput.click());

            fileInput.addEventListener('change', (e) => {
                const file = e.target.files[0];
                if (file) {
                    const reader = new FileReader();
                    reader.onload = (event) => {
                        preview.src = event.target.result;
                    };
                    reader.readAsDataURL(file);
                }
            });

            // Drag and drop
            uploader.addEventListener('dragover', (e) => {
                e.preventDefault();
                uploader.classList.add('dragging');
            });

            uploader.addEventListener('dragleave', () => {
                uploader.classList.remove('dragging');
            });

            uploader.addEventListener('drop', (e) => {
                e.preventDefault();
                uploader.classList.remove('dragging');
                const file = e.dataTransfer.files[0];
                if (file) {
                    fileInput.files = e.dataTransfer.files;
                    const reader = new FileReader();
                    reader.onload = (event) => {
                        preview.src = event.target.result;
                    };
                    reader.readAsDataURL(file);
                }
            });
        }
    }

    showRecordTypeFields(recordType) {
        // Hide and disable all fieldsets first.
        document.querySelectorAll('.record-fields').forEach(fieldset => {
            fieldset.style.display = 'none';
            fieldset.querySelectorAll('input, select, textarea').forEach(input => {
                input.disabled = true;
            });
        });

        // If a record type is selected, show and enable its fields.
        if (recordType) {
            const activeFieldset = document.getElementById(`${recordType}Fields`);
            if (activeFieldset) {
                activeFieldset.style.display = 'block';
                activeFieldset.querySelectorAll('input, select, textarea').forEach(input => {
                    input.disabled = false;
                });
            }
        }

        // Special handling for clearance form to load residents.
        if (recordType === 'clearance') {
            this.loadResidentsForClearance();
        }
    }

    async loadResidentsForClearance() {
        try {
            const response = await fetch('/api/residents');
            if (response.ok) {
                const residents = await response.json();
                this.populateResidentSelect(residents);
            }
        } catch (error) {
            console.error('Error loading residents:', error);
        }
    }

    populateResidentSelect(residents) {
        const select = document.getElementById('residentId');
        if (select) {
            select.innerHTML = '<option value="">Select Resident</option>';
            residents.forEach(resident => {
                const option = document.createElement('option');
                option.value = resident.id;
                option.textContent = `${resident.first_name} ${resident.last_name} - ${resident.address}`;
                select.appendChild(option);
            });
        }
    }

    async loadRecordTypes() {
        try {
            const response = await fetch('/api/record-types');
            if (response.ok) {
                const types = await response.json();
                this.populateRecordTypeSelect(types);
            }
        } catch (error) {
            console.error('Error loading record types:', error);
        }
    }

    populateRecordTypeSelect(types) {
        const select = document.getElementById('recordType');
        if (select) {
            select.innerHTML = '<option value="">Select Record Type</option>';
            types.forEach(type => {
                const option = document.createElement('option');
                option.value = type.value;
                option.textContent = type.label;
                select.appendChild(option);
            });
        }
    }

    async handleNewRecordSubmit(e) {
        e.preventDefault();
        
        const form = e.target;
        const formData = new FormData(form);
        
        // Validate required fields
        const recordType = formData.get('recordType');
        if (!recordType) {
            this.showError('Please select a record type');
            return;
        }
        
        // Show loading state
        const submitBtn = form.querySelector('button[type="submit"]');
        const originalText = submitBtn.textContent;
        submitBtn.textContent = 'Creating...';
        submitBtn.disabled = true;
        
        try {
            const response = await fetch('/api/new-record', {
                method: 'POST',
                body: formData
            });
            
            const result = await response.json();
            if (response.ok) {
                this.showSuccess(result.message || 'Record created successfully!');
                this.hideNewRecordModal();
                this.fetchDashboardData(); // Refresh dashboard
            } else {
                this.showError(result.error || 'Failed to create record');
            }
        } catch (error) {
            console.error('Error creating record:', error);
            this.showError('An unexpected error occurred. Please try again.');
        } finally {
            // Restore button state
            submitBtn.textContent = originalText;
            submitBtn.disabled = false;
        }
    }

    resetNewRecordForm() {
        const form = document.getElementById('newRecordForm');
        if (form) {
            form.reset();
        }
        
        // Hide and disable all record fields
        document.querySelectorAll('.record-fields').forEach(fieldset => {
            fieldset.style.display = 'none';
            fieldset.querySelectorAll('input, select, textarea').forEach(input => {
                input.disabled = true;
            });
        });
    }

    showSuccess(message) {
        const successDiv = document.createElement('div');
        successDiv.className = 'success-message';
        successDiv.textContent = message;
        document.body.appendChild(successDiv);
        
        setTimeout(() => {
            successDiv.remove();
        }, 5000);
    }
}

// Initialize dashboard when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.dashboardManager = new DashboardManager();
});

// Global refresh function for onclick handlers
function refreshDashboard() {
    if (window.dashboardManager) {
        window.dashboardManager.handleRefresh(new Event('click'));
    }
}

// Global function to show new record modal
function showNewRecordModal() {
    if (window.dashboardManager) {
        window.dashboardManager.showNewRecordModal();
    }
}

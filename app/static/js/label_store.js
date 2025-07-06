/**
 * Label Store Management - Task 2.4
 * JavaScript per gestione etichette centralizzato
 */

document.addEventListener('DOMContentLoaded', function() {
    console.log('🔵 Label Store JavaScript loaded successfully');
    
    // Initialize Materialize components
    M.Modal.init(document.querySelectorAll('.modal'));
    M.FormSelect.init(document.querySelectorAll('select'));
    M.updateTextFields();

    // Get project ID from URL
    const projectId = window.location.pathname.split('/')[2];
    console.log('🔵 Project ID extracted:', projectId);

    // Check authentication status on page load
    async function checkAuthStatus() {
        try {
            const response = await fetch('/api/auth/status', {
                credentials: 'same-origin'
            });
            
            if (response.ok) {
                const data = await response.json();
                console.log('🔵 User authenticated:', data);
                return true;
            } else {
                console.log('❌ User not authenticated');
                // Show login message
                M.toast({html: 'Devi effettuare il login per gestire le etichette', classes: 'orange'});
                return false;
            }
        } catch (error) {
            console.error('❌ Auth check failed:', error);
            return false;
        }
    }

    // Initialize event listeners
    console.log('🔵 Initializing event listeners...');
    initializeEventListeners();
    loadAISuggestions();
    console.log('🔵 Event listeners initialized successfully');
    setupFiltersAndSearch();
    
    // Check auth status
    checkAuthStatus();
    
    // Add global test function for debugging
    window.testLabelAPI = function() {
        console.log('🧪 Testing Label API...');
        console.log('Project ID:', projectId);
        
        // Test auth status
        fetch('/api/auth/status', { credentials: 'same-origin' })
            .then(response => {
                console.log('Auth status:', response.status);
                return response.json();
            })
            .then(data => console.log('Auth data:', data))
            .catch(err => console.error('Auth error:', err));
            
        // Test labels API
        fetch(`/api/projects/${projectId}/labels`, { credentials: 'same-origin' })
            .then(response => {
                console.log('Labels status:', response.status);
                return response.json();
            })
            .then(data => console.log('Labels data:', data))
            .catch(err => console.error('Labels error:', err));
    };

    function initializeEventListeners() {
        console.log('🔵 Setting up event listeners...');
        
        // Debug: Check if main table exists
        const labelsTable = document.getElementById('labels-table-body');
        if (labelsTable) {
            console.log(`✅ Labels table found with ${labelsTable.children.length} rows`);
        } else {
            console.log('❌ Labels table not found');
        }
        
        // Create label
        const saveNewBtn = document.getElementById('save-new-label');
        if (saveNewBtn) {
            saveNewBtn.addEventListener('click', handleCreateLabel);
            console.log('✅ Create label button listener added');
        }
        
        // Edit label
        const editBtns = document.querySelectorAll('.edit-label-btn');
        console.log(`🔵 Found ${editBtns.length} edit buttons`);
        editBtns.forEach(btn => {
            btn.addEventListener('click', handleEditLabelClick);
        });
        
        const saveEditBtn = document.getElementById('save-edit-label');
        if (saveEditBtn) {
            saveEditBtn.addEventListener('click', handleEditLabel);
            console.log('✅ Edit label button listener added');
        }
        
        // View cell values
        const viewCellsBtns = document.querySelectorAll('.view-cells-btn');
        console.log(`🔵 Found ${viewCellsBtns.length} view cells buttons`);
        viewCellsBtns.forEach(btn => {
            btn.addEventListener('click', handleViewCellsClick);
        });
        
        // Delete label
        const deleteBtns = document.querySelectorAll('.delete-label-btn');
        console.log(`🔵 Found ${deleteBtns.length} delete buttons`);
        deleteBtns.forEach(btn => {
            btn.addEventListener('click', handleDeleteLabelClick);
        });
        
        const confirmDeleteBtn = document.getElementById('confirm-delete-label');
        if (confirmDeleteBtn) {
            confirmDeleteBtn.addEventListener('click', handleDeleteLabel);
            console.log('✅ Delete confirmation button listener added');
        }
        
        // AI Suggestions
        document.getElementById('approve-all-suggestions')?.addEventListener('click', handleApproveAllSuggestions);
        document.getElementById('reject-all-suggestions')?.addEventListener('click', handleRejectAllSuggestions);
    }

    function setupFiltersAndSearch() {
        // Search functionality
        const searchInput = document.getElementById('search-labels');
        if (searchInput) {
            searchInput.addEventListener('input', debounce(handleSearch, 300));
        }

        // Sort functionality
        const sortSelect = document.getElementById('sort-by');
        if (sortSelect) {
            sortSelect.addEventListener('change', handleSort);
        }

        // Category filter
        const categoryFilter = document.getElementById('filter-category');
        if (categoryFilter) {
            categoryFilter.addEventListener('change', handleCategoryFilter);
        }
    }

    async function handleCreateLabel() {
        console.log('🔵 handleCreateLabel called'); // Debug
        
        const name = document.getElementById('create-label-name').value.trim();
        const description = document.getElementById('create-label-description').value.trim();
        const color = document.getElementById('create-label-color').value;
        const categoriesText = document.getElementById('create-label-categories').value.trim();
        const categories = categoriesText ? categoriesText.split(',').map(c => c.trim()).filter(c => c) : [];

        console.log('🔵 Form data:', { name, description, color, categories }); // Debug
        console.log('🔵 Project ID:', projectId); // Debug

        if (!name || !description) {
            console.log('❌ Validation failed: missing name or description');
            M.toast({html: 'Nome e descrizione sono obbligatori', classes: 'red'});
            return;
        }

        console.log('🔵 Starting API call...');
        
        try {
            const apiUrl = `/api/projects/${projectId}/labels`;
            console.log('🔵 API URL:', apiUrl);
            
            const response = await fetch(apiUrl, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-Requested-With': 'XMLHttpRequest'
                },
                credentials: 'same-origin',
                body: JSON.stringify({
                    name: name,
                    description: description,
                    color: color,
                    categories: categories
                })
            });

            console.log('🔵 Response status:', response.status);
            console.log('🔵 Response headers:', Object.fromEntries(response.headers.entries()));
            
            const data = await response.json();
            console.log('🔵 Response data:', data); // Debug

            if (response.ok && (data.success || data.message)) {
                console.log('✅ Label created successfully');
                M.toast({html: data.message || 'Etichetta creata con successo!', classes: 'green'});
                
                // Reset form
                document.getElementById('create-label-form').reset();
                
                // Close modal
                const modal = M.Modal.getInstance(document.getElementById('create-label-modal'));
                modal.close();
                
                // Reload page to show new label
                setTimeout(() => {
                    window.location.reload();
                }, 1000);
            } else {
                console.log('❌ API error:', data);
                M.toast({html: data.error || 'Errore nella creazione dell\'etichetta', classes: 'red'});
            }
        } catch (error) {
            console.error('❌ Network error:', error);
            M.toast({html: 'Errore di connessione', classes: 'red'});
        }
    }

    function handleEditLabelClick(event) {
        console.log('🔵 Edit label clicked');
        const btn = event.currentTarget;
        const labelId = btn.dataset.labelId;
        const labelName = btn.dataset.labelName;
        const labelDescription = btn.dataset.labelDescription;
        const labelColor = btn.dataset.labelColor;
        const labelCategories = btn.dataset.labelCategories;

        // Populate edit form
        document.getElementById('edit-label-id').value = labelId;
        document.getElementById('edit-label-name').value = labelName;
        document.getElementById('edit-label-description').value = labelDescription;
        document.getElementById('edit-label-color').value = labelColor;
        document.getElementById('edit-label-categories').value = labelCategories;

        // Update labels
        M.updateTextFields();

        // Check usage and show warning if needed
        checkLabelUsage(labelId);
    }

    function handleViewCellsClick(event) {
        console.log('🔵 View cells clicked');
        const btn = event.currentTarget;
        const labelId = btn.dataset.labelId;
        const labelName = btn.dataset.labelName;
        
        handleViewCellValues(labelId, labelName);
    }

    async function checkLabelUsage(labelId) {
        try {
            const response = await fetch(`/api/projects/${projectId}/labels/${labelId}/usage`, {
                credentials: 'same-origin'
            });
            if (response.ok) {
                const data = await response.json();
                const usageCount = data.usage_count || 0;
                
                const warningDiv = document.getElementById('edit-usage-warning');
                const usageCountSpan = document.getElementById('usage-count');
                
                if (usageCount > 0) {
                    usageCountSpan.textContent = usageCount;
                    warningDiv.style.display = 'block';
                } else {
                    warningDiv.style.display = 'none';
                }
            }
        } catch (error) {
            console.error('Error checking label usage:', error);
        }
    }

    async function handleEditLabel() {
        const labelId = document.getElementById('edit-label-id').value;
        const name = document.getElementById('edit-label-name').value.trim();
        const description = document.getElementById('edit-label-description').value.trim();
        const color = document.getElementById('edit-label-color').value;
        const categoriesText = document.getElementById('edit-label-categories').value.trim();
        const categories = categoriesText ? categoriesText.split(',').map(c => c.trim()).filter(c => c) : [];

        if (!name || !description) {
            M.toast({html: 'Nome e descrizione sono obbligatori', classes: 'red'});
            return;
        }

        try {
            const response = await fetch(`/api/projects/${projectId}/labels/${labelId}`, {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json',
                    'X-Requested-With': 'XMLHttpRequest'
                },
                credentials: 'same-origin',
                body: JSON.stringify({
                    name: name,
                    description: description,
                    color: color,
                    categories: categories
                })
            });

            const data = await response.json();

            if (response.ok && (data.success || data.message)) {
                M.toast({html: data.message || 'Etichetta aggiornata con successo!', classes: 'green'});
                
                // Close modal
                const modal = M.Modal.getInstance(document.getElementById('edit-label-modal'));
                modal.close();
                
                // Reload page to show updates
                setTimeout(() => window.location.reload(), 1000);
            } else {
                M.toast({html: data.error || 'Errore nell\'aggiornamento', classes: 'red'});
            }
        } catch (error) {
            console.error('Error updating label:', error);
            M.toast({html: 'Errore di connessione', classes: 'red'});
        }
    }

    function handleDeleteLabelClick(event) {
        console.log('🔵 Delete label clicked');
        const btn = event.currentTarget;
        const labelId = btn.dataset.labelId;
        const labelName = btn.dataset.labelName;

        document.getElementById('delete-label-id').value = labelId;
        document.getElementById('delete-label-name').textContent = labelName;
    }

    async function handleDeleteLabel() {
        const labelId = document.getElementById('delete-label-id').value;

        try {
            const response = await fetch(`/api/projects/${projectId}/labels/${labelId}`, {
                method: 'DELETE',
                credentials: 'same-origin',
                headers: {
                    'X-Requested-With': 'XMLHttpRequest'
                }
            });

            const data = await response.json();

            if (data.success) {
                M.toast({html: 'Etichetta eliminata con successo!', classes: 'green'});
                
                // Close modal
                const modal = M.Modal.getInstance(document.getElementById('delete-label-modal'));
                modal.close();
                
                // Remove row from table
                const row = document.querySelector(`tr[data-label-id="${labelId}"]`);
                if (row) {
                    row.remove();
                }
                
                // Update statistics
                setTimeout(() => window.location.reload(), 1000);
            } else {
                M.toast({html: data.error || 'Errore nell\'eliminazione', classes: 'red'});
            }
        } catch (error) {
            console.error('Error deleting label:', error);
            M.toast({html: 'Errore di connessione', classes: 'red'});
        }
    }

    async function loadAISuggestions() {
        try {
            const response = await fetch(`/api/projects/${projectId}/suggestions?type=store_label&status=pending`, {
                credentials: 'same-origin'
            });
            if (response.ok) {
                const data = await response.json();
                const suggestions = data.suggestions || [];
                
                if (suggestions.length > 0) {
                    displayAISuggestions(suggestions);
                    document.getElementById('ai-suggestions-section').style.display = 'block';
                }
            }
        } catch (error) {
            console.error('Error loading AI suggestions:', error);
        }
    }

    function displayAISuggestions(suggestions) {
        const container = document.getElementById('ai-suggestions-list');
        const countElement = document.getElementById('pending-suggestions-count');
        
        countElement.textContent = `${suggestions.length} in attesa`;
        
        container.innerHTML = suggestions.map(suggestion => `
            <div class="card-panel grey lighten-4" data-suggestion-id="${suggestion.id}">
                <div class="row valign-wrapper" style="margin-bottom: 0;">
                    <div class="col s12 m8">
                        <h6><strong>${suggestion.suggested_name}</strong></h6>
                        <p>${suggestion.suggested_description}</p>
                        <small class="grey-text">
                            Confidenza AI: ${Math.round((suggestion.ai_confidence || 0) * 100)}%
                        </small>
                    </div>
                    <div class="col s12 m4 right-align">
                        <a href="#!" class="btn-small green approve-suggestion" data-suggestion-id="${suggestion.id}">
                            <i class="material-icons left">check</i>Approva
                        </a>
                        <a href="#!" class="btn-small red reject-suggestion" data-suggestion-id="${suggestion.id}">
                            <i class="material-icons left">close</i>Rifiuta
                        </a>
                    </div>
                </div>
            </div>
        `).join('');

        // Add event listeners for individual suggestions
        container.querySelectorAll('.approve-suggestion').forEach(btn => {
            btn.addEventListener('click', (e) => handleApproveSuggestion(e.currentTarget.dataset.suggestionId));
        });
        
        container.querySelectorAll('.reject-suggestion').forEach(btn => {
            btn.addEventListener('click', (e) => handleRejectSuggestion(e.currentTarget.dataset.suggestionId));
        });
    }

    async function handleApproveSuggestion(suggestionId) {
        try {
            const response = await fetch(`/api/projects/${projectId}/suggestions/${suggestionId}/approve`, {
                method: 'PUT',
                credentials: 'same-origin',
                headers: {
                    'X-Requested-With': 'XMLHttpRequest'
                }
            });

            const data = await response.json();

            if (data.success) {
                M.toast({html: 'Suggerimento approvato!', classes: 'green'});
                
                // Remove suggestion from UI
                const suggestionElement = document.querySelector(`[data-suggestion-id="${suggestionId}"]`);
                if (suggestionElement) {
                    suggestionElement.remove();
                }
                
                // Reload page to show new label
                setTimeout(() => window.location.reload(), 1500);
            } else {
                M.toast({html: data.error || 'Errore nell\'approvazione', classes: 'red'});
            }
        } catch (error) {
            console.error('Error approving suggestion:', error);
            M.toast({html: 'Errore di connessione', classes: 'red'});
        }
    }

    async function handleRejectSuggestion(suggestionId) {
        try {
            const response = await fetch(`/api/projects/${projectId}/suggestions/${suggestionId}/reject`, {
                method: 'PUT',
                credentials: 'same-origin',
                headers: {
                    'X-Requested-With': 'XMLHttpRequest'
                }
            });

            const data = await response.json();

            if (data.success) {
                M.toast({html: 'Suggerimento rifiutato', classes: 'orange'});
                
                // Remove suggestion from UI
                const suggestionElement = document.querySelector(`[data-suggestion-id="${suggestionId}"]`);
                if (suggestionElement) {
                    suggestionElement.remove();
                }
                
                // Update count
                const remainingSuggestions = document.querySelectorAll('[data-suggestion-id]').length - 1;
                if (remainingSuggestions === 0) {
                    document.getElementById('ai-suggestions-section').style.display = 'none';
                }
            } else {
                M.toast({html: data.error || 'Errore nel rifiuto', classes: 'red'});
            }
        } catch (error) {
            console.error('Error rejecting suggestion:', error);
            M.toast({html: 'Errore di connessione', classes: 'red'});
        }
    }

    async function handleApproveAllSuggestions() {
        const suggestions = document.querySelectorAll('[data-suggestion-id]');
        const suggestionIds = Array.from(suggestions).map(el => el.dataset.suggestionId);
        
        if (suggestionIds.length === 0) return;

        M.toast({html: `Approvando ${suggestionIds.length} suggerimenti...`, classes: 'blue'});

        for (const suggestionId of suggestionIds) {
            await handleApproveSuggestion(suggestionId);
            // Small delay to avoid overwhelming the server
            await new Promise(resolve => setTimeout(resolve, 200));
        }
    }

    async function handleRejectAllSuggestions() {
        const suggestions = document.querySelectorAll('[data-suggestion-id]');
        const suggestionIds = Array.from(suggestions).map(el => el.dataset.suggestionId);
        
        if (suggestionIds.length === 0) return;

        M.toast({html: `Rifiutando ${suggestionIds.length} suggerimenti...`, classes: 'orange'});

        for (const suggestionId of suggestionIds) {
            await handleRejectSuggestion(suggestionId);
            // Small delay to avoid overwhelming the server
            await new Promise(resolve => setTimeout(resolve, 100));
        }
    }

    async function handleViewCellValues(labelId, labelName, page = 1) {
        try {
            const response = await fetch(`/api/projects/${projectId}/labels/${labelId}/cell-values?page=${page}`, {
                headers: {
                    'X-Requested-With': 'XMLHttpRequest'
                },
                credentials: 'same-origin'
            });

            const data = await response.json();

            if (response.ok && data.success) {
                showCellValuesModal(data.label, data.cell_values, data.pagination);
            } else {
                M.toast({html: data.error || 'Errore nel caricamento valori', classes: 'red'});
            }
        } catch (error) {
            console.error('Error loading cell values:', error);
            M.toast({html: 'Errore di connessione', classes: 'red'});
        }
    }

    function showCellValuesModal(label, cellValues, pagination) {
        // Update modal content
        document.getElementById('cell-values-label-name').textContent = label.name;
        document.getElementById('cell-values-count').textContent = `${pagination.total} valori`;
        
        const valuesContainer = document.getElementById('cell-values-list');
        valuesContainer.innerHTML = '';
        
        if (cellValues.length === 0) {
            document.getElementById('cell-values-empty').style.display = 'block';
            document.getElementById('cell-values-pagination').style.display = 'none';
        } else {
            document.getElementById('cell-values-empty').style.display = 'none';
            
            // Create table for values
            const table = document.createElement('table');
            table.className = 'striped responsive-table';
            table.innerHTML = `
                <thead>
                    <tr>
                        <th>Valore</th>
                        <th>File</th>
                        <th>Foglio</th>
                        <th>Colonna</th>
                        <th>Riga</th>
                        <th>Tipo</th>
                    </tr>
                </thead>
                <tbody></tbody>
            `;
            
            const tbody = table.querySelector('tbody');
            cellValues.forEach((value, index) => {
                const row = document.createElement('tr');
                row.innerHTML = `
                    <td><strong>${escapeHtml(value.cell_value)}</strong></td>
                    <td>${escapeHtml(value.file_name)}</td>
                    <td>${escapeHtml(value.sheet_name)}</td>
                    <td>${escapeHtml(value.column_name)}</td>
                    <td>${value.row_number}</td>
                    <td><span class="chip ${value.source_type === 'manual' ? 'blue' : 'green'}">${value.source_type}</span></td>
                `;
                tbody.appendChild(row);
            });
            
            valuesContainer.appendChild(table);
            
            // Handle pagination if needed
            if (pagination.pages > 1) {
                document.getElementById('cell-values-pagination').style.display = 'block';
                createPagination(pagination);
            } else {
                document.getElementById('cell-values-pagination').style.display = 'none';
            }
        }
        
        // Show modal
        const modal = M.Modal.getInstance(document.getElementById('view-cells-modal'));
        modal.open();
    }

    function createPagination(pagination) {
        const paginationList = document.getElementById('cell-values-pagination-list');
        paginationList.innerHTML = '';
        
        // Previous button
        if (pagination.has_prev) {
            const prevLi = document.createElement('li');
            prevLi.className = 'waves-effect';
            prevLi.innerHTML = `<a href="#" data-page="${pagination.prev_num}"><i class="material-icons">chevron_left</i></a>`;
            paginationList.appendChild(prevLi);
        }
        
        // Page numbers
        for (let i = Math.max(1, pagination.page - 2); i <= Math.min(pagination.pages, pagination.page + 2); i++) {
            const pageLi = document.createElement('li');
            if (i === pagination.page) {
                pageLi.className = 'active teal';
                pageLi.innerHTML = `<a href="#!">${i}</a>`;
            } else {
                pageLi.className = 'waves-effect';
                pageLi.innerHTML = `<a href="#" data-page="${i}">${i}</a>`;
            }
            paginationList.appendChild(pageLi);
        }
        
        // Next button
        if (pagination.has_next) {
            const nextLi = document.createElement('li');
            nextLi.className = 'waves-effect';
            nextLi.innerHTML = `<a href="#" data-page="${pagination.next_num}"><i class="material-icons">chevron_right</i></a>`;
            paginationList.appendChild(nextLi);
        }
        
        // Add event listeners for pagination
        paginationList.querySelectorAll('a[data-page]').forEach(link => {
            link.addEventListener('click', function(e) {
                e.preventDefault();
                const page = this.dataset.page;
                const labelId = document.querySelector('#view-cells-modal').dataset.labelId;
                const labelName = document.querySelector('#view-cells-modal').dataset.labelName;
                handleViewCellValues(labelId, labelName, page);
            });
        });
    }

    function escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    // Add event listener for cell values buttons
    document.addEventListener('click', function(event) {
        if (event.target.classList.contains('view-cells-btn')) {
            const labelId = event.target.dataset.labelId;
            const labelName = event.target.dataset.labelName;
            handleViewCellValues(labelId, labelName);
        }
    });
    
    // Re-initialize event listeners for dynamically loaded content
    function reinitializeEventListeners() {
        console.log('🔵 Re-initializing event listeners...');
        initializeEventListeners();
    }
    
    // Delegate events for dynamic content
    function setupEventDelegation() {
        console.log('🔵 Setting up event delegation...');
        
        // Use event delegation for buttons that might be added dynamically
        document.addEventListener('click', function(event) {
            // Edit label button
            if (event.target.closest('.edit-label-btn')) {
                console.log('🔵 Edit button clicked via delegation');
                handleEditLabelClick(event);
                return;
            }
            
            // View cells button  
            if (event.target.closest('.view-cells-btn')) {
                console.log('🔵 View cells button clicked via delegation');
                handleViewCellsClick(event);
                return;
            }
            
            // Delete label button
            if (event.target.closest('.delete-label-btn')) {
                console.log('🔵 Delete button clicked via delegation');
                handleDeleteLabelClick(event);
                return;
            }
        });
        
        console.log('✅ Event delegation setup complete');
    }

});  // Close DOMContentLoaded event listener

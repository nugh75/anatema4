/**
 * Label Store Management - Task 2.4
 * JavaScript per gestione store etichette centralizzato
 */

document.addEventListener('DOMContentLoaded', function() {
    // Initialize Materialize components
    M.Modal.init(document.querySelectorAll('.modal'));
    M.FormSelect.init(document.querySelectorAll('select'));
    M.updateTextFields();

    // Get project ID from URL
    const projectId = window.location.pathname.split('/')[2];

    // Initialize event listeners
    initializeEventListeners();
    loadAISuggestions();
    setupFiltersAndSearch();

    function initializeEventListeners() {
        // Create label
        document.getElementById('save-new-label')?.addEventListener('click', handleCreateLabel);
        
        // Edit label
        document.querySelectorAll('.edit-label-btn').forEach(btn => {
            btn.addEventListener('click', handleEditLabelClick);
        });
        document.getElementById('save-edit-label')?.addEventListener('click', handleEditLabel);
        
        // Delete label
        document.querySelectorAll('.delete-label-btn').forEach(btn => {
            btn.addEventListener('click', handleDeleteLabelClick);
        });
        document.getElementById('confirm-delete-label')?.addEventListener('click', handleDeleteLabel);
        
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
        const name = document.getElementById('create-label-name').value.trim();
        const description = document.getElementById('create-label-description').value.trim();
        const color = document.getElementById('create-label-color').value;
        const categoriesText = document.getElementById('create-label-categories').value.trim();
        const categories = categoriesText ? categoriesText.split(',').map(c => c.trim()).filter(c => c) : [];

        if (!name || !description) {
            M.toast({html: 'Nome e descrizione sono obbligatori', classes: 'red'});
            return;
        }

        try {
            const response = await fetch(`/api/projects/${projectId}/labels`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    name: name,
                    description: description,
                    color: color,
                    categories: categories
                })
            });

            const data = await response.json();

            if (data.success) {
                M.toast({html: 'Etichetta creata con successo!', classes: 'green'});
                
                // Reset form
                document.getElementById('create-label-form').reset();
                
                // Close modal
                const modal = M.Modal.getInstance(document.getElementById('create-label-modal'));
                modal.close();
                
                // Reload page to show new label
                setTimeout(() => window.location.reload(), 1000);
            } else {
                M.toast({html: data.error || 'Errore nella creazione', classes: 'red'});
            }
        } catch (error) {
            console.error('Error creating label:', error);
            M.toast({html: 'Errore di connessione', classes: 'red'});
        }
    }

    function handleEditLabelClick(event) {
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

    async function checkLabelUsage(labelId) {
        try {
            const response = await fetch(`/api/projects/${projectId}/labels/${labelId}/usage`);
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
                },
                body: JSON.stringify({
                    name: name,
                    description: description,
                    color: color,
                    categories: categories
                })
            });

            const data = await response.json();

            if (data.success) {
                M.toast({html: 'Etichetta aggiornata con successo!', classes: 'green'});
                
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
                method: 'DELETE'
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
            const response = await fetch(`/api/projects/${projectId}/suggestions?type=store_label&status=pending`);
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
                method: 'PUT'
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
                method: 'PUT'
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

    function handleSearch(event) {
        const searchTerm = event.target.value.toLowerCase();
        const rows = document.querySelectorAll('#labels-table-body tr');
        
        rows.forEach(row => {
            const labelName = row.querySelector('strong').textContent.toLowerCase();
            const labelDescription = row.querySelector('.label-description').textContent.toLowerCase();
            
            if (labelName.includes(searchTerm) || labelDescription.includes(searchTerm)) {
                row.style.display = '';
            } else {
                row.style.display = 'none';
            }
        });
    }

    function handleSort(event) {
        const sortBy = event.target.value;
        const tbody = document.getElementById('labels-table-body');
        const rows = Array.from(tbody.querySelectorAll('tr'));
        
        rows.sort((a, b) => {
            let valueA, valueB;
            
            switch (sortBy) {
                case 'name':
                    valueA = a.querySelector('strong').textContent.toLowerCase();
                    valueB = b.querySelector('strong').textContent.toLowerCase();
                    return valueA.localeCompare(valueB);
                
                case 'usage':
                    valueA = parseInt(a.querySelector('.chip').textContent) || 0;
                    valueB = parseInt(b.querySelector('.chip').textContent) || 0;
                    return valueB - valueA; // Descending
                
                case 'date':
                    valueA = a.querySelector('small').textContent;
                    valueB = b.querySelector('small').textContent;
                    return new Date(valueB) - new Date(valueA); // Most recent first
                
                default:
                    return 0;
            }
        });
        
        // Reappend sorted rows
        rows.forEach(row => tbody.appendChild(row));
    }

    function handleCategoryFilter(event) {
        const filterCategory = event.target.value.toLowerCase();
        const rows = document.querySelectorAll('#labels-table-body tr');
        
        rows.forEach(row => {
            if (!filterCategory) {
                row.style.display = '';
                return;
            }
            
            const categoryChips = row.querySelectorAll('.chip');
            const hasCategory = Array.from(categoryChips).some(chip => 
                chip.textContent.toLowerCase().includes(filterCategory)
            );
            
            row.style.display = hasCategory ? '' : 'none';
        });
    }

    function debounce(func, wait) {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    }
});

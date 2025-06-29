/**
 * Sistema Etichettatura Unificato - Task 2.3
 * Gestisce l'interfaccia di etichettatura integrata nelle view advanced
 */

class UnifiedLabelingSystem {
    constructor(projectId, sheetId) {
        this.projectId = projectId;
        this.sheetId = sheetId;
        this.selectedCells = new Set();
        this.currentColumn = null;
        this.projectLabels = [];
        this.selectedLabel = null;
        
        this.initializeSystem();
    }
    
    async initializeSystem() {
        try {
            // Carica etichette del progetto
            await this.loadProjectLabels();
            
            // Inizializza eventi
            this.initializeEvents();
            
            // Aggiorna UI
            this.updateUI();
            
            console.log('Sistema etichettatura unificato inizializzato');
        } catch (error) {
            console.error('Errore inizializzazione sistema etichettatura:', error);
            this.showError('Errore nel caricamento del sistema etichettatura');
        }
    }
    
    async loadProjectLabels() {
        try {
            const response = await fetch(`/api/projects/${this.projectId}/labels`, {
                method: 'GET',
                headers: {
                    'Content-Type': 'application/json'
                }
            });
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            const data = await response.json();
            this.projectLabels = data.labels || [];
            
            // Popola dropdown etichette
            this.populateLabelSelector();
            
            // Aggiorna statistiche
            this.updateStatistics(data.statistics);
            
        } catch (error) {
            console.error('Errore caricamento etichette progetto:', error);
            throw error;
        }
    }
    
    populateLabelSelector() {
        const selector = document.getElementById('label-selector');
        selector.innerHTML = '<option value="" disabled selected>Seleziona un\'etichetta</option>';
        
        this.projectLabels.forEach(label => {
            const option = document.createElement('option');
            option.value = label.id;
            option.textContent = label.name;
            option.dataset.description = label.description;
            option.dataset.color = label.color;
            selector.appendChild(option);
        });
        
        // Riabilita selector se ci sono etichette
        if (this.projectLabels.length > 0) {
            selector.disabled = false;
            $('#label-selector').formSelect();
        }
    }
    
    initializeEvents() {
        // Selezione etichetta
        $('#label-selector').on('change', (e) => {
            const labelId = e.target.value;
            this.selectedLabel = this.projectLabels.find(l => l.id == labelId);
            this.showLabelPreview();
            this.updateActionButtons();
        });
        
        // Applicazione manuale
        $('#apply-manual-label').on('click', (e) => {
            e.preventDefault();
            this.applyManualLabel();
        });
        
        // Richiesta suggerimenti AI
        $('#request-ai-label').on('click', (e) => {
            e.preventDefault();
            this.requestAISuggestions();
        });
        
        // Creazione nuova etichetta
        $('#create-new-label').on('click', (e) => {
            e.preventDefault();
            this.openCreateLabelModal();
        });
        
        // Salvataggio nuova etichetta
        $('#save-label-btn').on('click', (e) => {
            e.preventDefault();
            this.saveNewLabel();
        });
        
        // Preview in tempo reale della nuova etichetta
        $('#label-name, #label-description, #label-color').on('input', () => {
            this.updateLabelPreview();
        });
        
        // Gestione suggerimenti AI
        $(document).on('click', '.approve-suggestion', (e) => {
            e.preventDefault();
            const suggestionId = $(e.target).closest('.suggestion-item').data('suggestion-id');
            this.approveSuggestion(suggestionId);
        });
        
        $(document).on('click', '.reject-suggestion', (e) => {
            e.preventDefault();
            const suggestionId = $(e.target).closest('.suggestion-item').data('suggestion-id');
            this.rejectSuggestion(suggestionId);
        });
        
        $('#approve-all-suggestions').on('click', (e) => {
            e.preventDefault();
            this.approveAllSuggestions();
        });
    }
    
    // Metodi di selezione celle (da integrare con view esistenti)
    addCellToSelection(rowIndex, columnName, cellValue) {
        const cellKey = `${rowIndex}_${columnName}`;
        this.selectedCells.add({
            key: cellKey,
            row_index: rowIndex,
            column_name: columnName,
            cell_value: cellValue
        });
        
        this.updateSelectionInfo();
        this.updateActionButtons();
    }
    
    removeCellFromSelection(rowIndex, columnName) {
        const cellKey = `${rowIndex}_${columnName}`;
        this.selectedCells.forEach(cell => {
            if (cell.key === cellKey) {
                this.selectedCells.delete(cell);
            }
        });
        
        this.updateSelectionInfo();
        this.updateActionButtons();
    }
    
    clearSelection() {
        this.selectedCells.clear();
        this.updateSelectionInfo();
        this.updateActionButtons();
    }
    
    setCurrentColumn(columnName) {
        this.currentColumn = columnName;
        document.getElementById('current-column-name').textContent = columnName || '-';
    }
    
    updateSelectionInfo() {
        const count = this.selectedCells.size;
        document.getElementById('selected-cells-count').textContent = count;
        
        // Aggiorna badge con colore
        const badge = document.getElementById('selected-cells-count');
        badge.className = count > 0 ? 'badge green white-text' : 'badge';
    }
    
    updateActionButtons() {
        const hasSelection = this.selectedCells.size > 0;
        const hasLabel = this.selectedLabel !== null;
        
        document.getElementById('apply-manual-label').disabled = !(hasSelection && hasLabel);
        document.getElementById('request-ai-label').disabled = !hasSelection;
    }
    
    showLabelPreview() {
        const preview = document.getElementById('label-preview');
        if (this.selectedLabel) {
            preview.style.display = 'block';
            preview.querySelector('.label-name').textContent = this.selectedLabel.name;
            preview.querySelector('.label-description').textContent = this.selectedLabel.description;
            preview.style.borderLeft = `4px solid ${this.selectedLabel.color}`;
        } else {
            preview.style.display = 'none';
        }
    }
    
    async applyManualLabel() {
        if (!this.selectedLabel || this.selectedCells.size === 0) {
            this.showError('Seleziona celle ed etichetta prima di applicare');
            return;
        }
        
        try {
            const cellsArray = Array.from(this.selectedCells);
            
            const response = await fetch(`/api/projects/${this.projectId}/labels/apply-manual`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    label_id: this.selectedLabel.id,
                    sheet_id: this.sheetId,
                    cells: cellsArray.map(cell => ({
                        row_index: cell.row_index,
                        column_name: cell.column_name,
                        cell_value: cell.cell_value
                    }))
                })
            });
            
            if (!response.ok) {
                const error = await response.json();
                throw new Error(error.error || 'Errore applicazione etichetta');
            }
            
            const result = await response.json();
            this.showSuccess(`Etichetta applicata a ${result.applied_count} celle`);
            
            // Aggiorna UI
            this.clearSelection();
            await this.loadProjectLabels();
            
            // Notifica parent per aggiornamento view
            if (window.labelingSystemCallback) {
                window.labelingSystemCallback('manual_label_applied', result);
            }
            
        } catch (error) {
            console.error('Errore applicazione etichetta manuale:', error);
            this.showError(error.message);
        }
    }
    
    async requestAISuggestions() {
        if (this.selectedCells.size === 0) {
            this.showError('Seleziona almeno una cella per i suggerimenti AI');
            return;
        }
        
        try {
            // Mostra modal e loading
            $('#ai-suggestions-modal').modal('open');
            document.getElementById('ai-loading').style.display = 'block';
            document.getElementById('ai-suggestions-content').style.display = 'none';
            document.getElementById('ai-error').style.display = 'none';
            
            const cellsArray = Array.from(this.selectedCells);
            
            const response = await fetch(`/api/projects/${this.projectId}/labels/apply-ai`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    sheet_id: this.sheetId,
                    cells: cellsArray.map(cell => ({
                        row_index: cell.row_index,
                        column_name: cell.column_name,
                        cell_value: cell.cell_value
                    }))
                })
            });
            
            if (!response.ok) {
                const error = await response.json();
                throw new Error(error.error || 'Errore richiesta suggerimenti AI');
            }
            
            const result = await response.json();
            
            // Nasconde loading e mostra suggerimenti
            document.getElementById('ai-loading').style.display = 'none';
            this.displayAISuggestions(result.suggestions);
            
        } catch (error) {
            console.error('Errore richiesta suggerimenti AI:', error);
            document.getElementById('ai-loading').style.display = 'none';
            document.getElementById('ai-error').style.display = 'block';
            document.getElementById('ai-error').querySelector('span').textContent = error.message;
        }
    }
    
    displayAISuggestions(suggestions) {
        const container = document.getElementById('suggestions-list');
        const template = document.getElementById('ai-suggestion-template');
        
        container.innerHTML = '';
        
        if (!suggestions || suggestions.length === 0) {
            container.innerHTML = '<p class="center-align grey-text">Nessun suggerimento disponibile</p>';
            document.getElementById('ai-suggestions-content').style.display = 'block';
            return;
        }
        
        suggestions.forEach(suggestion => {
            const suggestionElement = template.content.cloneNode(true);
            
            suggestionElement.querySelector('.suggestion-item').dataset.suggestionId = suggestion.id;
            suggestionElement.querySelector('.suggestion-label-name').textContent = suggestion.suggested_name;
            suggestionElement.querySelector('.suggestion-description').textContent = suggestion.suggested_description;
            suggestionElement.querySelector('.suggestion-reasoning').textContent = suggestion.ai_reasoning;
            suggestionElement.querySelector('.confidence-value').textContent = 
                Math.round(suggestion.ai_confidence * 100) + '%';
            
            container.appendChild(suggestionElement);
        });
        
        document.getElementById('ai-suggestions-content').style.display = 'block';
        document.getElementById('approve-all-suggestions').style.display = 'inline-block';
    }
    
    async approveSuggestion(suggestionId) {
        try {
            const response = await fetch(`/api/projects/${this.projectId}/suggestions/${suggestionId}/approve`, {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json'
                }
            });
            
            if (!response.ok) {
                const error = await response.json();
                throw new Error(error.error || 'Errore approvazione suggerimento');
            }
            
            // Rimuovi suggerimento dalla lista
            $(`.suggestion-item[data-suggestion-id="${suggestionId}"]`).fadeOut();
            
            this.showSuccess('Suggerimento approvato');
            
            // Aggiorna dati
            await this.loadProjectLabels();
            
        } catch (error) {
            console.error('Errore approvazione suggerimento:', error);
            this.showError(error.message);
        }
    }
    
    async rejectSuggestion(suggestionId) {
        // Implementazione simile a approveSuggestion
        $(`.suggestion-item[data-suggestion-id="${suggestionId}"]`).fadeOut();
        this.showSuccess('Suggerimento rifiutato');
    }
    
    openCreateLabelModal() {
        // Reset form
        document.getElementById('create-label-form').reset();
        document.getElementById('label-color').value = '#1976d2';
        this.updateLabelPreview();
        
        $('#create-label-modal').modal('open');
    }
    
    updateLabelPreview() {
        const name = document.getElementById('label-name').value || 'Nuova Etichetta';
        const description = document.getElementById('label-description').value || 'Descrizione dell\'etichetta';
        const color = document.getElementById('label-color').value;
        
        document.getElementById('preview-color').textContent = name;
        document.getElementById('preview-color').style.backgroundColor = color;
        document.getElementById('preview-description').textContent = description;
    }
    
    async saveNewLabel() {
        const form = document.getElementById('create-label-form');
        if (!form.checkValidity()) {
            form.reportValidity();
            return;
        }
        
        try {
            const formData = {
                name: document.getElementById('label-name').value.trim(),
                description: document.getElementById('label-description').value.trim(),
                color: document.getElementById('label-color').value,
                categories: document.getElementById('label-categories').value
                    .split(',').map(c => c.trim()).filter(c => c)
            };
            
            const response = await fetch(`/api/projects/${this.projectId}/labels`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(formData)
            });
            
            if (!response.ok) {
                const error = await response.json();
                throw new Error(error.error || 'Errore creazione etichetta');
            }
            
            const result = await response.json();
            
            $('#create-label-modal').modal('close');
            this.showSuccess('Etichetta creata con successo');
            
            // Ricarica etichette
            await this.loadProjectLabels();
            
            // Seleziona automaticamente la nuova etichetta
            document.getElementById('label-selector').value = result.label.id;
            $('#label-selector').formSelect();
            this.selectedLabel = result.label;
            this.showLabelPreview();
            this.updateActionButtons();
            
        } catch (error) {
            console.error('Errore creazione etichetta:', error);
            this.showError(error.message);
        }
    }
    
    updateStatistics(stats) {
        if (!stats) return;
        
        document.getElementById('stats-total-labels').textContent = stats.total_labels || 0;
        // Altri stats verranno aggiornati dalle view parent
    }
    
    updateUI() {
        this.updateSelectionInfo();
        this.updateActionButtons();
        this.showLabelPreview();
    }
    
    showSuccess(message) {
        M.toast({html: `<i class="material-icons left">check</i>${message}`, classes: 'green'});
    }
    
    showError(message) {
        M.toast({html: `<i class="material-icons left">error</i>${message}`, classes: 'red'});
    }
    
    showInfo(message) {
        M.toast({html: `<i class="material-icons left">info</i>${message}`, classes: 'blue'});
    }
}

// Export per uso globale
window.UnifiedLabelingSystem = UnifiedLabelingSystem;

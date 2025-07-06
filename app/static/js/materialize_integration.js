/**
 * Soluzione corretta per Label Store - Lavora con Materialize CSS
 * Il problema era che stiamo sovrascrivendo i modal-trigger di Materialize
 */

document.addEventListener('DOMContentLoaded', function() {
    console.log('🔵 MATERIALIZE INTEGRATION: Label Store fix loading...');
    
    // Aspetta che Materialize sia completamente inizializzato
    setTimeout(() => {
        console.log('🔵 MATERIALIZE INTEGRATION: Initializing...');
        
        // Inizializza tutti i modal di Materialize
        const modalElems = document.querySelectorAll('.modal');
        const modalInstances = M.Modal.init(modalElems);
        
        // Configura event listeners per quando i modal si aprono
        modalInstances.forEach(instance => {
            instance.options.onOpenStart = function() {
                const modalId = this.el.id;
                console.log(`🔵 MATERIALIZE: Modal ${modalId} opening...`);
                
                // Trova il pulsante che ha attivato il modal
                const triggerBtn = document.querySelector(`[href="#${modalId}"]`);
                
                if (triggerBtn) {
                    handleModalOpen(modalId, triggerBtn);
                }
            };
        });
        
        // Configura event listeners per i pulsanti di azione nei modal
        setupModalActionButtons();
        
        console.log('🔵 MATERIALIZE INTEGRATION: Setup completed');
        
    }, 500);
});

function handleModalOpen(modalId, triggerBtn) {
    console.log(`🔵 HANDLING MODAL: ${modalId}`);
    
    const labelId = triggerBtn.dataset.labelId;
    const labelName = triggerBtn.dataset.labelName;
    const labelDescription = triggerBtn.dataset.labelDescription;
    const labelColor = triggerBtn.dataset.labelColor;
    const labelCategories = triggerBtn.dataset.labelCategories;
    
    console.log('🔵 MODAL DATA:', {
        modalId, labelId, labelName, labelDescription, labelColor, labelCategories
    });
    
    switch(modalId) {
        case 'edit-label-modal':
            populateEditModal(labelId, labelName, labelDescription, labelColor, labelCategories);
            break;
            
        case 'delete-label-modal':
            populateDeleteModal(labelId, labelName);
            break;
            
        case 'view-cells-modal':
            populateViewCellsModal(labelId, labelName);
            break;
    }
}

function populateEditModal(labelId, labelName, labelDescription, labelColor, labelCategories) {
    console.log('🔵 POPULATING EDIT MODAL:', {labelId, labelName, labelDescription, labelColor, labelCategories});
    
    // Popola i campi
    document.getElementById('edit-label-id').value = labelId || '';
    document.getElementById('edit-label-name').value = labelName || '';
    document.getElementById('edit-label-description').value = labelDescription || '';
    document.getElementById('edit-label-color').value = labelColor || '#2196F3';
    document.getElementById('edit-label-categories').value = labelCategories || '';
    
    // Aggiorna i campi Materialize
    M.updateTextFields();
    
    // Carica informazioni sull'uso dell'etichetta
    if (labelId) {
        checkLabelUsage(labelId);
    }
}

function populateDeleteModal(labelId, labelName) {
    console.log('🔵 POPULATING DELETE MODAL:', {labelId, labelName});
    
    document.getElementById('delete-label-id').value = labelId || '';
    document.getElementById('delete-label-name').textContent = labelName || 'Etichetta';
}

function populateViewCellsModal(labelId, labelName) {
    console.log('🔵 POPULATING VIEW CELLS MODAL:', {labelId, labelName});
    
    document.getElementById('cell-values-label-name').textContent = labelName || 'Etichetta';
    document.getElementById('cell-values-loading').style.display = 'block';
    document.getElementById('cell-values-list').innerHTML = '';
    
    // Carica i valori delle celle
    if (labelId) {
        loadCellValues(labelId);
    }
}

function setupModalActionButtons() {
    console.log('🔵 SETTING UP MODAL ACTION BUTTONS...');
    
    // Pulsante salva modifica
    const saveEditBtn = document.getElementById('save-edit-label');
    if (saveEditBtn) {
        saveEditBtn.addEventListener('click', function(e) {
            e.preventDefault();
            console.log('🔵 SAVE EDIT CLICKED');
            
            const labelId = document.getElementById('edit-label-id').value;
            const labelName = document.getElementById('edit-label-name').value;
            const labelDescription = document.getElementById('edit-label-description').value;
            const labelColor = document.getElementById('edit-label-color').value;
            const labelCategories = document.getElementById('edit-label-categories').value;
            
            if (labelId && labelName && labelDescription) {
                saveEditLabel(labelId, labelName, labelDescription, labelColor, labelCategories);
            } else {
                M.toast({html: 'Per favore compila tutti i campi richiesti', classes: 'red'});
            }
        });
    }
    
    // Pulsante conferma eliminazione
    const confirmDeleteBtn = document.getElementById('confirm-delete-label');
    if (confirmDeleteBtn) {
        confirmDeleteBtn.addEventListener('click', function(e) {
            e.preventDefault();
            console.log('🔵 CONFIRM DELETE CLICKED');
            
            const labelId = document.getElementById('delete-label-id').value;
            if (labelId) {
                deleteLabel(labelId);
            }
        });
    }
}

// Funzione sicura per le chiamate fetch che evita problemi CORS
function safeFetch(url, options = {}) {
    const defaultOptions = {
        method: 'GET',
        mode: 'cors',
        credentials: 'same-origin',
        headers: {
            'Content-Type': 'application/json',
            'X-Requested-With': 'XMLHttpRequest'
        },
        ...options
    };
    
    console.log('🔧 Safe fetch:', url, defaultOptions);
    
    return fetch(url, defaultOptions)
        .then(response => {
            console.log('🔧 Safe fetch response:', response.status, response.type);
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return response;
        })
        .catch(error => {
            console.error('🔧 Safe fetch error:', error);
            throw error;
        });
}

function checkLabelUsage(labelId) {
    console.log(`🔵 CHECKING USAGE for label ${labelId}`);
    
    const projectId = getProjectId();
    
    safeFetch(`/api/projects/${projectId}/labels/${labelId}/usage`)
    .then(response => {
        console.log(`🔵 USAGE RESPONSE: ${response.status}`);
        return response.json();
    })
    .then(data => {
        console.log('🔵 USAGE DATA:', data);
        
        const usageCount = data.usage_count || 0;
        const warningDiv = document.getElementById('edit-usage-warning');
        const countSpan = document.getElementById('usage-count');
        
        if (usageCount > 0 && warningDiv && countSpan) {
            countSpan.textContent = usageCount;
            warningDiv.style.display = 'block';
        } else if (warningDiv) {
            warningDiv.style.display = 'none';
        }
    })
    .catch(error => {
        console.error('🔵 USAGE ERROR:', error);
    });
}

function loadCellValues(labelId) {
    console.log(`🔵 LOADING CELL VALUES for label ${labelId}`);
    
    const projectId = getProjectId();
    
    safeFetch(`/api/projects/${projectId}/labels/${labelId}/cell-values`)
    .then(response => {
        console.log(`🔵 CELL VALUES RESPONSE: ${response.status}`);
        return response.json();
    })
    .then(data => {
        console.log('🔵 CELL VALUES DATA:', data);
        
        document.getElementById('cell-values-loading').style.display = 'none';
        
        if (data.success && data.cell_values) {
            displayCellValues(data.cell_values);
            document.getElementById('cell-values-count').textContent = `${data.cell_values.length} valori`;
        } else {
            document.getElementById('cell-values-list').innerHTML = '<p class="center-align">Nessun valore trovato</p>';
        }
    })
    .catch(error => {
        console.error('🔵 CELL VALUES ERROR:', error);
        document.getElementById('cell-values-loading').style.display = 'none';
        document.getElementById('cell-values-list').innerHTML = '<p class="center-align red-text">Errore nel caricamento</p>';
    });
}

function displayCellValues(cellValues) {
    console.log(`🔵 DISPLAYING ${cellValues.length} CELL VALUES`);
    
    const container = document.getElementById('cell-values-list');
    
    if (cellValues.length === 0) {
        container.innerHTML = '<p class="center-align">Nessun valore trovato</p>';
        return;
    }
    
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
        <tbody>
            ${cellValues.map(value => `
                <tr>
                    <td><strong>${escapeHtml(value.value || 'N/A')}</strong></td>
                    <td>${escapeHtml(value.file_name || 'N/A')}</td>
                    <td>${escapeHtml(value.sheet_name || 'N/A')}</td>
                    <td>${escapeHtml(value.column_name || 'N/A')}</td>
                    <td>${value.row_number || 'N/A'}</td>
                    <td><span class="chip ${value.label_type === 'manual' ? 'blue' : 'green'}">${value.label_type || 'N/A'}</span></td>
                </tr>
            `).join('')}
        </tbody>
    `;
    
    container.appendChild(table);
}

function saveEditLabel(labelId, labelName, labelDescription, labelColor, labelCategories) {
    console.log('🔵 SAVING EDIT LABEL:', {labelId, labelName, labelDescription, labelColor, labelCategories});
    
    const projectId = getProjectId();
    
    const data = {
        name: labelName,
        description: labelDescription,
        color: labelColor,
        categories: labelCategories.split(',').map(cat => cat.trim()).filter(cat => cat)
    };
    
    safeFetch(`/api/projects/${projectId}/labels/${labelId}`, {
        method: 'PUT',
        body: JSON.stringify(data)
    })
    .then(response => {
        console.log(`🔵 SAVE RESPONSE: ${response.status}`);
        return response.json();
    })
    .then(data => {
        console.log('🔵 SAVE DATA:', data);
        
        if (data.success) {
            M.toast({html: 'Etichetta aggiornata con successo', classes: 'green'});
            
            // Chiudi il modal
            const modal = M.Modal.getInstance(document.getElementById('edit-label-modal'));
            if (modal) {
                modal.close();
            }
            
            // Ricarica la pagina
            setTimeout(() => {
                location.reload();
            }, 1000);
        } else {
            M.toast({html: data.error || 'Errore nell\'aggiornamento', classes: 'red'});
        }
    })
    .catch(error => {
        console.error('🔵 SAVE ERROR:', error);
        M.toast({html: 'Errore di connessione', classes: 'red'});
    });
}

function deleteLabel(labelId) {
    console.log('🔵 DELETING LABEL:', labelId);
    
    const projectId = getProjectId();
    
    safeFetch(`/api/projects/${projectId}/labels/${labelId}`, {
        method: 'DELETE'
    })
    .then(response => {
        console.log(`🔵 DELETE RESPONSE: ${response.status}`);
        return response.json();
    })
    .then(data => {
        console.log('🔵 DELETE DATA:', data);
        
        if (data.success) {
            M.toast({html: 'Etichetta eliminata con successo', classes: 'green'});
            
            // Chiudi il modal
            const modal = M.Modal.getInstance(document.getElementById('delete-label-modal'));
            if (modal) {
                modal.close();
            }
            
            // Ricarica la pagina
            setTimeout(() => {
                location.reload();
            }, 1000);
        } else {
            M.toast({html: data.error || 'Errore nell\'eliminazione', classes: 'red'});
        }
    })
    .catch(error => {
        console.error('🔵 DELETE ERROR:', error);
        M.toast({html: 'Errore di connessione', classes: 'red'});
    });
}

// Funzioni helper
function getProjectId() {
    return window.location.pathname.split('/')[2];
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

console.log('🔵 MATERIALIZE INTEGRATION: Script loaded');

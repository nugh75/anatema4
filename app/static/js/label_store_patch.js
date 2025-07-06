/**
 * Patch per correggere i problemi dei pulsanti Label Store
 * Questo script corregge i problemi di event listeners e modal
 */

// Esegui dopo che il DOM è completamente caricato
document.addEventListener('DOMContentLoaded', function() {
    console.log("🔧 PATCH: Applying Label Store button fixes...");
    
    // Aspetta che anche il JavaScript principale sia caricato
    setTimeout(function() {
        console.log("🔧 PATCH: Initializing button fixes...");
        
        // 1. Verifica se i pulsanti esistono
        const editButtons = document.querySelectorAll('.edit-label-btn');
        const deleteButtons = document.querySelectorAll('.delete-label-btn');
        const viewCellsButtons = document.querySelectorAll('.view-cells-btn');
        
        console.log(`🔧 PATCH: Found buttons - Edit: ${editButtons.length}, Delete: ${deleteButtons.length}, ViewCells: ${viewCellsButtons.length}`);
        
        // 2. Aggiungi event listeners diretti se non esistono
        editButtons.forEach((btn, index) => {
            console.log(`🔧 PATCH: Processing edit button ${index + 1}`);
            
            // Rimuovi event listener esistenti per evitare duplicati
            const newBtn = btn.cloneNode(true);
            btn.parentNode.replaceChild(newBtn, btn);
            
            // Aggiungi nuovo event listener
            newBtn.addEventListener('click', function(e) {
                e.preventDefault();
                console.log(`🔧 PATCH: Edit button clicked for label ${newBtn.dataset.labelId}`);
                
                // Popola i campi del modal
                const labelId = newBtn.dataset.labelId;
                const labelName = newBtn.dataset.labelName;
                const labelDescription = newBtn.dataset.labelDescription || '';
                const labelColor = newBtn.dataset.labelColor || '#2196F3';
                const labelCategories = newBtn.dataset.labelCategories || '';
                
                console.log(`🔧 PATCH: Populating edit modal with:`, {
                    labelId, labelName, labelDescription, labelColor, labelCategories
                });
                
                // Popola i campi
                document.getElementById('edit-label-id').value = labelId;
                document.getElementById('edit-label-name').value = labelName;
                document.getElementById('edit-label-description').value = labelDescription;
                document.getElementById('edit-label-color').value = labelColor;
                document.getElementById('edit-label-categories').value = labelCategories;
                
                // Aggiorna i campi Materialize
                M.updateTextFields();
                
                // Apri il modal
                const modal = document.getElementById('edit-label-modal');
                if (modal) {
                    const modalInstance = M.Modal.getInstance(modal);
                    if (modalInstance) {
                        modalInstance.open();
                    } else {
                        console.log("🔧 PATCH: Modal instance not found, creating new one");
                        M.Modal.init(modal).open();
                    }
                }
            });
        });
        
        // 3. Fix delete buttons
        deleteButtons.forEach((btn, index) => {
            console.log(`🔧 PATCH: Processing delete button ${index + 1}`);
            
            // Rimuovi event listener esistenti per evitare duplicati
            const newBtn = btn.cloneNode(true);
            btn.parentNode.replaceChild(newBtn, btn);
            
            // Aggiungi nuovo event listener
            newBtn.addEventListener('click', function(e) {
                e.preventDefault();
                console.log(`🔧 PATCH: Delete button clicked for label ${newBtn.dataset.labelId}`);
                
                const labelId = newBtn.dataset.labelId;
                const labelName = newBtn.dataset.labelName;
                
                // Popola i campi del modal
                document.getElementById('delete-label-id').value = labelId;
                document.getElementById('delete-label-name').textContent = labelName;
                
                // Apri il modal
                const modal = document.getElementById('delete-label-modal');
                if (modal) {
                    const modalInstance = M.Modal.getInstance(modal);
                    if (modalInstance) {
                        modalInstance.open();
                    } else {
                        console.log("🔧 PATCH: Modal instance not found, creating new one");
                        M.Modal.init(modal).open();
                    }
                }
            });
        });
        
        // 4. Fix view cells buttons
        viewCellsButtons.forEach((btn, index) => {
            console.log(`🔧 PATCH: Processing view cells button ${index + 1}`);
            
            // Rimuovi event listener esistenti per evitare duplicati
            const newBtn = btn.cloneNode(true);
            btn.parentNode.replaceChild(newBtn, btn);
            
            // Aggiungi nuovo event listener
            newBtn.addEventListener('click', function(e) {
                e.preventDefault();
                console.log(`🔧 PATCH: View cells button clicked for label ${newBtn.dataset.labelId}`);
                
                const labelId = newBtn.dataset.labelId;
                const labelName = newBtn.dataset.labelName;
                
                // Popola il modal
                document.getElementById('cell-values-label-name').textContent = labelName;
                document.getElementById('cell-values-loading').style.display = 'block';
                document.getElementById('cell-values-list').innerHTML = '';
                
                // Apri il modal
                const modal = document.getElementById('view-cells-modal');
                if (modal) {
                    const modalInstance = M.Modal.getInstance(modal);
                    if (modalInstance) {
                        modalInstance.open();
                    } else {
                        console.log("🔧 PATCH: Modal instance not found, creating new one");
                        M.Modal.init(modal).open();
                    }
                }
                
                // Carica i dati
                loadCellValues(labelId);
            });
        });
        
        // 5. Fix confirm delete button
        const confirmDeleteBtn = document.getElementById('confirm-delete-label');
        if (confirmDeleteBtn) {
            console.log("🔧 PATCH: Processing confirm delete button");
            
            // Rimuovi event listener esistenti
            const newConfirmBtn = confirmDeleteBtn.cloneNode(true);
            confirmDeleteBtn.parentNode.replaceChild(newConfirmBtn, confirmDeleteBtn);
            
            newConfirmBtn.addEventListener('click', function(e) {
                e.preventDefault();
                console.log("🔧 PATCH: Confirm delete button clicked");
                
                const labelId = document.getElementById('delete-label-id').value;
                if (labelId) {
                    deleteLabel(labelId);
                }
            });
        }
        
        // 6. Fix save edit button
        const saveEditBtn = document.getElementById('save-edit-label');
        if (saveEditBtn) {
            console.log("🔧 PATCH: Processing save edit button");
            
            // Rimuovi event listener esistenti
            const newSaveBtn = saveEditBtn.cloneNode(true);
            saveEditBtn.parentNode.replaceChild(newSaveBtn, saveEditBtn);
            
            newSaveBtn.addEventListener('click', function(e) {
                e.preventDefault();
                console.log("🔧 PATCH: Save edit button clicked");
                
                const labelId = document.getElementById('edit-label-id').value;
                const labelName = document.getElementById('edit-label-name').value;
                const labelDescription = document.getElementById('edit-label-description').value;
                const labelColor = document.getElementById('edit-label-color').value;
                const labelCategories = document.getElementById('edit-label-categories').value;
                
                if (labelId && labelName && labelDescription) {
                    saveEditLabel(labelId, labelName, labelDescription, labelColor, labelCategories);
                }
            });
        }
        
        console.log("🔧 PATCH: All button fixes applied successfully");
        
    }, 1000); // Aspetta 1 secondo per essere sicuro che tutto sia caricato
});

// Funzioni helper
function loadCellValues(labelId) {
    console.log(`🔧 PATCH: Loading cell values for label ${labelId}`);
    
    const projectId = window.location.pathname.split('/')[2];
    
    fetch(`/api/projects/${projectId}/labels/${labelId}/cell-values`, {
        credentials: 'same-origin'
    })
    .then(response => {
        console.log(`🔧 PATCH: Cell values response: ${response.status}`);
        return response.json();
    })
    .then(data => {
        console.log(`🔧 PATCH: Cell values data:`, data);
        
        document.getElementById('cell-values-loading').style.display = 'none';
        
        if (data.success && data.cell_values) {
            displayCellValues(data.cell_values);
        } else {
            document.getElementById('cell-values-list').innerHTML = '<p class="center-align">Nessun valore trovato</p>';
        }
    })
    .catch(error => {
        console.error(`🔧 PATCH: Error loading cell values:`, error);
        document.getElementById('cell-values-loading').style.display = 'none';
        document.getElementById('cell-values-list').innerHTML = '<p class="center-align red-text">Errore nel caricamento</p>';
    });
}

function displayCellValues(cellValues) {
    console.log(`🔧 PATCH: Displaying ${cellValues.length} cell values`);
    
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
                    <td><strong>${value.value || 'N/A'}</strong></td>
                    <td>${value.file_name || 'N/A'}</td>
                    <td>${value.sheet_name || 'N/A'}</td>
                    <td>${value.column_name || 'N/A'}</td>
                    <td>${value.row_number || 'N/A'}</td>
                    <td><span class="chip ${value.label_type === 'manual' ? 'blue' : 'green'}">${value.label_type || 'N/A'}</span></td>
                </tr>
            `).join('')}
        </tbody>
    `;
    
    container.appendChild(table);
}

function saveEditLabel(labelId, labelName, labelDescription, labelColor, labelCategories) {
    console.log(`🔧 PATCH: Saving edit for label ${labelId}`);
    
    const projectId = window.location.pathname.split('/')[2];
    
    const data = {
        name: labelName,
        description: labelDescription,
        color: labelColor,
        categories: labelCategories.split(',').map(cat => cat.trim()).filter(cat => cat)
    };
    
    fetch(`/api/projects/${projectId}/labels/${labelId}`, {
        method: 'PUT',
        headers: {
            'Content-Type': 'application/json',
        },
        credentials: 'same-origin',
        body: JSON.stringify(data)
    })
    .then(response => {
        console.log(`🔧 PATCH: Edit response: ${response.status}`);
        return response.json();
    })
    .then(data => {
        console.log(`🔧 PATCH: Edit data:`, data);
        
        if (data.success) {
            M.toast({html: 'Etichetta aggiornata con successo', classes: 'green'});
            
            // Chiudi il modal
            const modal = document.getElementById('edit-label-modal');
            const modalInstance = M.Modal.getInstance(modal);
            if (modalInstance) {
                modalInstance.close();
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
        console.error(`🔧 PATCH: Error saving edit:`, error);
        M.toast({html: 'Errore di connessione', classes: 'red'});
    });
}

function deleteLabel(labelId) {
    console.log(`🔧 PATCH: Deleting label ${labelId}`);
    
    const projectId = window.location.pathname.split('/')[2];
    
    fetch(`/api/projects/${projectId}/labels/${labelId}`, {
        method: 'DELETE',
        credentials: 'same-origin'
    })
    .then(response => {
        console.log(`🔧 PATCH: Delete response: ${response.status}`);
        return response.json();
    })
    .then(data => {
        console.log(`🔧 PATCH: Delete data:`, data);
        
        if (data.success) {
            M.toast({html: 'Etichetta eliminata con successo', classes: 'green'});
            
            // Chiudi il modal
            const modal = document.getElementById('delete-label-modal');
            const modalInstance = M.Modal.getInstance(modal);
            if (modalInstance) {
                modalInstance.close();
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
        console.error(`🔧 PATCH: Error deleting:`, error);
        M.toast({html: 'Errore di connessione', classes: 'red'});
    });
}

console.log("🔧 PATCH: Label Store button fix script loaded");

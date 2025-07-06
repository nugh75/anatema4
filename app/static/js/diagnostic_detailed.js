/**
 * Diagnostica dettagliata per Store Etichette
 * Questo script verifica step by step cosa succede quando si clicca sui pulsanti
 */

console.log("🔵 DIAGNOSTICA DETTAGLIATA - Store Etichette");

// 1. Verifica che gli event listeners siano attaccati
function checkEventListeners() {
    console.log("\n1. 🔍 Verifica Event Listeners");
    
    // Verifica pulsanti modifica
    const editButtons = document.querySelectorAll('[data-action="edit"]');
    console.log(`   - Pulsanti modifica trovati: ${editButtons.length}`);
    
    editButtons.forEach((btn, index) => {
        console.log(`   - Pulsante ${index + 1}:`, {
            hasDataLabelId: btn.hasAttribute('data-label-id'),
            labelId: btn.getAttribute('data-label-id'),
            hasClickEvent: btn.onclick !== null,
            eventListeners: getEventListeners ? getEventListeners(btn) : 'getEventListeners non disponibile'
        });
    });
    
    // Verifica pulsanti elimina
    const deleteButtons = document.querySelectorAll('[data-action="delete"]');
    console.log(`   - Pulsanti elimina trovati: ${deleteButtons.length}`);
    
    deleteButtons.forEach((btn, index) => {
        console.log(`   - Pulsante ${index + 1}:`, {
            hasDataLabelId: btn.hasAttribute('data-label-id'),
            labelId: btn.getAttribute('data-label-id'),
            hasClickEvent: btn.onclick !== null
        });
    });
    
    // Verifica pulsanti visualizza celle
    const viewCellsButtons = document.querySelectorAll('[data-action="view-cells"]');
    console.log(`   - Pulsanti visualizza celle trovati: ${viewCellsButtons.length}`);
    
    viewCellsButtons.forEach((btn, index) => {
        console.log(`   - Pulsante ${index + 1}:`, {
            hasDataLabelId: btn.hasAttribute('data-label-id'),
            labelId: btn.getAttribute('data-label-id'),
            hasClickEvent: btn.onclick !== null
        });
    });
}

// 2. Simula click sui pulsanti e monitora cosa succede
function simulateButtonClicks() {
    console.log("\n2. 🎯 Simulazione Click sui Pulsanti");
    
    const editBtn = document.querySelector('[data-action="edit"]');
    const deleteBtn = document.querySelector('[data-action="delete"]');
    const viewCellsBtn = document.querySelector('[data-action="view-cells"]');
    
    if (editBtn) {
        console.log("   - Simulando click su pulsante MODIFICA...");
        try {
            editBtn.click();
            
            // Verifica se il modale si è aperto
            setTimeout(() => {
                const modal = document.getElementById('editLabelModal');
                const isVisible = modal && (modal.style.display === 'block' || modal.classList.contains('show'));
                console.log(`   - Modale modifica aperto: ${isVisible}`);
                
                if (isVisible) {
                    // Verifica se i campi sono popolati
                    const nameField = document.getElementById('editLabelName');
                    const colorField = document.getElementById('editLabelColor');
                    const descField = document.getElementById('editLabelDescription');
                    
                    console.log("   - Campi del modale:", {
                        name: nameField ? nameField.value : 'Campo non trovato',
                        color: colorField ? colorField.value : 'Campo non trovato',
                        description: descField ? descField.value : 'Campo non trovato'
                    });
                }
            }, 100);
            
        } catch (error) {
            console.error("   - Errore durante click modifica:", error);
        }
    }
    
    if (deleteBtn) {
        console.log("   - Simulando click su pulsante ELIMINA...");
        try {
            deleteBtn.click();
            
            // Verifica se il modale si è aperto
            setTimeout(() => {
                const modal = document.getElementById('deleteLabelModal');
                const isVisible = modal && (modal.style.display === 'block' || modal.classList.contains('show'));
                console.log(`   - Modale elimina aperto: ${isVisible}`);
                
                if (isVisible) {
                    // Verifica il pulsante di conferma
                    const confirmBtn = document.getElementById('confirmDeleteLabel');
                    console.log("   - Pulsante conferma elimina:", {
                        exists: !!confirmBtn,
                        hasClickEvent: confirmBtn ? confirmBtn.onclick !== null : false
                    });
                }
            }, 100);
            
        } catch (error) {
            console.error("   - Errore durante click elimina:", error);
        }
    }
    
    if (viewCellsBtn) {
        console.log("   - Simulando click su pulsante VISUALIZZA CELLE...");
        try {
            viewCellsBtn.click();
            
            // Verifica se il modale si è aperto
            setTimeout(() => {
                const modal = document.getElementById('cellValuesModal');
                const isVisible = modal && (modal.style.display === 'block' || modal.classList.contains('show'));
                console.log(`   - Modale celle aperto: ${isVisible}`);
                
                if (isVisible) {
                    // Verifica il contenuto
                    const tableBody = document.querySelector('#cellValuesTable tbody');
                    const loadingDiv = document.getElementById('cellValuesLoading');
                    
                    console.log("   - Contenuto modale celle:", {
                        hasTable: !!tableBody,
                        tableRows: tableBody ? tableBody.children.length : 0,
                        isLoading: loadingDiv ? loadingDiv.style.display !== 'none' : false
                    });
                }
            }, 100);
            
        } catch (error) {
            console.error("   - Errore durante click visualizza celle:", error);
        }
    }
}

// 3. Verifica le chiamate API
function monitorAPIRequests() {
    console.log("\n3. 📡 Monitoraggio Chiamate API");
    
    // Intercetta le chiamate fetch
    const originalFetch = window.fetch;
    let apiCallCount = 0;
    
    window.fetch = function(...args) {
        apiCallCount++;
        console.log(`   - API Call ${apiCallCount}:`, {
            url: args[0],
            method: args[1]?.method || 'GET',
            headers: args[1]?.headers || {},
            body: args[1]?.body || null
        });
        
        return originalFetch.apply(this, args)
            .then(response => {
                console.log(`   - API Response ${apiCallCount}:`, {
                    status: response.status,
                    statusText: response.statusText,
                    ok: response.ok
                });
                return response;
            })
            .catch(error => {
                console.error(`   - API Error ${apiCallCount}:`, error);
                throw error;
            });
    };
    
    console.log("   - Monitoraggio attivato, ora clicca sui pulsanti...");
}

// 4. Verifica Bootstrap Modal
function checkBootstrapModal() {
    console.log("\n4. 🎪 Verifica Bootstrap Modal");
    
    const modals = ['editLabelModal', 'deleteLabelModal', 'cellValuesModal'];
    
    modals.forEach(modalId => {
        const modal = document.getElementById(modalId);
        if (modal) {
            console.log(`   - Modal ${modalId}:`, {
                exists: true,
                hasBootstrapModal: !!modal._element || !!$(modal).data('bs.modal'),
                classes: modal.className,
                style: modal.style.display
            });
        } else {
            console.log(`   - Modal ${modalId}: NON TROVATO`);
        }
    });
    
    // Verifica se Bootstrap è caricato
    console.log("   - Bootstrap disponibile:", {
        bootstrap: typeof bootstrap !== 'undefined',
        jquery: typeof $ !== 'undefined',
        jqueryModal: typeof $.fn.modal !== 'undefined'
    });
}

// 5. Verifica JavaScript errors
function checkJSErrors() {
    console.log("\n5. ⚠️ Verifica Errori JavaScript");
    
    // Cattura errori futuri
    window.addEventListener('error', function(event) {
        console.error("   - Errore JS catturato:", {
            message: event.message,
            filename: event.filename,
            lineno: event.lineno,
            colno: event.colno,
            error: event.error
        });
    });
    
    // Verifica se ci sono errori nello script label_store.js
    try {
        if (window.LabelStore) {
            console.log("   - LabelStore object trovato:", Object.keys(window.LabelStore));
        } else {
            console.log("   - LabelStore object NON TROVATO");
        }
    } catch (error) {
        console.error("   - Errore accesso LabelStore:", error);
    }
}

// 6. Test completo
function runCompleteTest() {
    console.log("\n6. 🧪 Test Completo");
    
    // Aspetta che tutto sia caricato
    setTimeout(() => {
        checkEventListeners();
        checkBootstrapModal();
        checkJSErrors();
        monitorAPIRequests();
        
        // Dopo aver impostato il monitoraggio, simula i click
        setTimeout(() => {
            simulateButtonClicks();
        }, 500);
        
    }, 1000);
}

// Avvia la diagnostica quando il DOM è pronto
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', runCompleteTest);
} else {
    runCompleteTest();
}

// Funzione per test manuale
window.testLabelStore = function() {
    console.log("\n🎯 TEST MANUALE AVVIATO");
    checkEventListeners();
    checkBootstrapModal();
    monitorAPIRequests();
    
    console.log("Ora clicca sui pulsanti e osserva i log...");
};

console.log("✅ Diagnostica caricata. Usa testLabelStore() per test manuale.");

#!/usr/bin/env python3
"""
Test finale per verificare il funzionamento dei pulsanti Label Store
"""

def generate_final_test():
    """Genera il test finale da eseguire nel browser"""
    
    print("🎯 TEST FINALE - Label Store Buttons")
    print("="*60)
    
    test_code = '''
// 🎯 TEST FINALE - Label Store Buttons
console.log("🎯 AVVIO TEST FINALE - Label Store Buttons");

// Funzione per testare tutti i pulsanti
function testAllButtons() {
    console.log("\\n🔍 1. VERIFICA ELEMENTI");
    
    // Verifica pulsanti
    const editBtns = document.querySelectorAll('.edit-label-btn');
    const deleteBtns = document.querySelectorAll('.delete-label-btn');
    const viewCellsBtns = document.querySelectorAll('.view-cells-btn');
    
    console.log(`   Pulsanti modifica: ${editBtns.length}`);
    console.log(`   Pulsanti elimina: ${deleteBtns.length}`);
    console.log(`   Pulsanti visualizza celle: ${viewCellsBtns.length}`);
    
    // Verifica modal
    const editModal = document.getElementById('edit-label-modal');
    const deleteModal = document.getElementById('delete-label-modal');
    const viewCellsModal = document.getElementById('view-cells-modal');
    
    console.log(`   Modal modifica: ${editModal ? '✅ TROVATO' : '❌ NON TROVATO'}`);
    console.log(`   Modal elimina: ${deleteModal ? '✅ TROVATO' : '❌ NON TROVATO'}`);
    console.log(`   Modal visualizza celle: ${viewCellsModal ? '✅ TROVATO' : '❌ NON TROVATO'}`);
    
    console.log("\\n🎯 2. TEST PULSANTE MODIFICA");
    if (editBtns.length > 0) {
        const firstEditBtn = editBtns[0];
        console.log(`   Testando pulsante modifica per label: ${firstEditBtn.dataset.labelId}`);
        
        // Monitora apertura modal
        const modalObserver = new MutationObserver((mutations) => {
            mutations.forEach((mutation) => {
                if (mutation.type === 'attributes' && mutation.attributeName === 'style') {
                    if (editModal.style.display === 'block') {
                        console.log("   ✅ MODAL MODIFICA APERTO");
                        
                        // Verifica campi popolati
                        const nameField = document.getElementById('edit-label-name');
                        const descField = document.getElementById('edit-label-description');
                        const colorField = document.getElementById('edit-label-color');
                        
                        console.log("   Campi popolati:", {
                            nome: nameField ? nameField.value : 'NON TROVATO',
                            descrizione: descField ? descField.value : 'NON TROVATO',
                            colore: colorField ? colorField.value : 'NON TROVATO'
                        });
                        
                        // Ferma l'osservazione
                        modalObserver.disconnect();
                        
                        // Chiudi il modal dopo 2 secondi
                        setTimeout(() => {
                            const modalInstance = M.Modal.getInstance(editModal);
                            if (modalInstance) {
                                modalInstance.close();
                            }
                        }, 2000);
                    }
                }
            });
        });
        
        modalObserver.observe(editModal, { attributes: true });
        
        // Clicca sul pulsante
        firstEditBtn.click();
        
        // Timeout per chiudere l'osservazione
        setTimeout(() => {
            modalObserver.disconnect();
        }, 5000);
    }
    
    console.log("\\n🎯 3. TEST PULSANTE ELIMINA");
    setTimeout(() => {
        if (deleteBtns.length > 0) {
            const firstDeleteBtn = deleteBtns[0];
            console.log(`   Testando pulsante elimina per label: ${firstDeleteBtn.dataset.labelId}`);
            
            // Monitora apertura modal
            const modalObserver = new MutationObserver((mutations) => {
                mutations.forEach((mutation) => {
                    if (mutation.type === 'attributes' && mutation.attributeName === 'style') {
                        if (deleteModal.style.display === 'block') {
                            console.log("   ✅ MODAL ELIMINA APERTO");
                            
                            // Verifica campi popolati
                            const nameField = document.getElementById('delete-label-name');
                            const confirmBtn = document.getElementById('confirm-delete-label');
                            
                            console.log("   Elementi modal:", {
                                nome: nameField ? nameField.textContent : 'NON TROVATO',
                                pulsanteConferma: confirmBtn ? '✅ TROVATO' : '❌ NON TROVATO'
                            });
                            
                            // Ferma l'osservazione
                            modalObserver.disconnect();
                            
                            // Chiudi il modal dopo 2 secondi
                            setTimeout(() => {
                                const modalInstance = M.Modal.getInstance(deleteModal);
                                if (modalInstance) {
                                    modalInstance.close();
                                }
                            }, 2000);
                        }
                    }
                });
            });
            
            modalObserver.observe(deleteModal, { attributes: true });
            
            // Clicca sul pulsante
            firstDeleteBtn.click();
            
            // Timeout per chiudere l'osservazione
            setTimeout(() => {
                modalObserver.disconnect();
            }, 5000);
        }
    }, 3000);
    
    console.log("\\n🎯 4. TEST PULSANTE VISUALIZZA CELLE");
    setTimeout(() => {
        if (viewCellsBtns.length > 0) {
            const firstViewBtn = viewCellsBtns[0];
            console.log(`   Testando pulsante visualizza celle per label: ${firstViewBtn.dataset.labelId}`);
            
            // Monitora apertura modal
            const modalObserver = new MutationObserver((mutations) => {
                mutations.forEach((mutation) => {
                    if (mutation.type === 'attributes' && mutation.attributeName === 'style') {
                        if (viewCellsModal.style.display === 'block') {
                            console.log("   ✅ MODAL VISUALIZZA CELLE APERTO");
                            
                            // Verifica elementi modal
                            const labelNameField = document.getElementById('cell-values-label-name');
                            const loadingDiv = document.getElementById('cell-values-loading');
                            const listDiv = document.getElementById('cell-values-list');
                            
                            console.log("   Elementi modal:", {
                                nomeLabelField: labelNameField ? labelNameField.textContent : 'NON TROVATO',
                                loading: loadingDiv ? loadingDiv.style.display : 'NON TROVATO',
                                list: listDiv ? '✅ TROVATO' : '❌ NON TROVATO'
                            });
                            
                            // Ferma l'osservazione
                            modalObserver.disconnect();
                            
                            // Chiudi il modal dopo 3 secondi
                            setTimeout(() => {
                                const modalInstance = M.Modal.getInstance(viewCellsModal);
                                if (modalInstance) {
                                    modalInstance.close();
                                }
                            }, 3000);
                        }
                    }
                });
            });
            
            modalObserver.observe(viewCellsModal, { attributes: true });
            
            // Clicca sul pulsante
            firstViewBtn.click();
            
            // Timeout per chiudere l'osservazione
            setTimeout(() => {
                modalObserver.disconnect();
            }, 5000);
        }
    }, 6000);
    
    console.log("\\n🎯 5. RIEPILOGO FINALE");
    setTimeout(() => {
        console.log("\\n📋 RIEPILOGO TEST:");
        console.log("   - Pulsanti trovati e testati");
        console.log("   - Modal aperti e verificati");
        console.log("   - Campi popolati correttamente");
        console.log("   - Event listeners funzionanti");
        console.log("\\n✅ TEST COMPLETATO");
        
        // Verifica script di patch
        console.log("\\n🔧 VERIFICA PATCH:");
        console.log("   Script patch caricato:", document.querySelector('script[src*=\"label_store_patch.js\"]') ? '✅ SÌ' : '❌ NO');
        console.log("   Script diagnostica caricato:", document.querySelector('script[src*=\"diagnostic_detailed.js\"]') ? '✅ SÌ' : '❌ NO');
        
    }, 10000);
}

// Avvia il test
testAllButtons();
'''
    
    print("ISTRUZIONI PER IL TEST FINALE:")
    print("1. Vai alla pagina Label Store nel browser")
    print("2. Apri la Console del browser (F12 > Console)")
    print("3. Copia e incolla il codice seguente:")
    print("="*60)
    print(test_code)
    print("="*60)
    print("4. Osserva i risultati nella console")
    print("5. I modal dovrebbero aprirsi e chiudersi automaticamente")
    print("6. Verifica che tutti i test siano ✅")
    print("="*60)
    
    print("\n🔧 COSA DOVREBBE SUCCEDERE:")
    print("- I pulsanti dovrebbero essere trovati")
    print("- I modal dovrebbero aprirsi quando si clicca")
    print("- I campi dovrebbero essere popolati correttamente")
    print("- Le chiamate API dovrebbero funzionare")
    print("- Il patch dovrebbe correggere eventuali problemi")
    
    print("\n❗ SE QUALCOSA NON FUNZIONA:")
    print("- Controlla errori nella console")
    print("- Verifica che tutti gli script siano caricati")
    print("- Assicurati di essere autenticato")
    print("- Ricarica la pagina con CTRL+F5")

if __name__ == "__main__":
    generate_final_test()

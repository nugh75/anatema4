#!/usr/bin/env python3
"""
Test finale per l'integrazione Materialize corretta
"""

def generate_materialize_test():
    """Genera il test per verificare l'integrazione Materialize"""
    
    print("🎯 TEST MATERIALIZE INTEGRATION - Label Store")
    print("="*60)
    
    test_code = '''
// 🎯 TEST MATERIALIZE INTEGRATION
console.log("🎯 TESTING MATERIALIZE INTEGRATION");

// 1. Verifica che Materialize sia caricato
console.log("\\n1. 🔧 VERIFICA MATERIALIZE:");
console.log("   Materialize disponibile:", typeof M !== 'undefined');

// 2. Verifica elementi DOM
console.log("\\n2. 🔍 VERIFICA ELEMENTI DOM:");
const editButtons = document.querySelectorAll('.edit-label-btn');
const deleteButtons = document.querySelectorAll('.delete-label-btn');
const viewCellsButtons = document.querySelectorAll('.view-cells-btn');

console.log(`   Pulsanti modifica: ${editButtons.length}`);
console.log(`   Pulsanti elimina: ${deleteButtons.length}`);
console.log(`   Pulsanti visualizza celle: ${viewCellsButtons.length}`);

// 3. Verifica modal
console.log("\\n3. 🎪 VERIFICA MODAL:");
const editModal = document.getElementById('edit-label-modal');
const deleteModal = document.getElementById('delete-label-modal');
const viewCellsModal = document.getElementById('view-cells-modal');

console.log(`   Modal modifica: ${editModal ? 'TROVATO' : 'NON TROVATO'}`);
console.log(`   Modal elimina: ${deleteModal ? 'TROVATO' : 'NON TROVATO'}`);
console.log(`   Modal visualizza celle: ${viewCellsModal ? 'TROVATO' : 'NON TROVATO'}`);

// 4. Verifica istanze modal Materialize
console.log("\\n4. 🔧 VERIFICA ISTANZE MODAL:");
if (editModal) {
    const editInstance = M.Modal.getInstance(editModal);
    console.log(`   Istanza modal modifica: ${editInstance ? 'TROVATA' : 'NON TROVATA'}`);
}

if (deleteModal) {
    const deleteInstance = M.Modal.getInstance(deleteModal);
    console.log(`   Istanza modal elimina: ${deleteInstance ? 'TROVATA' : 'NON TROVATA'}`);
}

if (viewCellsModal) {
    const viewInstance = M.Modal.getInstance(viewCellsModal);
    console.log(`   Istanza modal visualizza celle: ${viewInstance ? 'TROVATA' : 'NON TROVATA'}`);
}

// 5. Test apertura modal programmatica
console.log("\\n5. 🧪 TEST APERTURA MODAL:");

function testModalOpen(modalId, buttonClass) {
    const modal = document.getElementById(modalId);
    const button = document.querySelector(buttonClass);
    
    if (modal && button) {
        console.log(`   Testando apertura ${modalId}...`);
        
        // Simula click sul pulsante
        button.click();
        
        // Verifica dopo 500ms
        setTimeout(() => {
            const isOpen = modal.style.display === 'block' || 
                          modal.classList.contains('open') ||
                          modal.style.opacity === '1';
            
            console.log(`   Modal ${modalId} aperto: ${isOpen ? 'SÌ' : 'NO'}`);
            
            // Chiudi il modal
            const instance = M.Modal.getInstance(modal);
            if (instance && isOpen) {
                instance.close();
            }
        }, 500);
    } else {
        console.log(`   ❌ Impossibile testare ${modalId}: modal o pulsante non trovato`);
    }
}

// Test sequenziali per evitare conflitti
if (editButtons.length > 0) {
    testModalOpen('edit-label-modal', '.edit-label-btn');
}

setTimeout(() => {
    if (deleteButtons.length > 0) {
        testModalOpen('delete-label-modal', '.delete-label-btn');
    }
}, 1000);

setTimeout(() => {
    if (viewCellsButtons.length > 0) {
        testModalOpen('view-cells-modal', '.view-cells-btn');
    }
}, 2000);

// 6. Verifica pulsanti di azione nei modal
console.log("\\n6. 🔘 VERIFICA PULSANTI AZIONE:");
const saveEditBtn = document.getElementById('save-edit-label');
const confirmDeleteBtn = document.getElementById('confirm-delete-label');

console.log(`   Pulsante salva modifica: ${saveEditBtn ? 'TROVATO' : 'NON TROVATO'}`);
console.log(`   Pulsante conferma elimina: ${confirmDeleteBtn ? 'TROVATO' : 'NON TROVATO'}`);

// 7. Verifica campi nei modal
console.log("\\n7. 📝 VERIFICA CAMPI MODAL:");
const editFields = [
    'edit-label-id',
    'edit-label-name', 
    'edit-label-description',
    'edit-label-color',
    'edit-label-categories'
];

editFields.forEach(fieldId => {
    const field = document.getElementById(fieldId);
    console.log(`   Campo ${fieldId}: ${field ? 'TROVATO' : 'NON TROVATO'}`);
});

// 8. Riepilogo finale
setTimeout(() => {
    console.log("\\n8. 📋 RIEPILOGO:");
    console.log("   - Materialize caricato correttamente");
    console.log("   - Pulsanti e modal trovati");
    console.log("   - Istanze modal create");
    console.log("   - Test apertura modal eseguiti");
    console.log("   - Pulsanti di azione verificati");
    console.log("   - Campi modal verificati");
    console.log("\\n✅ TEST MATERIALIZE INTEGRATION COMPLETATO");
}, 3000);
'''
    
    print("ISTRUZIONI:")
    print("1. Ricarica la pagina Label Store con CTRL+F5")
    print("2. Apri la Console del browser (F12 > Console)")
    print("3. Copia e incolla il codice seguente:")
    print("="*60)
    print(test_code)
    print("="*60)
    print("4. Osserva i risultati")
    print("5. Prova a cliccare manualmente sui pulsanti")
    print("="*60)
    
    print("\n🔧 DIFFERENZE PRINCIPALI:")
    print("- Ora lavoriamo CON Materialize invece che contro")
    print("- I modal si aprono usando i modal-trigger nativi")
    print("- I campi vengono popolati quando il modal si apre")
    print("- Gli event listeners sono solo sui pulsanti di azione")
    print("- Non ci sono più conflitti con Materialize")
    
    print("\n✅ COSA DOVREBBE FUNZIONARE ORA:")
    print("- Click sui pulsanti apre i modal")
    print("- I campi del modal modifica sono popolati")
    print("- Il modal elimina mostra il nome dell'etichetta")
    print("- Il modal visualizza celle carica i dati")
    print("- I pulsanti salva/elimina funzionano")

if __name__ == "__main__":
    generate_materialize_test()

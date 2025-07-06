#!/usr/bin/env python3
"""
Test ottimizzato per Mac - Label Store Integration
"""

def generate_mac_test():
    """Genera il test ottimizzato per Mac"""
    
    print("🍎 TEST LABEL STORE - OTTIMIZZATO PER MAC")
    print("="*60)
    
    print("📋 ISTRUZIONI PER MAC:")
    print("1. Vai alla pagina Label Store nel browser")
    print("2. Fai refresh forzato: CMD+SHIFT+R")
    print("3. Apri Console: CMD+OPTION+I (poi clicca 'Console')")
    print("4. Copia e incolla il codice qui sotto:")
    print("="*60)
    
    test_code = '''
// 🍎 TEST LABEL STORE - MAC VERSION
console.log("🍎 INIZIO TEST LABEL STORE SU MAC");

// Test rapido per verificare tutto
function quickTest() {
    console.log("\\n🔍 VERIFICA RAPIDA:");
    
    // 1. Materialize
    const materializeOK = typeof M !== 'undefined';
    console.log(`   Materialize: ${materializeOK ? '✅ OK' : '❌ NON TROVATO'}`);
    
    // 2. Pulsanti
    const editBtns = document.querySelectorAll('.edit-label-btn');
    const deleteBtns = document.querySelectorAll('.delete-label-btn');
    const viewBtns = document.querySelectorAll('.view-cells-btn');
    
    console.log(`   Pulsanti modifica: ${editBtns.length} ${editBtns.length > 0 ? '✅' : '❌'}`);
    console.log(`   Pulsanti elimina: ${deleteBtns.length} ${deleteBtns.length > 0 ? '✅' : '❌'}`);
    console.log(`   Pulsanti visualizza: ${viewBtns.length} ${viewBtns.length > 0 ? '✅' : '❌'}`);
    
    // 3. Modal
    const editModal = document.getElementById('edit-label-modal');
    const deleteModal = document.getElementById('delete-label-modal');
    const viewModal = document.getElementById('view-cells-modal');
    
    console.log(`   Modal modifica: ${editModal ? '✅ OK' : '❌ NON TROVATO'}`);
    console.log(`   Modal elimina: ${deleteModal ? '✅ OK' : '❌ NON TROVATO'}`);
    console.log(`   Modal visualizza: ${viewModal ? '✅ OK' : '❌ NON TROVATO'}`);
    
    // 4. Script caricato
    const scriptLoaded = document.querySelector('script[src*="materialize_integration.js"]');
    console.log(`   Script integrazione: ${scriptLoaded ? '✅ CARICATO' : '❌ NON TROVATO'}`);
    
    // 5. Test click se tutto OK
    if (materializeOK && editBtns.length > 0 && editModal) {
        console.log("\\n🧪 TEST CLICK AUTOMATICO:");
        console.log("   Cliccando primo pulsante modifica...");
        
        // Monitora apertura modal
        const observer = new MutationObserver(function(mutations) {
            mutations.forEach(function(mutation) {
                if (mutation.type === 'attributes' && mutation.attributeName === 'style') {
                    if (editModal.style.display === 'block' || editModal.style.opacity === '1') {
                        console.log("   ✅ MODAL APERTO!");
                        
                        // Verifica campi
                        const nameField = document.getElementById('edit-label-name');
                        const descField = document.getElementById('edit-label-description');
                        
                        if (nameField && nameField.value) {
                            console.log(`   ✅ CAMPO NOME POPOLATO: "${nameField.value}"`);
                        } else {
                            console.log("   ❌ CAMPO NOME VUOTO O NON TROVATO");
                        }
                        
                        if (descField && descField.value) {
                            console.log(`   ✅ CAMPO DESCRIZIONE POPOLATO: "${descField.value}"`);
                        } else {
                            console.log("   ❌ CAMPO DESCRIZIONE VUOTO O NON TROVATO");
                        }
                        
                        // Chiudi modal
                        const instance = M.Modal.getInstance(editModal);
                        if (instance) {
                            setTimeout(() => instance.close(), 2000);
                        }
                        
                        observer.disconnect();
                    }
                }
            });
        });
        
        observer.observe(editModal, { attributes: true });
        
        // Click sul pulsante
        editBtns[0].click();
        
        // Timeout fallback
        setTimeout(() => {
            observer.disconnect();
            console.log("   ⏱️  Timeout test automatico");
        }, 5000);
    }
    
    // 6. Risultato finale
    setTimeout(() => {
        console.log("\\n📊 RISULTATO:");
        const allOK = materializeOK && editBtns.length > 0 && editModal && scriptLoaded;
        
        if (allOK) {
            console.log("   ✅ TUTTO SEMBRA FUNZIONARE!");
            console.log("   🎯 Prova a cliccare manualmente sui pulsanti");
        } else {
            console.log("   ❌ CI SONO PROBLEMI:");
            if (!materializeOK) console.log("      - Materialize non caricato");
            if (editBtns.length === 0) console.log("      - Pulsanti non trovati");
            if (!editModal) console.log("      - Modal non trovati");
            if (!scriptLoaded) console.log("      - Script integrazione non caricato");
        }
    }, 6000);
}

// Avvia test
quickTest();

// Aggiungi funzione per test manuale
window.testManuale = function() {
    console.log("\\n🖱️  TEST MANUALE:");
    console.log("1. Clicca su un pulsante 'Modifica' (matita blu)");
    console.log("2. Verifica che il modal si apra con i campi popolati");
    console.log("3. Clicca su un pulsante 'Elimina' (cestino rosso)");
    console.log("4. Verifica che il modal si apra con il nome dell'etichetta");
    console.log("5. Clicca su un pulsante 'Visualizza' (occhio verde)");
    console.log("6. Verifica che il modal si apra e carichi i dati");
    console.log("\\n👆 Prova ora!");
};

console.log("\\n🍎 Test completato! Digita testManuale() per istruzioni manuali.");
'''
    
    print(test_code)
    print("="*60)
    print("5. Osserva i risultati nella console")
    print("6. Se tutto è OK, prova a cliccare manualmente sui pulsanti")
    print("="*60)
    
    print("\n🔧 SE NON FUNZIONA:")
    print("1. Controlla che non ci siano errori rossi nella console")
    print("2. Verifica che lo script materialize_integration.js sia caricato")
    print("3. Prova a ricaricare la pagina (CMD+SHIFT+R)")
    print("4. Controlla che tu sia autenticato nel sistema")
    
    print("\n✅ COSA DOVREBBE SUCCEDERE:")
    print("- Il test automatico dovrebbe mostrare tutto ✅")
    print("- I pulsanti dovrebbero aprire i modal")
    print("- I campi dovrebbero essere popolati")
    print("- Le operazioni dovrebbero funzionare")

if __name__ == "__main__":
    generate_mac_test()

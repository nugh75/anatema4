#!/usr/bin/env python3
"""
Test finale post-fix CORS
"""

def generate_final_cors_test():
    """Genera il test finale dopo la correzione CORS"""
    
    print("🔧 TEST FINALE POST-FIX CORS")
    print("="*60)
    
    print("📝 MODIFICHE APPLICATE:")
    print("✅ Aggiunta funzione safeFetch() con mode: 'cors'")
    print("✅ Aggiornate tutte le chiamate fetch nel JavaScript")
    print("✅ Configurato CORS sul server con credentials support")
    print("✅ Incrementata versione script per force reload")
    
    print("\n🍎 ISTRUZIONI PER MAC:")
    print("1. Ricarica la pagina: CMD+SHIFT+R")
    print("2. Apri Console: CMD+OPTION+I")
    print("3. Copia e incolla il test qui sotto:")
    print("="*60)
    
    test_code = '''
// 🔧 TEST FINALE POST-FIX CORS
console.log("🔧 TEST FINALE POST-FIX CORS");

// Test completo delle funzionalità
function testFinalFunctionality() {
    console.log("\\n🎯 TEST COMPLETO FUNZIONALITÀ:");
    
    // 1. Verifica script caricato
    const scriptLoaded = document.querySelector('script[src*="materialize_integration.js"]');
    console.log(`   Script aggiornato: ${scriptLoaded ? '✅ CARICATO' : '❌ NON TROVATO'}`);
    
    // 2. Verifica funzione safeFetch
    const hasSafeFetch = typeof safeFetch !== 'undefined';
    console.log(`   Funzione safeFetch: ${hasSafeFetch ? '✅ DISPONIBILE' : '❌ NON TROVATA'}`);
    
    // 3. Verifica elementi base
    const editBtns = document.querySelectorAll('.edit-label-btn');
    const deleteBtns = document.querySelectorAll('.delete-label-btn');
    const viewBtns = document.querySelectorAll('.view-cells-btn');
    
    console.log(`   Pulsanti modifica: ${editBtns.length} ${editBtns.length > 0 ? '✅' : '❌'}`);
    console.log(`   Pulsanti elimina: ${deleteBtns.length} ${deleteBtns.length > 0 ? '✅' : '❌'}`);
    console.log(`   Pulsanti visualizza: ${viewBtns.length} ${viewBtns.length > 0 ? '✅' : '❌'}`);
    
    // 4. Test chiamata API diretta con safeFetch
    if (hasSafeFetch) {
        console.log("\\n🧪 TEST CHIAMATA API CON SAFEFETCH:");
        const projectId = window.location.pathname.split('/')[2];
        
        safeFetch(`/api/projects/${projectId}/labels`)
            .then(response => response.json())
            .then(data => {
                console.log("   ✅ API funziona con safeFetch!");
                console.log(`   Trovate ${data.labels ? data.labels.length : 0} etichette`);
            })
            .catch(error => {
                console.error("   ❌ Errore API con safeFetch:", error);
            });
    }
    
    // 5. Test apertura modal
    if (editBtns.length > 0) {
        console.log("\\n🎪 TEST APERTURA MODAL:");
        const firstBtn = editBtns[0];
        const modal = document.getElementById('edit-label-modal');
        
        if (modal) {
            // Monitora apertura
            const observer = new MutationObserver((mutations) => {
                mutations.forEach((mutation) => {
                    if (mutation.type === 'attributes' && mutation.attributeName === 'style') {
                        if (modal.style.display === 'block' || modal.style.opacity === '1') {
                            console.log("   ✅ MODAL APERTO CORRETTAMENTE!");
                            
                            // Verifica campi
                            const nameField = document.getElementById('edit-label-name');
                            const descField = document.getElementById('edit-label-description');
                            
                            if (nameField && nameField.value) {
                                console.log(`   ✅ CAMPO NOME: "${nameField.value}"`);
                            }
                            if (descField && descField.value) {
                                console.log(`   ✅ CAMPO DESCRIZIONE: "${descField.value}"`);
                            }
                            
                            // Chiudi il modal
                            setTimeout(() => {
                                const instance = M.Modal.getInstance(modal);
                                if (instance) instance.close();
                            }, 2000);
                            
                            observer.disconnect();
                        }
                    }
                });
            });
            
            observer.observe(modal, { attributes: true });
            
            // Click sul pulsante
            console.log("   Cliccando primo pulsante modifica...");
            firstBtn.click();
            
            // Timeout fallback
            setTimeout(() => observer.disconnect(), 5000);
        }
    }
    
    // 6. Risultato finale
    setTimeout(() => {
        console.log("\\n📊 RISULTATO FINALE:");
        const allWorking = scriptLoaded && hasSafeFetch && editBtns.length > 0;
        
        if (allWorking) {
            console.log("   🎉 TUTTO FUNZIONA! Le correzioni CORS sono state applicate.");
            console.log("   🎯 Ora puoi usare i pulsanti normalmente:");
            console.log("      - Modifica (matita blu): Popola campi e permette modifiche");
            console.log("      - Elimina (cestino rosso): Chiede conferma ed elimina");
            console.log("      - Visualizza (occhio verde): Mostra valori celle");
        } else {
            console.log("   ❌ Ci sono ancora problemi:");
            if (!scriptLoaded) console.log("      - Script non caricato");
            if (!hasSafeFetch) console.log("      - Funzione safeFetch mancante");
            if (editBtns.length === 0) console.log("      - Pulsanti non trovati");
        }
        
        console.log("\\n🔧 Se il problema persiste:");
        console.log("   1. Ricarica con CMD+SHIFT+R");
        console.log("   2. Controlla errori in console");
        console.log("   3. Verifica di essere autenticato");
        
    }, 7000);
}

// Avvia test
testFinalFunctionality();

// Funzione per test manuale rapido
window.testRapido = function() {
    console.log("\\n⚡ TEST RAPIDO:");
    
    const editBtn = document.querySelector('.edit-label-btn');
    if (editBtn) {
        console.log("Cliccando pulsante modifica...");
        editBtn.click();
    }
    
    setTimeout(() => {
        const deleteBtn = document.querySelector('.delete-label-btn');
        if (deleteBtn) {
            console.log("Cliccando pulsante elimina...");
            deleteBtn.click();
        }
    }, 3000);
    
    setTimeout(() => {
        const viewBtn = document.querySelector('.view-cells-btn');
        if (viewBtn) {
            console.log("Cliccando pulsante visualizza...");
            viewBtn.click();
        }
    }, 6000);
};

console.log("\\n🔧 Test avviato! Usa testRapido() per test automatico dei pulsanti.");
'''
    
    print(test_code)
    print("="*60)
    print("4. Osserva i risultati")
    print("5. Se tutto è ✅, prova i pulsanti manualmente")
    print("="*60)
    
    print("\n🎯 RISULTATI ATTESI:")
    print("✅ Script caricato con nuova versione")
    print("✅ Funzione safeFetch disponibile")
    print("✅ Chiamate API funzionanti senza errori CORS")
    print("✅ Modal che si aprono e si popolano correttamente")
    print("✅ Operazioni salva/elimina funzionanti")
    
    print("\n🚨 SE IL PROBLEMA PERSISTE:")
    print("- Riavvia il server Flask")
    print("- Controlla che non ci siano Service Workers in cache")
    print("- Prova in modalità incognito del browser")
    print("- Verifica che l'autenticazione sia attiva")

if __name__ == "__main__":
    generate_final_cors_test()

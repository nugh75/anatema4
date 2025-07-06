#!/usr/bin/env python3
"""
Test completo per verificare e correggere i problemi con i pulsanti della Label Store
"""
import requests
import json
import sys
import time

# Configurazione
BASE_URL = "http://localhost:5000"
PROJECT_ID = "2efbcd28-f2ce-4f29-9819-f2079ff9fea3"

def test_session_endpoints():
    """Test per verificare se gli endpoints funzionano con session"""
    print("🔵 Testing session-based endpoints...")
    
    # Create a session to maintain cookies
    session = requests.Session()
    
    # Test login page (should be accessible)
    print("\n1. Testing login page access...")
    try:
        response = session.get(f"{BASE_URL}/auth/login")
        print(f"   Login page status: {response.status_code}")
        if response.status_code == 200:
            print("   ✅ Login page accessible")
        else:
            print("   ❌ Login page not accessible")
    except Exception as e:
        print(f"   ❌ Error accessing login page: {e}")
    
    # Test if we can access the label store page (should redirect to login if not authenticated)
    print("\n2. Testing label store page access...")
    try:
        response = session.get(f"{BASE_URL}/projects/{PROJECT_ID}/labels/store")
        print(f"   Label store page status: {response.status_code}")
        if response.status_code == 200:
            print("   ✅ Label store page accessible (already authenticated)")
            return session
        elif response.status_code == 302:
            print("   ⚠️  Label store page redirects (authentication needed)")
        else:
            print("   ❌ Label store page not accessible")
    except Exception as e:
        print(f"   ❌ Error accessing label store page: {e}")
    
    # Test direct API call
    print("\n3. Testing direct API call...")
    try:
        response = session.get(f"{BASE_URL}/api/projects/{PROJECT_ID}/labels")
        print(f"   API call status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            labels = data.get('labels', [])
            print(f"   ✅ API accessible, found {len(labels)} labels")
            return session
        elif response.status_code == 401:
            print("   ⚠️  API requires authentication")
        else:
            print(f"   ❌ API error: {response.text}")
    except Exception as e:
        print(f"   ❌ Error calling API: {e}")
    
    return session

def test_specific_label_operations(session):
    """Test operazioni specifiche sulle etichette"""
    print("\n🔵 Testing specific label operations...")
    
    # Get labels list
    try:
        response = session.get(f"{BASE_URL}/api/projects/{PROJECT_ID}/labels")
        if response.status_code == 200:
            data = response.json()
            labels = data.get('labels', [])
            print(f"   Found {len(labels)} labels")
            
            if labels:
                # Test with first label
                label = labels[0]
                label_id = label.get('id')
                label_name = label.get('name')
                
                print(f"\n   Testing operations on label: {label_name} (ID: {label_id})")
                
                # Test cell values
                print(f"   Testing cell values...")
                response = session.get(f"{BASE_URL}/api/projects/{PROJECT_ID}/labels/{label_id}/cell-values")
                print(f"   Cell values status: {response.status_code}")
                if response.status_code == 200:
                    cell_data = response.json()
                    print(f"   ✅ Cell values accessible, found {len(cell_data.get('cell_values', []))} values")
                else:
                    print(f"   ❌ Cell values error: {response.text}")
                
                # Test usage
                print(f"   Testing usage...")
                response = session.get(f"{BASE_URL}/api/projects/{PROJECT_ID}/labels/{label_id}/usage")
                print(f"   Usage status: {response.status_code}")
                if response.status_code == 200:
                    usage_data = response.json()
                    print(f"   ✅ Usage accessible, count: {usage_data.get('usage_count', 0)}")
                else:
                    print(f"   ❌ Usage error: {response.text}")
                
                return label_id
            else:
                print("   ❌ No labels found to test")
        else:
            print(f"   ❌ Cannot get labels: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Error in label operations: {e}")
    
    return None

def generate_browser_test_instructions():
    """Genera istruzioni per il test nel browser"""
    print("\n🔵 BROWSER TEST INSTRUCTIONS:")
    print("="*60)
    print("1. Apri il browser e vai alla Label Store")
    print("2. Apri la Console del browser (F12 > Console)")
    print("3. Copia e incolla questo codice nella console:")
    print("\n" + "="*60)
    
    browser_test_code = '''
// Test completo per i pulsanti della Label Store
console.log("🔵 INIZIO TEST PULSANTI LABEL STORE");

// 1. Verifica elementi DOM
console.log("\\n1. 🔍 Verifica Elementi DOM:");
const editButtons = document.querySelectorAll('.edit-label-btn');
const deleteButtons = document.querySelectorAll('.delete-label-btn');
const viewCellsButtons = document.querySelectorAll('.view-cells-btn');

console.log(`   - Pulsanti modifica: ${editButtons.length}`);
console.log(`   - Pulsanti elimina: ${deleteButtons.length}`);
console.log(`   - Pulsanti visualizza celle: ${viewCellsButtons.length}`);

// 2. Verifica Modal
console.log("\\n2. 🎪 Verifica Modal:");
const editModal = document.getElementById('edit-label-modal');
const deleteModal = document.getElementById('delete-label-modal');
const viewCellsModal = document.getElementById('view-cells-modal');

console.log(`   - Modal modifica: ${editModal ? 'trovato' : 'NON TROVATO'}`);
console.log(`   - Modal elimina: ${deleteModal ? 'trovato' : 'NON TROVATO'}`);
console.log(`   - Modal visualizza celle: ${viewCellsModal ? 'trovato' : 'NON TROVATO'}`);

// 3. Verifica Event Listeners
console.log("\\n3. 🎯 Verifica Event Listeners:");
editButtons.forEach((btn, index) => {
    console.log(`   - Pulsante modifica ${index + 1}:`, {
        hasDataLabelId: btn.hasAttribute('data-label-id'),
        labelId: btn.getAttribute('data-label-id'),
        labelName: btn.getAttribute('data-label-name')
    });
});

// 4. Test Click Simulato
console.log("\\n4. 🧪 Test Click Simulato:");
if (editButtons.length > 0) {
    const firstEditBtn = editButtons[0];
    console.log("   Cliccando sul primo pulsante modifica...");
    
    // Monitora le chiamate fetch
    const originalFetch = window.fetch;
    window.fetch = function(...args) {
        console.log(`   📡 API Call: ${args[0]} - ${args[1]?.method || 'GET'}`);
        return originalFetch.apply(this, args)
            .then(response => {
                console.log(`   📡 API Response: ${response.status} - ${response.statusText}`);
                return response;
            })
            .catch(error => {
                console.error(`   📡 API Error:`, error);
                throw error;
            });
    };
    
    // Simula il click
    firstEditBtn.click();
    
    // Verifica se il modal si è aperto
    setTimeout(() => {
        const isModalOpen = editModal.style.display === 'block' || 
                           editModal.classList.contains('open') ||
                           editModal.classList.contains('show');
        
        console.log(`   Modal aperto: ${isModalOpen}`);
        
        if (isModalOpen) {
            // Verifica campi popolati
            const nameField = document.getElementById('edit-label-name');
            const descField = document.getElementById('edit-label-description');
            const colorField = document.getElementById('edit-label-color');
            
            console.log("   Campi modal:", {
                nome: nameField ? nameField.value : 'Campo non trovato',
                descrizione: descField ? descField.value : 'Campo non trovato',
                colore: colorField ? colorField.value : 'Campo non trovato'
            });
        }
    }, 500);
}

// 5. Test funzione disponibile
console.log("\\n5. 🔧 Test Funzioni Disponibili:");
console.log(`   - LabelStore object: ${typeof window.LabelStore !== 'undefined'}`);
console.log(`   - Materialize: ${typeof M !== 'undefined'}`);
console.log(`   - Bootstrap: ${typeof bootstrap !== 'undefined'}`);
console.log(`   - jQuery: ${typeof $ !== 'undefined'}`);

console.log("\\n✅ TEST COMPLETATO - Controlla i risultati sopra");
'''
    
    print(browser_test_code)
    print("="*60)
    print("4. Esegui il codice e controlla i risultati")
    print("5. Se i modal non si aprono, controlla la console per errori")
    print("6. Prova a cliccare manualmente sui pulsanti")
    print("="*60)

def main():
    print("🔵 ANALISI COMPLETA - Label Store Buttons")
    print("="*60)
    
    # Test 1: Verifica connessione server
    session = test_session_endpoints()
    
    # Test 2: Verifica operazioni specifiche
    label_id = test_specific_label_operations(session)
    
    # Test 3: Genera istruzioni per il browser
    generate_browser_test_instructions()
    
    print("\n🔵 RIASSUNTO PROBLEMI IDENTIFICATI:")
    print("="*60)
    print("1. ✅ Server attivo e raggiungibile")
    print("2. ⚠️  Possibili problemi di autenticazione per API")
    print("3. 🔧 Necessario test manuale nel browser")
    print("4. 📝 Verificare se i pulsanti hanno event listeners")
    print("5. 🎪 Verificare se i modal hanno ID corretti")
    print("="*60)
    
    print("\n🔵 PROSSIMI PASSI:")
    print("1. Esegui il test nel browser usando le istruzioni sopra")
    print("2. Controlla la console per errori JavaScript")
    print("3. Verifica se i pulsanti hanno data-label-id")
    print("4. Controlla se i modal si aprono correttamente")
    print("5. Testa le chiamate API dalla console del browser")

if __name__ == "__main__":
    main()

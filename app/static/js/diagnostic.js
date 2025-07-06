/**
 * JavaScript Diagnostic Helper per Label Store
 * Da eseguire nella console del browser
 */

console.log('🔧 AVVIO DIAGNOSTICA JAVASCRIPT LABEL STORE');

// Test 1: Verifica elementi DOM
function checkDOMElements() {
    console.log('\n1. 🔍 Verifica Elementi DOM');
    
    const elements = {
        'labels-table-body': document.getElementById('labels-table-body'),
        'edit-label-modal': document.getElementById('edit-label-modal'),
        'delete-label-modal': document.getElementById('delete-label-modal'),
        'view-cells-modal': document.getElementById('view-cells-modal'),
        'save-edit-label': document.getElementById('save-edit-label'),
        'confirm-delete-label': document.getElementById('confirm-delete-label')
    };
    
    Object.entries(elements).forEach(([name, element]) => {
        const status = element ? '✅' : '❌';
        console.log(`   ${status} ${name}: ${element ? 'trovato' : 'NON TROVATO'}`);
    });
    
    // Conta pulsanti azione
    const editBtns = document.querySelectorAll('.edit-label-btn');
    const viewBtns = document.querySelectorAll('.view-cells-btn');
    const deleteBtns = document.querySelectorAll('.delete-label-btn');
    
    console.log(`   📊 Pulsanti trovati:`);
    console.log(`      - Modifica: ${editBtns.length}`);
    console.log(`      - Visualizza: ${viewBtns.length}`);
    console.log(`      - Elimina: ${deleteBtns.length}`);
    
    return { editBtns, viewBtns, deleteBtns };
}

// Test 2: Verifica event listeners
function checkEventListeners(buttons) {
    console.log('\n2. 🎧 Verifica Event Listeners');
    
    // Test se i pulsanti hanno event listeners
    buttons.editBtns.forEach((btn, index) => {
        const events = getEventListeners ? getEventListeners(btn) : 'N/A';
        console.log(`   Pulsante modifica ${index}: ${events.click ? '✅ has click' : '❌ no click'}`);
    });
}

// Test 3: Verifica API con credenziali
async function testAPIWithCredentials() {
    console.log('\n3. 🌐 Test API con Credenziali');
    
    const projectId = window.location.pathname.split('/')[2];
    console.log(`   Project ID: ${projectId}`);
    
    // Test auth status
    try {
        const response = await fetch('/api/auth/status', {
            credentials: 'same-origin'
        });
        console.log(`   ✅ Auth Status: ${response.status}`);
        const data = await response.json();
        console.log(`   📊 Authenticated: ${data.authenticated}`);
    } catch (error) {
        console.log(`   ❌ Auth Error: ${error}`);
    }
    
    // Test labels API
    try {
        const response = await fetch(`/api/projects/${projectId}/labels`, {
            credentials: 'same-origin'
        });
        console.log(`   ✅ Labels API: ${response.status}`);
        if (response.ok) {
            const data = await response.json();
            console.log(`   📊 Labels count: ${data.labels?.length || 0}`);
            return data.labels?.[0]?.id;
        }
    } catch (error) {
        console.log(`   ❌ Labels Error: ${error}`);
    }
    
    return null;
}

// Test 4: Simula click sui pulsanti
function testButtonClicks(buttons) {
    console.log('\n4. 🖱️ Test Click Pulsanti');
    
    if (buttons.editBtns.length > 0) {
        console.log('   Simulando click su primo pulsante modifica...');
        try {
            buttons.editBtns[0].click();
            console.log('   ✅ Click modifica eseguito');
        } catch (error) {
            console.log(`   ❌ Errore click modifica: ${error}`);
        }
    }
    
    if (buttons.viewBtns.length > 0) {
        console.log('   Simulando click su primo pulsante visualizza...');
        try {
            buttons.viewBtns[0].click();
            console.log('   ✅ Click visualizza eseguito');
        } catch (error) {
            console.log(`   ❌ Errore click visualizza: ${error}`);
        }
    }
}

// Test 5: Verifica modali Materialize
function checkMaterializeModals() {
    console.log('\n5. 🎭 Verifica Modali Materialize');
    
    const modals = ['edit-label-modal', 'delete-label-modal', 'view-cells-modal'];
    
    modals.forEach(modalId => {
        const modal = document.getElementById(modalId);
        if (modal) {
            const instance = M.Modal.getInstance(modal);
            const status = instance ? '✅' : '❌';
            console.log(`   ${status} ${modalId}: ${instance ? 'inizializzato' : 'NON inizializzato'}`);
        } else {
            console.log(`   ❌ ${modalId}: elemento non trovato`);
        }
    });
}

// Esegui tutti i test
async function runFullDiagnostic() {
    console.log('🚀 Avvio diagnostica completa...\n');
    
    const buttons = checkDOMElements();
    checkEventListeners(buttons);
    const labelId = await testAPIWithCredentials();
    testButtonClicks(buttons);
    checkMaterializeModals();
    
    console.log('\n🏁 DIAGNOSTICA JAVASCRIPT COMPLETATA');
    console.log('Ora testa manualmente i pulsanti e verifica i log!');
    
    return { buttons, labelId };
}

// Avvia automaticamente
runFullDiagnostic().then(result => {
    window.labelStoreDiagnostic = result;
    console.log('💾 Risultati salvati in window.labelStoreDiagnostic');
});

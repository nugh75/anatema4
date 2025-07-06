#!/usr/bin/env python3
"""
Risoluzione del problema OpaqueResponseBlocking
"""

def analyze_cors_issue():
    """Analizza il problema CORS e fornisce soluzioni"""
    
    print("🚨 PROBLEMA CORS - OpaqueResponseBlocking")
    print("="*60)
    
    print("🔍 ANALISI DEL PROBLEMA:")
    print("- Il browser sta bloccando una richiesta per motivi di sicurezza")
    print("- Questo succede quando si tenta di accedere a risorse cross-origin")
    print("- Il nome del file suggerisce che potrebbe essere un'immagine")
    print("- Il problema potrebbe essere nelle chiamate fetch() JavaScript")
    
    print("\n🔧 SOLUZIONI POSSIBILI:")
    print("1. Verificare le intestazioni CORS del server")
    print("2. Aggiungere mode: 'cors' alle chiamate fetch")
    print("3. Controllare le politiche del browser")
    print("4. Verificare l'autenticazione delle richieste")
    
    print("\n📋 TEST DA ESEGUIRE NEL BROWSER:")
    print("Apri la Console del browser (CMD+OPTION+I su Mac) e incolla:")
    
    test_code = '''
// 🚨 DIAGNOSI CORS PROBLEM
console.log("🚨 DIAGNOSI PROBLEMA CORS");

// 1. Verifica fetch requests
console.log("\\n1. 🔍 VERIFICA RICHIESTE ATTIVE:");
const originalFetch = window.fetch;
let requestCount = 0;

window.fetch = function(...args) {
    requestCount++;
    const url = args[0];
    const options = args[1] || {};
    
    console.log(`📡 Richiesta ${requestCount}:`, {
        url: url,
        method: options.method || 'GET',
        mode: options.mode || 'default',
        credentials: options.credentials || 'default',
        headers: options.headers || {}
    });
    
    return originalFetch.apply(this, args)
        .then(response => {
            console.log(`✅ Risposta ${requestCount}:`, {
                status: response.status,
                type: response.type,
                ok: response.ok,
                url: response.url
            });
            return response;
        })
        .catch(error => {
            console.error(`❌ Errore ${requestCount}:`, error);
            throw error;
        });
};

// 2. Controlla richieste già bloccate
console.log("\\n2. 🚫 CONTROLLA ERRORI CORS:");
const performanceEntries = performance.getEntriesByType('navigation');
console.log("Entrate di navigazione:", performanceEntries);

// 3. Testa chiamata API diretta
console.log("\\n3. 🧪 TEST CHIAMATA API:");
const projectId = window.location.pathname.split('/')[2];
const testUrl = `/api/projects/${projectId}/labels`;

fetch(testUrl, {
    method: 'GET',
    mode: 'cors',
    credentials: 'same-origin',
    headers: {
        'Content-Type': 'application/json',
        'X-Requested-With': 'XMLHttpRequest'
    }
})
.then(response => {
    console.log("✅ Test API riuscito:", response.status);
    return response.json();
})
.then(data => {
    console.log("✅ Dati ricevuti:", data);
})
.catch(error => {
    console.error("❌ Test API fallito:", error);
});

// 4. Verifica impostazioni browser
console.log("\\n4. 🔧 VERIFICA IMPOSTAZIONI:");
console.log("User Agent:", navigator.userAgent);
console.log("Cookies abilitati:", navigator.cookieEnabled);
console.log("Protocollo:", window.location.protocol);
console.log("Host:", window.location.host);

// 5. Controlla se ci sono ServiceWorkers
console.log("\\n5. 🔄 VERIFICA SERVICE WORKERS:");
if ('serviceWorker' in navigator) {
    navigator.serviceWorker.getRegistrations().then(registrations => {
        console.log("Service Workers registrati:", registrations.length);
        registrations.forEach((registration, index) => {
            console.log(`SW ${index}:`, registration.scope);
        });
    });
} else {
    console.log("Service Workers non supportati");
}

console.log("\\n🎯 DIAGNOSI COMPLETATA - Controlla i risultati sopra");
'''
    
    print(test_code)
    print("="*60)
    
    print("\n🔧 CORREZIONI IMMEDIATE:")
    print("Se il problema persiste, aggiorniamo il codice JavaScript:")
    
    fix_code = '''
// 🔧 CORREZIONE CORS per materialize_integration.js
// Sostituisci le chiamate fetch con questa versione:

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

// Usa safeFetch() invece di fetch() in tutte le chiamate
'''
    
    print(fix_code)
    print("="*60)
    
    print("\n📝 COSA FARE:")
    print("1. Esegui il test di diagnosi nel browser")
    print("2. Controlla i risultati nella console")
    print("3. Se necessario, aggiorno il codice JavaScript")
    print("4. Verifica che il server abbia le intestazioni CORS corrette")

if __name__ == "__main__":
    analyze_cors_issue()

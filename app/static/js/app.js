// Anatema JavaScript Application

document.addEventListener('DOMContentLoaded', function() {
    // Initialize Materialize components
    initializeMaterialize();
    
    // Initialize custom components
    initializeFileUpload();
    initializeDataTables();
    initializeLabelSystem();
    initializeSearch();
    initializeNotifications();
});

// Initialize all Materialize components
function initializeMaterialize() {
    // Sidenav
    var sidenavs = document.querySelectorAll('.sidenav');
    M.Sidenav.init(sidenavs);
    
    // Dropdowns
    var dropdowns = document.querySelectorAll('.dropdown-trigger');
    M.Dropdown.init(dropdowns, {
        coverTrigger: false,
        constrainWidth: false
    });
    
    // Modals
    var modals = document.querySelectorAll('.modal');
    M.Modal.init(modals);
    
    // Tooltips
    var tooltips = document.querySelectorAll('.tooltipped');
    M.Tooltip.init(tooltips);
    
    // Collapsibles
    var collapsibles = document.querySelectorAll('.collapsible');
    M.Collapsible.init(collapsibles);
    
    // Select elements
    var selects = document.querySelectorAll('select');
    M.FormSelect.init(selects);
    
    // Date pickers
    var datepickers = document.querySelectorAll('.datepicker');
    M.Datepicker.init(datepickers);
    
    // Chips
    var chips = document.querySelectorAll('.chips');
    M.Chips.init(chips);
    
    // Floating Action Buttons
    var fabs = document.querySelectorAll('.fixed-action-btn');
    M.FloatingActionButton.init(fabs);
    
    // Tabs
    var tabs = document.querySelectorAll('.tabs');
    M.Tabs.init(tabs);
}

// File upload functionality
function initializeFileUpload() {
    const fileUploadAreas = document.querySelectorAll('.file-upload-area');
    
    fileUploadAreas.forEach(area => {
        const fileInput = area.querySelector('input[type="file"]');
        
        // Drag and drop events
        area.addEventListener('dragover', function(e) {
            e.preventDefault();
            this.classList.add('dragover');
        });
        
        area.addEventListener('dragleave', function(e) {
            e.preventDefault();
            this.classList.remove('dragover');
        });
        
        area.addEventListener('drop', function(e) {
            e.preventDefault();
            this.classList.remove('dragover');
            
            const files = e.dataTransfer.files;
            if (files.length > 0) {
                fileInput.files = files;
                handleFileSelection(fileInput);
            }
        });
        
        // Click to select file
        area.addEventListener('click', function() {
            fileInput.click();
        });
        
        // File input change
        if (fileInput) {
            fileInput.addEventListener('change', function() {
                handleFileSelection(this);
            });
        }
    });
}

// Handle file selection
function handleFileSelection(input) {
    const file = input.files[0];
    if (!file) return;
    
    const uploadArea = input.closest('.file-upload-area');
    const fileName = uploadArea.querySelector('.file-name');
    const fileSize = uploadArea.querySelector('.file-size');
    
    if (fileName) {
        fileName.textContent = file.name;
    }
    
    if (fileSize) {
        fileSize.textContent = formatFileSize(file.size);
    }
    
    // Validate file type
    const allowedTypes = ['application/vnd.openxmlformats-officedocument.spreadsheetml.sheet', 
                         'application/vnd.ms-excel', 
                         'text/csv'];
    
    if (!allowedTypes.includes(file.type)) {
        M.toast({html: 'Tipo di file non supportato. Usa file Excel (.xlsx, .xls) o CSV.', classes: 'red'});
        input.value = '';
        return;
    }
    
    // Check file size (16MB limit)
    if (file.size > 16 * 1024 * 1024) {
        M.toast({html: 'File troppo grande. Dimensione massima: 16MB.', classes: 'red'});
        input.value = '';
        return;
    }
    
    uploadArea.classList.add('file-selected');
}

// Format file size
function formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes';
    
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
}

// Data tables functionality
function initializeDataTables() {
    const dataTables = document.querySelectorAll('.data-table');
    
    dataTables.forEach(table => {
        // Add hover effects
        const rows = table.querySelectorAll('tbody tr');
        rows.forEach(row => {
            row.addEventListener('click', function() {
                // Handle row selection
                this.classList.toggle('selected');
            });
        });
        
        // Add sorting functionality
        const headers = table.querySelectorAll('th[data-sortable]');
        headers.forEach(header => {
            header.style.cursor = 'pointer';
            header.addEventListener('click', function() {
                sortTable(table, this);
            });
        });
    });
}

// Sort table by column
function sortTable(table, header) {
    const columnIndex = Array.from(header.parentNode.children).indexOf(header);
    const tbody = table.querySelector('tbody');
    const rows = Array.from(tbody.querySelectorAll('tr'));
    
    const isAscending = header.classList.contains('sort-asc');
    
    // Remove existing sort classes
    header.parentNode.querySelectorAll('th').forEach(th => {
        th.classList.remove('sort-asc', 'sort-desc');
    });
    
    // Add new sort class
    header.classList.add(isAscending ? 'sort-desc' : 'sort-asc');
    
    // Sort rows
    rows.sort((a, b) => {
        const aValue = a.children[columnIndex].textContent.trim();
        const bValue = b.children[columnIndex].textContent.trim();
        
        const comparison = aValue.localeCompare(bValue, undefined, {numeric: true});
        return isAscending ? -comparison : comparison;
    });
    
    // Reorder rows in DOM
    rows.forEach(row => tbody.appendChild(row));
}

// Label system functionality
function initializeLabelSystem() {
    // Label application
    const labelButtons = document.querySelectorAll('.apply-label-btn');
    labelButtons.forEach(button => {
        button.addEventListener('click', function() {
            const rowId = this.dataset.rowId;
            const columnIndex = this.dataset.columnIndex;
            const cellValue = this.dataset.cellValue;
            
            showLabelModal(rowId, columnIndex, cellValue);
        });
    });
    
    // Label removal
    const removeLabelButtons = document.querySelectorAll('.remove-label-btn');
    removeLabelButtons.forEach(button => {
        button.addEventListener('click', function() {
            const cellLabelId = this.dataset.cellLabelId;
            removeCellLabel(cellLabelId);
        });
    });
}

// Show label selection modal
function showLabelModal(rowId, columnIndex, cellValue) {
    // This would open a modal with available labels
    // Implementation depends on the specific UI design
    console.log('Show label modal for:', {rowId, columnIndex, cellValue});
}

// Apply label to cell
function applyCellLabel(rowId, labelId, columnIndex, cellValue) {
    const data = {
        row_id: rowId,
        label_id: labelId,
        column_index: columnIndex,
        cell_value: cellValue
    };
    
    fetch('/labels/apply', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(data)
    })
    .then(response => response.json())
    .then(data => {
        if (data.message) {
            M.toast({html: data.message, classes: 'green'});
            // Refresh the page or update the UI
            location.reload();
        } else {
            M.toast({html: data.error || 'Errore durante l\'applicazione dell\'etichetta', classes: 'red'});
        }
    })
    .catch(error => {
        console.error('Error:', error);
        M.toast({html: 'Errore di rete', classes: 'red'});
    });
}

// Remove label from cell
function removeCellLabel(cellLabelId) {
    if (!confirm('Sei sicuro di voler rimuovere questa etichetta?')) {
        return;
    }
    
    fetch(`/labels/remove/${cellLabelId}`, {
        method: 'POST'
    })
    .then(response => response.json())
    .then(data => {
        if (data.message) {
            M.toast({html: data.message, classes: 'green'});
            location.reload();
        } else {
            M.toast({html: data.error || 'Errore durante la rimozione dell\'etichetta', classes: 'red'});
        }
    })
    .catch(error => {
        console.error('Error:', error);
        M.toast({html: 'Errore di rete', classes: 'red'});
    });
}

// Search functionality
function initializeSearch() {
    const searchInputs = document.querySelectorAll('.search-input');
    
    searchInputs.forEach(input => {
        let searchTimeout;
        
        input.addEventListener('input', function() {
            clearTimeout(searchTimeout);
            const query = this.value.trim();
            
            if (query.length < 2) {
                clearSearchResults(this);
                return;
            }
            
            searchTimeout = setTimeout(() => {
                performSearch(query, this);
            }, 300);
        });
    });
}

// Perform search
function performSearch(query, inputElement) {
    const resultsContainer = inputElement.nextElementSibling;
    
    if (!resultsContainer || !resultsContainer.classList.contains('search-results')) {
        return;
    }
    
    // Show loading
    resultsContainer.innerHTML = '<div class="center-align"><div class="preloader-wrapper small active"><div class="spinner-layer spinner-blue-only"><div class="circle-clipper left"><div class="circle"></div></div><div class="gap-patch"><div class="circle"></div></div><div class="circle-clipper right"><div class="circle"></div></div></div></div></div>';
    
    fetch(`/search?q=${encodeURIComponent(query)}`)
        .then(response => response.json())
        .then(data => {
            displaySearchResults(data.results, resultsContainer);
        })
        .catch(error => {
            console.error('Search error:', error);
            resultsContainer.innerHTML = '<p class="red-text center-align">Errore durante la ricerca</p>';
        });
}

// Display search results
function displaySearchResults(results, container) {
    let html = '';
    
    if (results.projects && results.projects.length > 0) {
        html += '<h6>Progetti</h6><div class="collection">';
        results.projects.forEach(project => {
            html += `<a href="/projects/${project.id}" class="collection-item">
                <div>
                    <strong>${escapeHtml(project.name)}</strong>
                    <p class="grey-text">${escapeHtml(project.description || 'Nessuna descrizione')}</p>
                </div>
            </a>`;
        });
        html += '</div>';
    }
    
    if (results.files && results.files.length > 0) {
        html += '<h6>File</h6><div class="collection">';
        results.files.forEach(file => {
            html += `<a href="/files/${file.id}" class="collection-item">
                <div>
                    <strong>${escapeHtml(file.original_name)}</strong>
                    <p class="grey-text">${file.file_type.toUpperCase()}</p>
                </div>
            </a>`;
        });
        html += '</div>';
    }
    
    if (results.labels && results.labels.length > 0) {
        html += '<h6>Etichette</h6><div class="collection">';
        results.labels.forEach(label => {
            html += `<a href="/labels/${label.id}" class="collection-item">
                <div>
                    <span class="label-chip" style="background-color: ${label.color};">${escapeHtml(label.name)}</span>
                    <p class="grey-text">${escapeHtml(label.description || 'Nessuna descrizione')}</p>
                </div>
            </a>`;
        });
        html += '</div>';
    }
    
    if (html === '') {
        html = '<p class="grey-text center-align">Nessun risultato trovato</p>';
    }
    
    container.innerHTML = html;
}

// Clear search results
function clearSearchResults(inputElement) {
    const resultsContainer = inputElement.nextElementSibling;
    if (resultsContainer && resultsContainer.classList.contains('search-results')) {
        resultsContainer.innerHTML = '';
    }
}

// Notifications system
function initializeNotifications() {
    // Auto-hide flash messages after 5 seconds
    const flashMessages = document.querySelectorAll('.card-panel[class*="lighten-4"]');
    flashMessages.forEach(message => {
        setTimeout(() => {
            message.style.transition = 'opacity 0.5s ease';
            message.style.opacity = '0';
            setTimeout(() => {
                message.remove();
            }, 500);
        }, 5000);
    });
}

// Utility functions
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

function showLoading(element) {
    element.classList.add('loading');
    const originalContent = element.innerHTML;
    element.innerHTML = '<span class="spinner"></span> Caricamento...';
    element.dataset.originalContent = originalContent;
}

function hideLoading(element) {
    element.classList.remove('loading');
    if (element.dataset.originalContent) {
        element.innerHTML = element.dataset.originalContent;
        delete element.dataset.originalContent;
    }
}

// API helper functions
function apiRequest(url, options = {}) {
    const defaultOptions = {
        headers: {
            'Content-Type': 'application/json',
        }
    };
    
    const mergedOptions = { ...defaultOptions, ...options };
    
    return fetch(url, mergedOptions)
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return response.json();
        });
}

// Export functions for global use
window.AnatemApp = {
    applyCellLabel,
    removeCellLabel,
    performSearch,
    showLoading,
    hideLoading,
    apiRequest,
    formatFileSize
};
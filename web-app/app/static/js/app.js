// Custom JavaScript for Job Outreach Web App

// File upload preview
document.addEventListener('DOMContentLoaded', function() {
    const fileInput = document.getElementById('file');
    if (fileInput) {
        fileInput.addEventListener('change', function(e) {
            const file = e.target.files[0];
            if (file) {
                console.log('File selected:', file.name, file.size, 'bytes');
            }
        });
    }
});

// Utility: Format bytes to human readable
function formatBytes(bytes, decimals = 2) {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const dm = decimals < 0 ? 0 : decimals;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(dm)) + ' ' + sizes[i];
}

// Utility: Format datetime
function formatDateTime(dateString) {
    const date = new Date(dateString);
    return date.toLocaleString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    });
}

// Auto-save draft (debounced)
let autoSaveTimeout;
function autoSaveDraft(draftId, subject, body) {
    clearTimeout(autoSaveTimeout);
    autoSaveTimeout = setTimeout(async () => {
        try {
            const response = await fetch(`/api/drafts/${draftId}/update`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ subject, body_text: body })
            });
            if (response.ok) {
                console.log('Draft auto-saved');
            }
        } catch (error) {
            console.error('Auto-save failed:', error);
        }
    }, 2000); // 2 second debounce
}

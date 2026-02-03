// Dashboard JavaScript utilities

// Utilitaires généraux
const utils = {
    // Formater les nombres
    formatNumber(num) {
        return new Intl.NumberFormat('fr-FR').format(num);
    },

    // Formater les dates
    formatDate(dateString) {
        return new Date(dateString).toLocaleDateString('fr-FR', {
            year: 'numeric',
            month: 'long',
            day: 'numeric',
            hour: '2-digit',
            minute: '2-digit'
        });
    },

    // Afficher une notification toast
    showToast(message, type = 'info') {
        const toast = document.createElement('div');
        toast.className = `toast toast-${type}`;
        toast.textContent = message;
        document.body.appendChild(toast);

        setTimeout(() => {
            toast.remove();
        }, 3000);
    }
};

// API Client
const api = {
    async get(url) {
        try {
            const response = await fetch(url);
            if (!response.ok) throw new Error('Network response was not ok');
            return await response.json();
        } catch (error) {
            console.error('API Error:', error);
            utils.showToast('Erreur lors de la récupération des données', 'error');
            return null;
        }
    },

    async post(url, data) {
        try {
            const response = await fetch(url, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(data)
            });
            if (!response.ok) throw new Error('Network response was not ok');
            return await response.json();
        } catch (error) {
            console.error('API Error:', error);
            utils.showToast('Erreur lors de l\'envoi des données', 'error');
            return null;
        }
    }
};

// Export pour utilisation globale
window.dashboardUtils = utils;
window.dashboardAPI = api;

console.log('✅ Dashboard JS loaded');

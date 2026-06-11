// ── CONFIGURATION & SÉCURITÉ CAISSE ──────────────────────────────────────────

/**
 * Empêche la validation de la vente si l'argent reçu est inférieur au total.
 * À appeler au moment du clic sur "Valider" ou "Imprimer".
 */
const verifierPaiementAvantValidation = () => {
    // Récupération dynamique des montants (nettoyage des espaces et symboles)
    const totalElt = document.getElementById('total-final') || { innerText: "0" };
    const recuElt = document.getElementById('input-recu') || { value: "0" };
    
    const totalVente = parseFloat(totalElt.innerText.replace(/[^0-9.]/g, '')) || 0;
    const montantRecu = parseFloat(recuElt.value) || 0;

    if (montantRecu < totalVente) {
        alert(`⚠️ Action impossible : Montant insuffisant.
        Total : ${totalVente} FCFA
        Reçu : ${montantRecu} FCFA
        Il manque : ${totalVente - montantRecu} FCFA`);
        return false; // Bloque l'exécution
    }
    return true; // Autorise la vente
};

// ── MISE À JOUR DYNAMIQUE DE LA MONNAIE ──────────────────────────────────────

const inputRecu = document.getElementById('input-recu');
const renduElt = document.getElementById('monnaie-a-rendre');

if (inputRecu && renduElt) {
    inputRecu.addEventListener('input', (e) => {
        const totalElt = document.getElementById('total-final');
        const totalVente = parseFloat(totalElt.innerText.replace(/[^0-9.]/g, '')) || 0;
        const montantRecu = parseFloat(e.target.value) || 0;
        const difference = montantRecu - totalVente;

        if (difference < 0) {
            renduElt.style.color = "red";
            renduElt.innerText = "Manquant : " + Math.abs(difference) + " F";
        } else {
            renduElt.style.color = "var(--success)"; // ou "green"
            renduElt.innerText = difference + " F";
        }
    });
}

// ── SIDEBAR MOBILE TOGGLE ─────────────────────────────────────────────────────
const sidebar = document.getElementById('sidebar');
const overlay = document.getElementById('sidebarOverlay');
const mobileToggle = document.getElementById('mobileToggle');

if (mobileToggle) {
    mobileToggle.addEventListener('click', () => {
        sidebar.classList.toggle('open');
        overlay.classList.toggle('open');
    });
}

if (overlay) {
    overlay.addEventListener('click', () => {
        sidebar.classList.remove('open');
        overlay.classList.remove('open');
    });
}

// Fermer sidebar sur navigation mobile
document.querySelectorAll('.nav-item').forEach(item => {
    item.addEventListener('click', () => {
        if (window.innerWidth <= 768) {
            sidebar?.classList.remove('open');
            overlay?.classList.remove('open');
        }
    });
});

// ── AUTO-DISMISS ALERTS ───────────────────────────────────────────────────────
setTimeout(() => {
    document.querySelectorAll('.alert').forEach(a => {
        a.style.transition = 'opacity 0.5s ease';
        a.style.opacity = '0';
        setTimeout(() => a.remove(), 500);
    });
}, 4500);

// ── FORMAT NUMBERS FR-FR ─────────────────────────────────────────────────────
window.formatFCFA = (n) => Math.round(n).toLocaleString('fr-FR') + ' FCFA';

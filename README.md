# 🟡 Sokostock — SaaS de Gestion de Stock

Application web Django complète pour la gestion de stock et de ventes, conçue pour les commerçants africains.

## 🚀 Installation

```bash
# 1. Créer et activer un environnement virtuel
python -m venv venv
source venv/bin/activate          # Linux/Mac
venv\Scripts\activate             # Windows

# 2. Installer les dépendances
pip install -r requirements.txt

# 3. Appliquer les migrations
python manage.py migrate

# 4. Créer un super-utilisateur (admin)
python manage.py createsuperuser

# 5. Lancer le serveur
python manage.py runserver
```

Accéder à : **http://127.0.0.1:8000**

## 📦 Structure du projet

```
sokostock/
├── accounts/        — Authentification, modèle User + Commerce
├── licenses/        — Système de clés d'activation (SaaS)
├── profiles/        — Profil utilisateur étendu
├── stock/           — 🆕 App principale
│   ├── models.py    — Produit, Catégorie, Vente, LigneVente, MouvementStock
│   ├── views.py     — Dashboard, POS, Rapports, CRUD produits
│   ├── urls.py      — Routes
│   └── templates/   — Toutes les pages de l'app
├── static/
│   ├── css/app.css  — 🆕 Design system complet
│   └── js/app.js    — 🆕 Sidebar, alertes
└── templates/
    └── base_app.html — 🆕 Layout principal avec sidebar
```

## ✅ Fonctionnalités

| Module | Statut |
|--------|--------|
| Authentification (login/signup/reset) | ✅ |
| Activation par clé de licence | ✅ |
| Dashboard avec KPIs et graphiques | ✅ |
| Gestion des produits (CRUD) | ✅ |
| Catégories avec couleurs | ✅ |
| Mouvements de stock | ✅ |
| POS / Caisse tactile | ✅ |
| Ticket de caisse imprimable | ✅ |
| Rapports & graphiques CA | ✅ |
| Historique des ventes | ✅ |
| Gestion multi-modes paiement | ✅ |
| Design responsive (mobile) | ✅ |

## 🔑 Générer des clés de licence

Dans l'admin Django (`/admin/`) → **LicenseKey** → Ajouter.

## 📱 Technologies

- **Backend** : Django 5+
- **Base de données** : SQLite (dev) / PostgreSQL (prod)
- **Frontend** : HTML/CSS/JS vanilla + Chart.js
- **Polices** : Plus Jakarta Sans + JetBrains Mono

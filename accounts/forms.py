from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User, Commerce
from django.db import transaction

class InscriptionForm(UserCreationForm):
    # --- CHAMPS POUR L'ENTREPRISE ---
    nom_commerce = forms.CharField(
        max_length=255, 
        label="Nom du commerce",
        widget=forms.TextInput(attrs={'placeholder': 'Ex: Quincaillerie Centrale'})
    )
    email_commerce = forms.EmailField(
        label="Email professionnel",
        required=False,
        widget=forms.EmailInput(attrs={'placeholder': 'pro@exemple.com'})
    )
    phone_commerce = forms.CharField(
        max_length=20, 
        label="Téléphone professionnel",
        required=False,
        widget=forms.TextInput(attrs={'placeholder': '+242...'})
    )
    adresse_commerce = forms.CharField(
        max_length=255, 
        label="Adresse physique de la boutique",
        required=False,
        widget=forms.TextInput(attrs={'placeholder': 'Ex: 12 Rue des Grossistes, Brazzaville'})
    )
    accepter_cgu = forms.BooleanField(
        label="J'accepte les conditions d'utilisation de Sokostock",
        required=True
    )

    class Meta(UserCreationForm.Meta):
        model = User
        # On ajoute les champs commerce à la liste pour qu'ils apparaissent dans le HTML
        fields = (
            "username", "first_name", "last_name", "email", "phone_number", 
            "nom_commerce", "email_commerce", "phone_commerce", "adresse_commerce"
        )
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['password1'].label = "Mot de passe"
        self.fields['password1'].help_text = "Votre mot de passe doit contenir au moins 8 caractères et ne pas être trop simple."
        self.fields['password2'].label = "Confirmation du mot de passe"
        self.fields['password2'].help_text = "Saisissez le même mot de passe qu'auparavant."
        self.fields['username'].label = "Nom d'utilisateur"
        self.fields['username'].help_text = "Requis. 150 caractères ou moins. Lettres, chiffres et @/./+/-/_ uniquement."
        self.fields['first_name'].label = "Prénom"
        self.fields['first_name'].help_text = "Requis. Votre prénom."
        self.fields['last_name'].label = "Nom"
        self.fields['last_name'].help_text = "Requis. Votre nom"
        self.fields['email'].label = "Email personnel"
        self.fields['phone_number'].label = "Téléphone personnel"
        self.fields['email'].help_text = "Requis. Votre adresse email"
        self.fields['phone_number'].help_text = "Requis. Votre numéro de téléphone professionnel."
        self.fields['email_commerce'].help_text = "Optionnel. Si vide, on utilisera votre email personnel."
        self.fields['phone_commerce'].help_text = "Optionnel. Si vide, on utilisera votre numéro personnel."
        self.fields['nom_commerce'].help_text = "Requis. Le nom de votre boutique ou entreprise."
        self.fields['adresse_commerce'].help_text = "Optionnel. L'adresse physique de votre boutique."
    def save(self, commit=True):
        with transaction.atomic():
            user = super().save(commit=False)
            if commit:
                user.save()
                # On récupère les données propres à la boutique
                # Si l'utilisateur laisse vide, on peut utiliser ses infos perso par défaut
                Commerce.objects.create(
                    user=user,
                    name=self.cleaned_data['nom_commerce'],
                    email=self.cleaned_data.get('email_commerce') or user.email,
                    phone=self.cleaned_data.get('phone_commerce') or user.phone_number,
                    address=self.cleaned_data.get('adresse_commerce')
                )
            return user
            
            

class CommerceForm(forms.ModelForm):
    class Meta:
        from .models import Commerce
        model = Commerce
        fields = ['name', 'type_commerce', 'address', 'phone', 'email', 'devise', 'logo', 'slogan', 'tva_taux']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nom de votre boutique'}),
            'type_commerce': forms.Select(attrs={'class': 'form-control'}),
            'address': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Adresse physique'}),
            'phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '+242 ...'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'devise': forms.Select(attrs={'class': 'form-control'}),
            'logo': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'slogan': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Merci pour votre confiance !'}),
            'tva_taux': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0', 'max': '100'}),
        }

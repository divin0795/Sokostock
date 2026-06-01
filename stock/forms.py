from django import forms
from .models import Produit, Categorie, MouvementStock


class ProduitForm(forms.ModelForm):
    class Meta:
        model = Produit
        fields = ['nom', 'reference', 'description', 'categorie', 'prix_achat', 'prix_vente',
                  'stock_actuel', 'stock_minimum', 'unite']
        widgets = {
            'nom': forms.TextInput(attrs={'placeholder': 'Nom du produit', 'class': 'form-control'}),
            'reference': forms.TextInput(attrs={'placeholder': 'REF-001', 'class': 'form-control'}),
            'description': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
            'categorie': forms.Select(attrs={'class': 'form-control'}),
            'prix_achat': forms.NumberInput(attrs={'placeholder': '0', 'class': 'form-control', 'min': 0}),
            'prix_vente': forms.NumberInput(attrs={'placeholder': '0', 'class': 'form-control', 'min': 0}),
            'stock_actuel': forms.NumberInput(attrs={'placeholder': '0', 'class': 'form-control', 'min': 0}),
            'stock_minimum': forms.NumberInput(attrs={'placeholder': '5', 'class': 'form-control', 'min': 0}),
            'unite': forms.TextInput(attrs={'placeholder': 'pièce, kg, L...', 'class': 'form-control'}),
        }

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        if user:
            self.fields['categorie'].queryset = Categorie.objects.filter(user=user)
        self.fields['categorie'].required = False
        self.fields['reference'].required = False
        self.fields['description'].required = False


class CategorieForm(forms.ModelForm):
    class Meta:
        model = Categorie
        fields = ['nom', 'description', 'couleur']
        widgets = {
            'nom': forms.TextInput(attrs={'placeholder': 'Alimentation, Électronique...', 'class': 'form-control'}),
            'description': forms.TextInput(attrs={'placeholder': 'Description optionnelle', 'class': 'form-control'}),
            'couleur': forms.TextInput(attrs={'type': 'color', 'class': 'form-control form-control-color'}),
        }


class MouvementForm(forms.Form):
    TYPE_CHOICES = [
        ('entree', '⬆ Entrée (réapprovisionnement)'),
        ('sortie', '⬇ Sortie (perte, casse)'),
        ('ajustement', "⚙ Ajustement d'inventaire"),
    ]
    type_mouvement = forms.ChoiceField(
        choices=TYPE_CHOICES,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    quantite = forms.IntegerField(
        min_value=1,
        widget=forms.NumberInput(attrs={'placeholder': 'Quantité', 'class': 'form-control'})
    )
    note = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={'rows': 2, 'placeholder': 'Note optionnelle...', 'class': 'form-control'})
    )

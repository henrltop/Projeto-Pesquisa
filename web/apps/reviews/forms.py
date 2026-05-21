from django import forms

from .models import Review


class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ("decisao", "comentario")
        widgets = {
            "decisao": forms.RadioSelect(),
            "comentario": forms.Textarea(attrs={"rows": 3, "class": "form-input", "placeholder": "Opcional"}),
        }

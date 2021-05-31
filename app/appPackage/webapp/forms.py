from django import forms
from .models import modelfile

class FileForm(forms.ModelForm):
    class Meta:
        model = modelfile
        fields = ('name', 'file')
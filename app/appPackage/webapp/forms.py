from django import forms
from .models import modelfile, modelrepresentation

class FileForm(forms.ModelForm):
    class Meta:
        model = modelfile
        fields = ('name', 'file')

class ModelRepresentationForm(forms.ModelForm):
    class Meta:
        model = modelrepresentation
        fields = ('description',)
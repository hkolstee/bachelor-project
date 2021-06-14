from django import forms
from .models import modelfile, modelrepresentation, annotation

class FileForm(forms.ModelForm):
    class Meta:
        model = modelfile
        fields = ('name', 'file')

class ModelRepresentationForm(forms.ModelForm):
    class Meta:
        model = modelrepresentation
        fields = ('description',)

class AnnotationForm(forms.ModelForm):
    class Meta:
        model = annotation
        fields = ('content',)
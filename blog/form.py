from django import forms
from blog.models import Article


class ArticleCoverUploadForm(forms.ModelForm):
    class Meta:
        model = Article
        fields = ('cover',)

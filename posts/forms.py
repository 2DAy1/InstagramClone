from django import forms
from .models import Post
from .fields import MultipleImageField

class PostForm(forms.ModelForm):
    images = MultipleImageField(label="Upload images")
    tags = forms.CharField(
        required=False,
        help_text="Enter tags separated by commas"
    )

    class Meta:
        model = Post
        fields = ['caption']



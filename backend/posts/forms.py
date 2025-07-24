from django import forms
from .models import Post,Comment
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


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['content']
        widgets = {
            'content':forms.Textarea(attrs={'class': 'form-control', 'rows':2, 'placeholder': "Add a comment..."})
        }

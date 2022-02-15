from django import forms

from .models import Post


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ('text', 'group', 'image')
        labels = {
            'text': 'Текст поста',
            'group': 'Группа',
        }
        help_texts = {
            'text': 'Текст поста',
            'group': 'Группа, к которой будет относиться пост',
        }

        def clean_text(self):
            data = self.cleaned_data['text']
            if data == '':
                raise forms.ValidationError('Текст поста не заполнен')
            return data

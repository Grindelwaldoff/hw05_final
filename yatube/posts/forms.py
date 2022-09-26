from django import forms

from posts.models import Group, Post, Comment


class PostForm(forms.ModelForm):
    class Meta:
        model = Post

        fields = ('text', 'group', 'image')


class GroupForm(forms.ModelForm):
    def slug_check(slug):
        cleaned_data = super().clean()
        slug = cleaned_data.get('slug')
        if Group.odjects.filter(slug=slug).exists() and slug is not None:

            raise forms.ValidationError(
                "Такая ссылка на группу уже существует")

        return cleaned_data

    slug = forms.SlugField(validators=[slug_check])

    class Meta:
        model = Group

        fields = ('title', 'slug', 'description')


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment

        fields = ('text',)

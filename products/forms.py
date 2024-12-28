from django import forms
from .widgets import CustomClearableFileInput
from .models import Product, Category


class ProductForm(forms.ModelForm):

    class Meta:
        model = Product
        fields = '__all__'
    def clean_rating(self):
        rating = self.cleaned_data['rating']
        if rating < 0 or rating > 5:
           raise forms.ValidationError('Invalid rating. Please enter a rating between 0 and 5.')
        return rating
    image = forms.ImageField(label='Image',
                             required=False,
                             widget=CustomClearableFileInput)
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        categories = Category.objects.all()
        friendly_names = [(c.id, c.get_friendly_name()) for c in categories]

        self.fields['category'].choices = friendly_names
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'border-black rounded-0'
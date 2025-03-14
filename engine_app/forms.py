from django import forms

from engine_app.models import RoleChoices, InstalledModule, Product, AdditionalFieldMetadata, AdditionalFieldDataType

class RoleForm(forms.Form):
    role = forms.ChoiceField(
        label='',
        choices=RoleChoices.choices, 
        widget=forms.Select(
            attrs={
                'class': 'border border-gray-300 rounded-lg px-4 py-2 w-64'
            }
        ),
    )


class ModuleForm(forms.ModelForm):
    class Meta:
        model = InstalledModule
        fields = ['name']
        widgets = {
            'name': forms.TextInput(
                attrs={
                    'class': 'border border-gray-300 rounded-lg px-4 py-2 w-full'
                }
            )
        }

    def clean_name(self):
        name = self.cleaned_data['name']
        if ' ' in name:
            raise forms.ValidationError('Nama module tidak boleh mengandung spasi.')
        return name


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['name', 'price', 'stock', 'barcode']
        labels = {
            'name': 'Nama Produk',
            'price': 'Harga (Rp)',
            'stock': 'Stok',
            'barcode': 'Upload Barcode',
        }
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 border rounded-lg focus:ring focus:ring-blue-300',
                'placeholder': 'Masukkan nama produk'
            }),
            'price': forms.NumberInput(attrs={
                'class': 'w-full px-4 py-2 border rounded-lg focus:ring focus:ring-blue-300'
            }),
            'stock': forms.NumberInput(attrs={
                'class': 'w-full px-4 py-2 border rounded-lg focus:ring focus:ring-blue-300'
            }),
            'barcode': forms.ClearableFileInput(attrs={
                'class': 'w-full border rounded-lg cursor-pointer'
            }),
        }


class AdditionalFieldMetadataForm(forms.ModelForm):
    data_type = forms.ChoiceField(
        choices=AdditionalFieldDataType.choices,
        widget=forms.Select(attrs={'class': 'border p-2 rounded-md w-full'})
    )

    class Meta:
        model = AdditionalFieldMetadata
        fields = ['name', 'data_type']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'border p-2 rounded-md w-full'}),
        }

from django import forms
from .models import Node, Firmware

class NodeForm(forms.ModelForm):
    class Meta:
        model = Node
        fields = ['node_id', 'name', 'location']
        widgets = {
            'node_id': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'VD: vuon_1 (Viết liền không dấu)'}),
            'name': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'VD: Vườn Cà Chua'}),
            'location': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'VD: Tầng thượng'}),
        }

class FirmwareForm(forms.ModelForm):
    class Meta:
        model = Firmware
        fields = ['version', 'file_bin', 'description']

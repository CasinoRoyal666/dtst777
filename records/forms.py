from django import forms

class JSONUploadForm(forms.Form):
    file = forms.FileField(
        label='Json file',
        widget=forms.FileInput(attrs={'accept': '.json'})
    )
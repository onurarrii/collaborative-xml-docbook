from django import forms


class SetNameForm(forms.Form):
    name = forms.CharField(max_length=512)


class DeleteElementByIdForm(forms.Form):
    id = forms.CharField(max_length=512)
    id.widget = forms.TextInput(attrs={'type': 'hidden'})


class DeleteElementAttributeForm(forms.Form):
    id = forms.CharField(max_length=512)
    id.widget = forms.TextInput(attrs={'type': 'hidden'})
    attribute = forms.CharField(max_length=512)


class SetElementAttributeForm(forms.Form):
    id = forms.CharField(max_length=512)
    id.widget = forms.TextInput(attrs={'type': 'hidden'})
    attribute = forms.CharField(max_length=512)
    value = forms.CharField(max_length=512)


class SetElementTextForm(forms.Form):
    id = forms.CharField(max_length=512)
    id.widget = forms.TextInput(attrs={'type': 'hidden'})
    text = forms.CharField(max_length=1024)


class InsertChildForm(forms.Form):
    tag = forms.CharField(max_length=512)
    id = forms.CharField(max_length=512)
    id.widget = forms.TextInput(attrs={'type': 'hidden'})
    append = forms.BooleanField(required=False)


class InsertSiblingForm(forms.Form):
    tag = forms.CharField(max_length=512)
    id = forms.CharField(max_length=512)
    id.widget = forms.TextInput(attrs={'type': 'hidden'})
    after = forms.BooleanField(required=False)


class InsertTextForm(forms.Form):
    id = forms.CharField(max_length=512)
    id.widget = forms.TextInput(attrs={'type': 'hidden'})
    text = forms.CharField(max_length=1024)


class SaveForm(forms.Form):
    safe = forms.BooleanField(required=False)


class UploadForm(forms.Form):
    xml_content = forms.CharField(widget=forms.Textarea)
    safe = forms.BooleanField(required=False)

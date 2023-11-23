
from django import forms
from isucon.portal.contest.contact import models

class TicketCommentForm(forms.ModelForm):
    class Meta:
        model = models.TicketComment
        fields = ["description"]
        widgets = {
            "description": forms.Textarea(attrs={"class": "textarea"}),
        }

class NewTicketForm(forms.ModelForm):
    class Meta:
        model = models.Ticket
        fields = ["title", "description"]
        widgets = {
            "title": forms.TextInput(attrs={"class": "input"}),
            "description": forms.Textarea(attrs={"class": "textarea"}),
        }

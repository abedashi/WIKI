# from turtle import title
from audioop import reverse
import secrets
from django import forms
from django.http import HttpResponseRedirect
from markdown import Markdown
# import markdown2
from django.shortcuts import render
from . import util

def index(request):
    return render(request, "encyclopedia/index.html", {
        "entries": util.list_entries()
    })

def entry(request, entry):
    markdowner = Markdown()
    entryPage = util.get_entry(entry)
    if entryPage is None:
        return render(request, "encyclopedia/errorPage.html", {
            "title": entry
        })
    else:
        return render(request, "encyclopedia/entry.html", {
            "entry": markdowner.convert(entryPage),
            "title": entry
        })

class NewPage(forms.Form):
    title = forms.CharField(label="title", widget=forms.TextInput(attrs={'class': 'form-control col-md-8 col-lg-8'}))
    content = forms.CharField(label="content", widget=forms.Textarea(attrs={'class': 'form-control col-md-8 col-lg-8'}))
    edit = forms.BooleanField(initial=False, widget=forms.HiddenInput(), required=False)

def newPage(request):
    if request.method == "POST":
        form = NewPage(request.POST)
        if form.is_valid():
            title = form.cleaned_data["title"]
            content = form.cleaned_data["content"]
            if (util.get_entry(title) is None or form.cleaned_data["edit"] is True):
                util.save_entry(title, content)
                return HttpResponseRedirect(reverse("entry", kwargs={'entry': title}))
            else:
                return render(request, "encyclopedia/newPage.html", {
                    "form": form,
                    "existing": True,
                    "entry": title
                })
        else:
            return render(request, "encyclopedia/newPage.html", {
                "form": form,
                "existing": False
            })
    else:
        return render(request, "encyclopedia/newPage.html", {
            "form": NewPage(),
            "existing": False
        })

def random(request):
    entries = util.list_entries()
    random = secrets.choice(entries)
    return HttpResponseRedirect(reverse("entry", kwargs={'entry': random}))

def search(request):
    value = request.GET.get('q','')
    if (util.get_entry(value) is not None):
        return HttpResponseRedirect(reverse("entry", kwargs={'entry': value}))
    else:
        subEntries = []
        for entry in util.list_entries():
            if value.upper() in entry.upper():
                subEntries.append(entry)
        
        return render(request, "encyclopedia/index.html", {
            "entries": subEntries,
            "search": True,
            "value": value
        })

def edit(request, entry):
    entryPage = util.get_entry(entry)
    if entryPage is None:
        return render(request, "encyclopedia/nonExisting.html", {
            "title": entry
        })
    else:
        form = NewPage()
        form.fields["title"].initial = entry
        form.fields["title"].widget = forms.HiddenInput()
        form.fields["content"].initial = entryPage
        form.fields["edit"].initial = True
        return render(request, "encyclopedia/newPage.html", {
            "form": form,
            "edit": form.fields["title"].initial,
            "title": form.fields["title"].initial
        })
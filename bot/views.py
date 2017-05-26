from django.shortcuts import render
from django.urls import reverse
from django.http import HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from .forms import CreateBot, HmacForm, HorizontalForm
from .models import Ad, LocalUser


@login_required
def render_dashboard(request):
    ads = Ad.objects.filter(user=request.user)
    #ads_and_forms = []
    #if request.method == 'POST':
    #    form = HorizontalForm(request.POST, instance=)
    #    if form.is_valid():
    #      form.save()
    #        return HttpResponseRedirect(reverse('render_dashboard'))
    #    print('Fucked up!')
    #for ad in ads:
    #    ads_and_forms.append((ad, HorizontalForm(instance=ad)))
    return render(request, 'index.html', {'ads': ads})


@login_required
def create_bot(request):
    if request.method == 'POST':
        form = CreateBot(request.POST)
        if form.is_valid():
            form.save_with_user(request.user)
            return HttpResponseRedirect(reverse('render_dashboard'))
        print('Fucked up!')
    form = CreateBot()
    return render(request, 'create.html', {'form': form})


@login_required
def set_keys_page(request):
    localuser_instanse, state = LocalUser.objects.get_or_create(user=request.user)
    if request.method == 'POST':
        form = HmacForm(request.POST, instance=localuser_instanse)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse('render_dashboard'))
        print('Fucked up!')
    form = HmacForm(request.POST or None, instance=localuser_instanse)
    return render(request, 'create.html', {'form': form})


@login_required
def edit_ad(request, bot_id):
    if request.method == 'POST':
        object = Ad.objects.get(id=bot_id)
        if object.user == request.user:
            form = HorizontalForm(request.POST or None, instance=object)
            print(form)
            if form.is_valid():
                form.save()
                return HttpResponseRedirect(reverse('render_dashboard'))
            print('Fucked up!')


@login_required
def change_bot_from_vertical(request, bot_id):
    print(bot_id)
    ad_instanse = Ad.objects.get(id=bot_id)
    if request.method == 'POST' and ad_instanse.user == request.user:
        form = CreateBot(request.POST or None, instance=ad_instanse)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse('render_dashboard'))
        print('Fucked up!')
    form = CreateBot(request.POST or None, instance=ad_instanse)
    return render(request, 'create.html', {'form': form})


def update_table(request):
    ads = Ad.objects.filter(user=request.user)
    # ads_and_forms = []
    # if request.method == 'POST':
    #    form = HorizontalForm(request.POST, instance=)
    #    if form.is_valid():
    #      form.save()
    #        return HttpResponseRedirect(reverse('render_dashboard'))
    #    print('Fucked up!')
    # for ad in ads:
    #    ads_and_forms.append((ad, HorizontalForm(instance=ad)))
    return render(request, 'table.html', {'ads': ads})



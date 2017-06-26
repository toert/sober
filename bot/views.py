from django.shortcuts import render
from django.urls import reverse
from django.http import HttpResponseRedirect, HttpResponseForbidden
from django.contrib.auth.decorators import login_required
from .forms import CreateBot, HmacForm, HorizontalForm
from .models import Ad, LocalUser
from django.views.decorators.csrf import csrf_exempt


@login_required
def render_dashboard(request):
    ads = list(Ad.objects.filter(user=request.user).order_by('id'))
    ads_and_forms = []
    #if request.method == 'POST':
    #    form = HorizontalForm(request.POST, instance=)
    #    if form.is_valid():
    #      form.save()
    #        return HttpResponseRedirect(reverse('render_dashboard'))
    #    print('Fucked up!')
    for ad in ads:
        ads_and_forms.append((ad, HorizontalForm(instance=ad)))
    return render(request, 'index.html', {'ads': ads_and_forms})


@login_required
def create_bot(request):
    if request.method == 'POST':
        form = CreateBot(request.POST)
        if form.is_valid():
            form.save_with_user(request.user)
            return HttpResponseRedirect(reverse('render_dashboard'))
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
    form = HmacForm(request.POST or None, instance=localuser_instanse)
    return render(request, 'create.html', {'form': form})


@login_required
@csrf_exempt
def edit_ad(request, bot_id):
    if request.method == 'POST':
        object = Ad.objects.get(id=bot_id)
        if object.user == request.user:
            form = HorizontalForm(request.POST or None, instance=object)
            print('Form:', form)
            if form.is_valid():
                form.save()
                return HttpResponseRedirect(reverse('render_dashboard'))
            else:
                print('Errors', form.errors)
                return HttpResponseRedirect(reverse('render_dashboard'))
            print('Fuck')
        print('Fuck2')
    print('Fuck3')


@login_required
def change_bot_from_vertical(request, bot_id):
    ad_instanse = Ad.objects.get(id=bot_id)
    if request.method == 'POST' and ad_instanse.user == request.user:
        form = CreateBot(request.POST or None, instance=ad_instanse)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse('render_dashboard'))

    if ad_instanse.user == request.user:
        form = CreateBot(request.POST or None, instance=ad_instanse)
        return render(request, 'create.html', {'form': form})
    else:
        return HttpResponseForbidden()



def update_table(request):
    ads = list(Ad.objects.filter(user=request.user).order_by('id'))
    ads_and_forms = []
    # if request.method == 'POST':
    #    form = HorizontalForm(request.POST, instance=)
    #    if form.is_valid():
    #      form.save()
    #        return HttpResponseRedirect(reverse('render_dashboard'))
    #    print('Fucked up!')
    for ad in ads:
        ads_and_forms.append((ad, HorizontalForm(instance=ad)))
    return render(request, 'table.html', {'ads': ads_and_forms})



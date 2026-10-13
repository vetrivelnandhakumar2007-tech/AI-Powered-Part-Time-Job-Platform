from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import redirect, render

from ai_assist import services as ai

from .forms import AIBusinessBlurbForm, OwnerProfileForm, SignUpForm, StudentProfileForm
from .models import OwnerProfile, StudentProfile, User


def signup(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.email = form.cleaned_data['email']
            user.phone = form.cleaned_data.get('phone', '')
            user.role = form.cleaned_data['role']
            user.save()

            if user.role == User.ROLE_STUDENT:
                StudentProfile.objects.create(user=user)
            else:
                OwnerProfile.objects.create(user=user, business_name=user.username)

            login(request, user)
            messages.success(request, "Welcome to Namma Ooru Jobs! Complete your profile to get started.")
            return redirect('accounts:edit_profile')
        else:
            return render(request, 'accounts/signup.html', {'form': form})
    return render(request, 'accounts/signup.html', {'form': SignUpForm()})


@login_required
def edit_profile(request):
    user = request.user
    if user.is_student():
        profile, _ = StudentProfile.objects.get_or_create(user=user)
        FormClass = StudentProfileForm
        template = 'accounts/edit_student_profile.html'
        tips = ai.profile_tips(profile) if request.method == 'GET' else []

        if request.method == 'POST':
            form = FormClass(request.POST, request.FILES, instance=profile)
            if form.is_valid():
                form.save()
                messages.success(request, "Profile updated.")
                return redirect('core:dashboard_redirect')
        else:
            form = FormClass(instance=profile)
        return render(request, template, {'form': form, 'tips': tips})

    # Owner
    profile, _ = OwnerProfile.objects.get_or_create(user=user, defaults={'business_name': user.username})
    ai_form = AIBusinessBlurbForm(prefix='ai')
    initial = {}

    if request.method == 'POST' and 'draft' in request.POST:
        ai_form = AIBusinessBlurbForm(request.POST, prefix='ai')
        if ai_form.is_valid():
            blurb = ai.generate_business_blurb(profile.business_name or user.username, ai_form.cleaned_data['notes'])
            initial = {'about': blurb}
            messages.info(request, "AI drafted a blurb below — feel free to tweak it.")
        form = OwnerProfileForm(instance=profile, initial=initial)
        return render(request, 'accounts/edit_owner_profile.html', {'form': form, 'ai_form': ai_form})

    if request.method == 'POST':
        form = OwnerProfileForm(request.POST, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, "Profile updated.")
            return redirect('core:dashboard_redirect')
    else:
        form = OwnerProfileForm(instance=profile)

    return render(request, 'accounts/edit_owner_profile.html', {'form': form, 'ai_form': ai_form})

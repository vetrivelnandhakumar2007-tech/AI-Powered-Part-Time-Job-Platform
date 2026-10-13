from django.contrib import messages
from django.db.models import Avg, Count, Q
from django.shortcuts import get_object_or_404, redirect, render

from accounts.models import OwnerProfile, StudentProfile, User
from applications.models import Application
from core.models import AboutFeature, HeroSlide, SiteSettings
from jobs.models import Job, JobCategory
from reviews.models import Review

from .decorators import admin_required
from .forms import (
    AboutFeatureForm, AdminApplicationForm, AdminCategoryForm, AdminJobForm,
    AdminUserForm, HeroSlideForm, SiteSettingsForm,
)


@admin_required
def dashboard(request):
    stats = {
        'total_users': User.objects.count(),
        'total_owners': User.objects.filter(role=User.ROLE_OWNER).count(),
        'total_students': User.objects.filter(role=User.ROLE_STUDENT).count(),
        'total_jobs': Job.objects.count(),
        'open_jobs': Job.objects.filter(status=Job.STATUS_OPEN).count(),
        'total_applications': Application.objects.count(),
        'pending_applications': Application.objects.filter(status=Application.STATUS_PENDING).count(),
        'total_reviews': Review.objects.count(),
        'avg_rating': Review.objects.aggregate(avg=Avg('rating'))['avg'],
    }
    recent_users = User.objects.order_by('-date_joined')[:5]
    recent_jobs = Job.objects.select_related('owner').order_by('-created_at')[:5]
    recent_applications = Application.objects.select_related('job', 'student').order_by('-applied_at')[:5]

    top_categories = (
        JobCategory.objects.annotate(job_count=Count('jobs')).order_by('-job_count')[:6]
    )
    max_cat_count = max([c.job_count for c in top_categories], default=0) or 1

    return render(request, 'adminpanel/dashboard.html', {
        'stats': stats, 'recent_users': recent_users, 'recent_jobs': recent_jobs,
        'recent_applications': recent_applications, 'top_categories': top_categories,
        'max_cat_count': max_cat_count,
    })


# ---------------------------------------------------------------------------
# Users
# ---------------------------------------------------------------------------

@admin_required
def user_list(request):
    users = User.objects.all().order_by('-date_joined')
    role = request.GET.get('role', '')
    q = request.GET.get('q', '')
    if role:
        users = users.filter(role=role)
    if q:
        users = users.filter(Q(username__icontains=q) | Q(email__icontains=q) | Q(first_name__icontains=q) | Q(last_name__icontains=q))
    return render(request, 'adminpanel/user_list.html', {'users': users, 'role': role, 'q': q})


@admin_required
def user_edit(request, pk):
    user = get_object_or_404(User, pk=pk)
    if request.method == 'POST':
        form = AdminUserForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            messages.success(request, f'Updated {user.username}.')
            return redirect('adminpanel:user_list')
    else:
        form = AdminUserForm(instance=user)
    return render(request, 'adminpanel/user_form.html', {'form': form, 'obj': user})


@admin_required
def user_delete(request, pk):
    user = get_object_or_404(User, pk=pk)
    if request.method == 'POST':
        username = user.username
        user.delete()
        messages.success(request, f'Deleted user {username}.')
        return redirect('adminpanel:user_list')
    return render(request, 'adminpanel/confirm_delete.html', {'obj': user, 'label': user.username, 'cancel_url': 'adminpanel:user_list'})


# ---------------------------------------------------------------------------
# Jobs
# ---------------------------------------------------------------------------

@admin_required
def job_list(request):
    jobs = Job.objects.select_related('owner', 'category').order_by('-created_at')
    status = request.GET.get('status', '')
    q = request.GET.get('q', '')
    if status:
        jobs = jobs.filter(status=status)
    if q:
        jobs = jobs.filter(Q(title__icontains=q) | Q(owner__username__icontains=q) | Q(location__icontains=q))
    return render(request, 'adminpanel/job_list.html', {'jobs': jobs, 'status': status, 'q': q})


@admin_required
def job_edit(request, pk):
    job = get_object_or_404(Job, pk=pk)
    if request.method == 'POST':
        form = AdminJobForm(request.POST, instance=job)
        if form.is_valid():
            form.save()
            messages.success(request, f'Updated "{job.title}".')
            return redirect('adminpanel:job_list')
    else:
        form = AdminJobForm(instance=job)
    return render(request, 'adminpanel/job_form.html', {'form': form, 'obj': job})


@admin_required
def job_delete(request, pk):
    job = get_object_or_404(Job, pk=pk)
    if request.method == 'POST':
        title = job.title
        job.delete()
        messages.success(request, f'Deleted job "{title}".')
        return redirect('adminpanel:job_list')
    return render(request, 'adminpanel/confirm_delete.html', {'obj': job, 'label': job.title, 'cancel_url': 'adminpanel:job_list'})


# ---------------------------------------------------------------------------
# Applications
# ---------------------------------------------------------------------------

@admin_required
def application_list(request):
    applications = Application.objects.select_related('job', 'student').order_by('-applied_at')
    status = request.GET.get('status', '')
    q = request.GET.get('q', '')
    if status:
        applications = applications.filter(status=status)
    if q:
        applications = applications.filter(Q(job__title__icontains=q) | Q(student__username__icontains=q))
    return render(request, 'adminpanel/application_list.html', {'applications': applications, 'status': status, 'q': q})


@admin_required
def application_edit(request, pk):
    application = get_object_or_404(Application, pk=pk)
    if request.method == 'POST':
        form = AdminApplicationForm(request.POST, instance=application)
        if form.is_valid():
            form.save()
            messages.success(request, 'Application updated.')
            return redirect('adminpanel:application_list')
    else:
        form = AdminApplicationForm(instance=application)
    return render(request, 'adminpanel/application_form.html', {'form': form, 'obj': application})


@admin_required
def application_delete(request, pk):
    application = get_object_or_404(Application, pk=pk)
    if request.method == 'POST':
        application.delete()
        messages.success(request, 'Application deleted.')
        return redirect('adminpanel:application_list')
    label = f"{application.student.username} → {application.job.title}"
    return render(request, 'adminpanel/confirm_delete.html', {'obj': application, 'label': label, 'cancel_url': 'adminpanel:application_list'})


# ---------------------------------------------------------------------------
# Categories
# ---------------------------------------------------------------------------

@admin_required
def category_list(request):
    categories = JobCategory.objects.annotate(job_count=Count('jobs')).order_by('name')
    return render(request, 'adminpanel/category_list.html', {'categories': categories})


@admin_required
def category_create(request):
    if request.method == 'POST':
        form = AdminCategoryForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Category created.')
            return redirect('adminpanel:category_list')
    else:
        form = AdminCategoryForm()
    return render(request, 'adminpanel/category_form.html', {'form': form, 'obj': None})


@admin_required
def category_edit(request, pk):
    category = get_object_or_404(JobCategory, pk=pk)
    if request.method == 'POST':
        form = AdminCategoryForm(request.POST, instance=category)
        if form.is_valid():
            form.save()
            messages.success(request, 'Category updated.')
            return redirect('adminpanel:category_list')
    else:
        form = AdminCategoryForm(instance=category)
    return render(request, 'adminpanel/category_form.html', {'form': form, 'obj': category})


@admin_required
def category_delete(request, pk):
    category = get_object_or_404(JobCategory, pk=pk)
    if request.method == 'POST':
        name = category.name
        category.delete()
        messages.success(request, f'Deleted category "{name}".')
        return redirect('adminpanel:category_list')
    return render(request, 'adminpanel/confirm_delete.html', {'obj': category, 'label': category.name, 'cancel_url': 'adminpanel:category_list'})


# ---------------------------------------------------------------------------
# Reviews
# ---------------------------------------------------------------------------

@admin_required
def review_list(request):
    reviews = Review.objects.select_related('job', 'from_user', 'to_user').order_by('-created_at')
    return render(request, 'adminpanel/review_list.html', {'reviews': reviews})


@admin_required
def review_delete(request, pk):
    review = get_object_or_404(Review, pk=pk)
    if request.method == 'POST':
        review.delete()
        messages.success(request, 'Review deleted.')
        return redirect('adminpanel:review_list')
    label = f"{review.from_user.username} → {review.to_user.username} ({review.rating}★)"
    return render(request, 'adminpanel/confirm_delete.html', {'obj': review, 'label': label, 'cancel_url': 'adminpanel:review_list'})


# ---------------------------------------------------------------------------
# Site Content — Site Settings, Hero Slides, About Features
# ---------------------------------------------------------------------------

@admin_required
def site_settings_edit(request):
    settings_obj = SiteSettings.get_solo()
    if request.method == 'POST':
        form = SiteSettingsForm(request.POST, instance=settings_obj)
        if form.is_valid():
            form.save()
            messages.success(request, 'Site settings updated.')
            return redirect('adminpanel:site_settings_edit')
    else:
        form = SiteSettingsForm(instance=settings_obj)
    return render(request, 'adminpanel/site_settings_form.html', {'form': form})


@admin_required
def hero_slide_list(request):
    slides = HeroSlide.objects.all()
    return render(request, 'adminpanel/hero_slide_list.html', {'slides': slides})


@admin_required
def hero_slide_create(request):
    if request.method == 'POST':
        form = HeroSlideForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Hero slide created.')
            return redirect('adminpanel:hero_slide_list')
    else:
        form = HeroSlideForm(initial={'order': HeroSlide.objects.count() + 1})
    return render(request, 'adminpanel/hero_slide_form.html', {'form': form, 'obj': None})


@admin_required
def hero_slide_edit(request, pk):
    slide = get_object_or_404(HeroSlide, pk=pk)
    if request.method == 'POST':
        form = HeroSlideForm(request.POST, request.FILES, instance=slide)
        if form.is_valid():
            form.save()
            messages.success(request, 'Hero slide updated.')
            return redirect('adminpanel:hero_slide_list')
    else:
        form = HeroSlideForm(instance=slide)
    return render(request, 'adminpanel/hero_slide_form.html', {'form': form, 'obj': slide})


@admin_required
def hero_slide_delete(request, pk):
    slide = get_object_or_404(HeroSlide, pk=pk)
    if request.method == 'POST':
        title = slide.title
        slide.delete()
        messages.success(request, f'Deleted hero slide "{title}".')
        return redirect('adminpanel:hero_slide_list')
    return render(request, 'adminpanel/confirm_delete.html', {'obj': slide, 'label': slide.title, 'cancel_url': 'adminpanel:hero_slide_list'})


@admin_required
def about_feature_list(request):
    features = AboutFeature.objects.all()
    return render(request, 'adminpanel/about_feature_list.html', {'features': features})


@admin_required
def about_feature_create(request):
    if request.method == 'POST':
        form = AboutFeatureForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'About feature created.')
            return redirect('adminpanel:about_feature_list')
    else:
        form = AboutFeatureForm(initial={'order': AboutFeature.objects.count() + 1})
    return render(request, 'adminpanel/about_feature_form.html', {'form': form, 'obj': None})


@admin_required
def about_feature_edit(request, pk):
    feature = get_object_or_404(AboutFeature, pk=pk)
    if request.method == 'POST':
        form = AboutFeatureForm(request.POST, instance=feature)
        if form.is_valid():
            form.save()
            messages.success(request, 'About feature updated.')
            return redirect('adminpanel:about_feature_list')
    else:
        form = AboutFeatureForm(instance=feature)
    return render(request, 'adminpanel/about_feature_form.html', {'form': form, 'obj': feature})


@admin_required
def about_feature_delete(request, pk):
    feature = get_object_or_404(AboutFeature, pk=pk)
    if request.method == 'POST':
        title = feature.title
        feature.delete()
        messages.success(request, f'Deleted feature "{title}".')
        return redirect('adminpanel:about_feature_list')
    return render(request, 'adminpanel/confirm_delete.html', {'obj': feature, 'label': feature.title, 'cancel_url': 'adminpanel:about_feature_list'})

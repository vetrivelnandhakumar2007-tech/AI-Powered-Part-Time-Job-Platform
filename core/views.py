from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render

from applications.models import Application
from jobs.models import Job

from .models import AboutFeature, HeroSlide


def home(request):
    if request.user.is_authenticated:
        return redirect('core:dashboard_redirect')
    recent_jobs = Job.objects.filter(status=Job.STATUS_OPEN)[:6]
    hero_slides = HeroSlide.objects.filter(is_active=True)
    return render(request, 'core/home.html', {'recent_jobs': recent_jobs, 'hero_slides': hero_slides})


def about(request):
    from accounts.models import User
    stats = {
        'owners': User.objects.filter(role=User.ROLE_OWNER).count(),
        'students': User.objects.filter(role=User.ROLE_STUDENT).count(),
        'jobs': Job.objects.count(),
    }
    features = AboutFeature.objects.filter(is_active=True)
    return render(request, 'core/about.html', {'stats': stats, 'features': features})


@login_required
def dashboard_redirect(request):
    if request.user.is_owner():
        return redirect('core:owner_dashboard')
    return redirect('core:student_dashboard')


@login_required
def owner_dashboard(request):
    jobs = Job.objects.filter(owner=request.user)
    open_jobs = jobs.filter(status=Job.STATUS_OPEN)
    pending_count = Application.objects.filter(job__owner=request.user, status=Application.STATUS_PENDING).count()
    return render(request, 'core/owner_dashboard.html', {
        'jobs': jobs, 'open_jobs': open_jobs, 'pending_count': pending_count,
    })


@login_required
def student_dashboard(request):
    applications = Application.objects.filter(student=request.user).select_related('job')
    from ai_assist import services as ai
    profile = getattr(request.user, 'student_profile', None)
    recommended = []
    if profile:
        open_jobs = list(Job.objects.filter(status=Job.STATUS_OPEN).exclude(
            applications__student=request.user
        ))
        recommended = ai.rank_jobs_for_student(open_jobs, profile)[:5]
    return render(request, 'core/student_dashboard.html', {
        'applications': applications, 'recommended': recommended,
    })

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from ai_assist import services as ai
from jobs.models import Job

from .forms import ApplicationForm
from .models import Application


@login_required
def apply_to_job(request, job_pk):
    job = get_object_or_404(Job, pk=job_pk, status=Job.STATUS_OPEN)
    if not request.user.is_student():
        messages.error(request, "Only students can apply to jobs.")
        return redirect('jobs:job_detail', pk=job_pk)

    if Application.objects.filter(job=job, student=request.user).exists():
        messages.info(request, "You already applied to this job.")
        return redirect('jobs:job_detail', pk=job_pk)

    if request.method == 'POST':
        form = ApplicationForm(request.POST)
        if form.is_valid():
            application = form.save(commit=False)
            application.job = job
            application.student = request.user
            profile = getattr(request.user, 'student_profile', None)

            # AI: score relevance and summarize the applicant for the owner.
            application.ai_match_score = ai.match_score(job, profile)
            application.ai_summary = ai.summarize_applicant(request.user, profile, application.message)

            application.save()
            messages.success(request, "Application submitted!")
            return redirect('applications:my_applications')
    else:
        form = ApplicationForm()

    return render(request, 'applications/apply_form.html', {'job': job, 'form': form})


@login_required
def my_applications(request):
    if not request.user.is_student():
        return redirect('jobs:job_list')
    applications = Application.objects.filter(student=request.user).select_related('job')
    return render(request, 'applications/my_applications.html', {'applications': applications})


@login_required
def job_applicants(request, job_pk):
    """Owner view: list applicants for one of their jobs, AI-ranked."""
    job = get_object_or_404(Job, pk=job_pk, owner=request.user)
    applicants = job.applications.select_related('student', 'student__student_profile')
    return render(request, 'applications/job_applicants.html', {'job': job, 'applicants': applicants})


@login_required
def update_application_status(request, pk, new_status):
    application = get_object_or_404(Application, pk=pk, job__owner=request.user)
    valid = dict(Application.STATUS_CHOICES)
    if new_status in valid:
        application.status = new_status
        application.save(update_fields=['status'])
        messages.success(request, f"Application marked as {valid[new_status]}.")
    return redirect('applications:job_applicants', job_pk=application.job_id)

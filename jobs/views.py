from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render

from ai_assist import services as ai
from applications.models import Application

from .forms import AIJobDraftForm, JobForm, JobSearchForm
from .models import Job, JobCategory


def job_list(request):
    """Browse/search jobs. Students get AI-ranked recommendations when no search is active."""
    form = JobSearchForm(request.GET or None)
    jobs = Job.objects.filter(status=Job.STATUS_OPEN)

    query_text = ''
    if form.is_valid():
        query_text = form.cleaned_data.get('q', '')
        category = form.cleaned_data.get('category')
        location = form.cleaned_data.get('location')

        if query_text:
            # Let AI turn a natural-language query into structured filters.
            parsed = ai.parse_search_query(query_text)
            if parsed.get('keywords'):
                kw_q = Q()
                for kw in parsed['keywords']:
                    kw_q |= Q(title__icontains=kw) | Q(description__icontains=kw) | Q(required_skills__icontains=kw)
                jobs = jobs.filter(kw_q)
            if parsed.get('location'):
                jobs = jobs.filter(location__icontains=parsed['location'])

        if category:
            jobs = jobs.filter(category=category)
        if location:
            jobs = jobs.filter(location__icontains=location)

    # AI-based recommendation ranking for logged-in students browsing without a search query.
    if request.user.is_authenticated and request.user.is_student() and not query_text:
        jobs = list(jobs)
        profile = getattr(request.user, 'student_profile', None)
        if profile:
            jobs = ai.rank_jobs_for_student(jobs, profile)
    else:
        jobs = list(jobs)

    paginator = Paginator(jobs, 10)
    page_obj = paginator.get_page(request.GET.get('page'))

    return render(request, 'jobs/job_list.html', {
        'form': form, 'page_obj': page_obj, 'query_text': query_text,
    })


def job_detail(request, pk):
    job = get_object_or_404(Job, pk=pk)
    already_applied = False
    if request.user.is_authenticated and request.user.is_student():
        already_applied = Application.objects.filter(job=job, student=request.user).exists()
    return render(request, 'jobs/job_detail.html', {'job': job, 'already_applied': already_applied})


@login_required
def job_create(request):
    if not request.user.is_owner():
        messages.error(request, "Only owners can post jobs.")
        return redirect('jobs:job_list')

    ai_form = AIJobDraftForm(prefix='ai')
    initial = {}

    if request.method == 'POST' and 'draft' in request.POST:
        ai_form = AIJobDraftForm(request.POST, prefix='ai')
        if ai_form.is_valid():
            draft = ai.enhance_job_posting(ai_form.cleaned_data['raw_idea'])
            initial = draft
            messages.info(request, "AI draft generated below — review and adjust before posting.")
        form = JobForm(initial=initial)
        return render(request, 'jobs/job_form.html', {'form': form, 'ai_form': ai_form})

    if request.method == 'POST':
        form = JobForm(request.POST)
        if form.is_valid():
            job = form.save(commit=False)
            job.owner = request.user
            job.ai_tags = ai.extract_tags(f"{job.title} {job.description} {job.required_skills}")
            job.save()
            messages.success(request, "Job posted.")
            return redirect('jobs:job_detail', pk=job.pk)
    else:
        form = JobForm(initial=initial)

    return render(request, 'jobs/job_form.html', {'form': form, 'ai_form': ai_form})


@login_required
def job_edit(request, pk):
    job = get_object_or_404(Job, pk=pk, owner=request.user)
    if request.method == 'POST':
        form = JobForm(request.POST, instance=job)
        if form.is_valid():
            form.save()
            messages.success(request, "Job updated.")
            return redirect('jobs:job_detail', pk=job.pk)
    else:
        form = JobForm(instance=job)
    return render(request, 'jobs/job_form.html', {'form': form, 'ai_form': AIJobDraftForm(prefix='ai'), 'editing': True})


@login_required
def job_close(request, pk):
    job = get_object_or_404(Job, pk=pk, owner=request.user)
    job.status = Job.STATUS_CLOSED
    job.save(update_fields=['status'])
    messages.success(request, f'"{job.title}" closed.')
    return redirect('jobs:my_jobs')


@login_required
def my_jobs(request):
    if not request.user.is_owner():
        return redirect('jobs:job_list')
    jobs = Job.objects.filter(owner=request.user)
    return render(request, 'jobs/my_jobs.html', {'jobs': jobs})

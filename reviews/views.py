from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from applications.models import Application
from jobs.models import Job

from .forms import ReviewForm
from .models import Review


@login_required
def leave_review(request, job_pk, to_user_pk):
    job = get_object_or_404(Job, pk=job_pk)
    to_user = get_object_or_404(job.owner.__class__, pk=to_user_pk)

    # Only participants of a completed application may review each other.
    involved = Application.objects.filter(
        job=job, status=Application.STATUS_COMPLETED
    ).filter(student=request.user) if request.user.is_student() else Application.objects.filter(
        job=job, status=Application.STATUS_COMPLETED, job__owner=request.user
    )
    if not involved.exists():
        messages.error(request, "You can only review after a completed job.")
        return redirect('jobs:job_detail', pk=job_pk)

    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            review, _ = Review.objects.update_or_create(
                job=job, from_user=request.user, to_user=to_user,
                defaults={'rating': form.cleaned_data['rating'], 'comment': form.cleaned_data['comment']},
            )
            messages.success(request, "Review submitted.")
            return redirect('jobs:job_detail', pk=job_pk)
    else:
        form = ReviewForm()

    return render(request, 'reviews/review_form.html', {'form': form, 'job': job, 'to_user': to_user})

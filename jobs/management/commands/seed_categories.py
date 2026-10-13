from django.core.management.base import BaseCommand

from jobs.models import JobCategory

DEFAULT_CATEGORIES = [
    "Retail & Shop Help", "Tutoring", "Event Support", "Delivery",
    "Data Entry", "Customer Service", "Cafe & Restaurant", "Freelance / Gig",
]


class Command(BaseCommand):
    help = "Seed default job categories."

    def handle(self, *args, **options):
        created = 0
        for name in DEFAULT_CATEGORIES:
            _, was_created = JobCategory.objects.get_or_create(name=name)
            created += int(was_created)
        self.stdout.write(self.style.SUCCESS(f"Seeded categories ({created} new)."))

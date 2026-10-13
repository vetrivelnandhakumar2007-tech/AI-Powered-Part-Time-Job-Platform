from django.core.management.base import BaseCommand

from core.models import AboutFeature, HeroSlide, SiteSettings

DEFAULT_SLIDES = [
    ("retail", "Retail & Shop Help", "Local shops need weekend hands on deck.",
     "Owners post shift work in minutes. Students pick up hours that fit around class.", 1),
    ("tutoring", "Tutoring & Academic Support", "Turn what you're good at into weekly income.",
     "AI matches your strongest subjects to students and owners looking for tutors nearby.", 2),
    ("events", "Event Support", "Campus events run on last-minute hands.",
     "Post a one-day gig or find one — no long applications, just a quick match.", 3),
    ("delivery", "Delivery & Logistics", "Flexible hours, close to where you already are.",
     "Set your availability once — AI keeps surfacing jobs that actually fit it.", 4),
]

DEFAULT_FEATURES = [
    ("✨", "AI that does the writing", "Owners type a rough idea and AI drafts a clean, structured job listing — title, description, and a fair pay suggestion — in seconds.", 1),
    ("🎯", "Matching that actually fits", "Every job is scored against a student's skills and availability, with a plain-language reason — not just a ranked list, an explanation.", 2),
    ("⚡", "Faster hiring decisions", "Owners see an AI-written one-line summary of every applicant, so reviewing a stack of applications takes minutes, not hours.", 3),
]


class Command(BaseCommand):
    help = "Seed default site settings, hero banner slides, and about-page features (idempotent)."

    def handle(self, *args, **options):
        SiteSettings.get_solo()

        created_slides = 0
        for theme, eyebrow, title, subtitle, order in DEFAULT_SLIDES:
            _, created = HeroSlide.objects.get_or_create(
                title=title,
                defaults={"theme": theme, "eyebrow": eyebrow, "subtitle": subtitle, "order": order},
            )
            created_slides += int(created)

        created_features = 0
        for icon, title, desc, order in DEFAULT_FEATURES:
            _, created = AboutFeature.objects.get_or_create(
                title=title,
                defaults={"icon": icon, "description": desc, "order": order},
            )
            created_features += int(created)

        self.stdout.write(self.style.SUCCESS(
            f"Site settings ready. Seeded {created_slides} new hero slides and {created_features} new about features."
        ))

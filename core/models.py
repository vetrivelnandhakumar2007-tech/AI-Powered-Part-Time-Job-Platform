from django.db import models


class SiteSettings(models.Model):
    """Singleton row holding site-wide, admin-editable text and contact info."""

    site_name = models.CharField(max_length=60, default="Namma Ooru Jobs")
    tagline = models.CharField(
        max_length=160,
        default="Part-time jobs, matched by AI.",
        help_text="Short line shown under the site name in a few places.",
    )
    footer_about_text = models.TextField(
        default="Connecting local owners and students for flexible part-time work — with AI doing the matching, drafting, and summarizing along the way."
    )
    support_email = models.EmailField(blank=True, default="support@example.com")
    support_phone = models.CharField(max_length=20, blank=True)

    about_mission_title = models.CharField(
        max_length=160, default="Making part-time work easy to find, and easy to fill."
    )
    about_mission_text = models.TextField(
        default="Namma Ooru Jobs connects local shop owners, tutoring centres, event organizers, and small businesses with students who want flexible, part-time work — with AI doing the busywork of drafting, matching, and screening on both sides."
    )
    about_college_heading = models.CharField(max_length=160, default="Built at Sacred Heart College")
    about_college_text = models.TextField(
        default="Namma Ooru Jobs is a student project from the Department of Artificial Intelligence and Machine Learning, Sacred Heart College (Autonomous), Tirupattur — built to solve a problem students and local businesses run into every semester: finding each other."
    )

    class Meta:
        verbose_name = "Site Settings"
        verbose_name_plural = "Site Settings"

    def __str__(self):
        return self.site_name

    @classmethod
    def get_solo(cls):
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj

    @property
    def name_prefix(self):
        parts = self.site_name.strip().split(" ")
        return " ".join(parts[:-1])

    @property
    def name_last_word(self):
        parts = self.site_name.strip().split(" ")
        return parts[-1] if parts else self.site_name


class HeroSlide(models.Model):
    """One rotating slide on the home page banner — fully admin-editable."""

    THEME_CHOICES = [
        ("retail", "Amber (Retail)"),
        ("tutoring", "Emerald (Tutoring)"),
        ("events", "Coral (Events)"),
        ("delivery", "Blue (Delivery)"),
    ]

    eyebrow = models.CharField(max_length=60, help_text="Small label above the headline, e.g. 'Retail & Shop Help'.")
    title = models.CharField(max_length=140)
    subtitle = models.CharField(max_length=220)
    theme = models.CharField(max_length=10, choices=THEME_CHOICES, default="retail")
    image = models.ImageField(upload_to="hero_slides/", blank=True, null=True, help_text="Optional — leave blank to use the built-in illustration for the theme.")
    order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["order", "id"]

    def __str__(self):
        return self.title

    def default_image_url(self):
        return f"img/hero-{self.theme}.svg"


class AboutFeature(models.Model):
    """One 'why choose us' card on the About page — fully admin-editable."""

    icon = models.CharField(max_length=8, default="✨", help_text="A single emoji, e.g. ✨ 🎯 ⚡")
    title = models.CharField(max_length=100)
    description = models.CharField(max_length=240)
    order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["order", "id"]

    def __str__(self):
        return self.title

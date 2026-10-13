"""
Seed the database with demo data: 10 owners, 10 students, and 15 jobs.

Usage:
    python3 manage.py seed_demo

Safe to re-run — uses get_or_create keyed on username/title so it won't
duplicate data on a second run.
"""
import random
from datetime import timedelta

from django.core.management import call_command
from django.core.management.base import BaseCommand
from django.utils import timezone

from accounts.models import OwnerProfile, StudentProfile, User
from applications.models import Application
from jobs.models import Job, JobCategory

DEMO_PASSWORD = "demo1234"

CATEGORY_NAMES = [
    "Retail & Shop Help", "Tutoring", "Event Support", "Delivery",
    "Data Entry", "Customer Service", "Cafe & Restaurant", "Freelance / Gig",
]

LOCATIONS = [
    "Tirupattur", "Vaniyambadi", "Ambur", "Vellore", "Gudiyattam", "Jolarpet",
]

OWNERS = [
    ("rajesh_stationery", "Rajesh Stationery Mart", "Sells stationery, books, and printing supplies near the college gate; open evenings."),
    ("anitha_tuitions", "Anitha's Tuition Centre", "After-school tuition centre for school students, looking for subject helpers."),
    ("campus_cafe", "Campus Corner Cafe", "Cosy cafe near campus serving snacks and coffee; busiest during evenings and weekends."),
    ("swift_deliveries", "Swift Local Deliveries", "Small courier service handling same-day parcel and food deliveries around town."),
    ("greenleaf_super", "Greenleaf Supermarket", "Neighbourhood supermarket needing billing and shelf-stocking support."),
    ("eventpro_tn", "EventPro Tamil Nadu", "Organizes college fests, weddings, and corporate events; needs on-ground crew."),
    ("bytewise_solutions", "Bytewise Solutions", "Small IT services firm needing help with data entry and basic office work."),
    ("spice_route", "Spice Route Restaurant", "Family restaurant looking for weekend waitstaff and kitchen helpers."),
    ("trendy_threads", "Trendy Threads Boutique", "Clothing boutique needing sales help during festival season."),
    ("quickfix_electronics", "QuickFix Electronics", "Mobile and electronics repair shop needing a front-desk assistant."),
]

STUDENTS = [
    ("arun_kumar", "Arun Kumar", "B.Sc. AI & ML", "2nd year", "communication, billing, ms office", "weekends"),
    ("divya_s", "Divya S", "B.Com", "3rd year", "tutoring, mathematics, patience", "evenings, weekends"),
    ("karthik_r", "Karthik R", "BCA", "1st year", "data entry, excel, typing", "weekday evenings"),
    ("priya_v", "Priya V", "B.Sc. AI & ML", "3rd year", "customer service, communication, billing", "weekends"),
    ("suresh_m", "Suresh M", "B.E. Mechanical", "2nd year", "delivery, driving, punctuality", "weekday mornings"),
    ("lakshmi_n", "Lakshmi N", "B.A. English", "4th year", "tutoring, english, communication", "evenings"),
    ("vignesh_t", "Vignesh T", "BBA", "2nd year", "event support, teamwork, event planning", "weekends"),
    ("meena_k", "Meena K", "B.Sc. AI & ML", "1st year", "data entry, excel, ms office", "weekday evenings"),
    ("harish_p", "Harish P", "B.Com", "3rd year", "billing, customer service, communication", "weekends"),
    ("swathi_j", "Swathi J", "BCA", "2nd year", "excel, data entry, communication", "evenings, weekends"),
]

JOB_TEMPLATES = [
    ("rajesh_stationery", "Retail & Shop Help", "Weekend Counter Assistant", "Help customers at the counter, handle billing, and restock shelves on weekends.", "communication, billing", 150, "hourly", 2, 10),
    ("rajesh_stationery", "Data Entry", "Evening Stock Entry Helper", "Update stock records and print job entries into our system on weekday evenings.", "data entry, excel", 130, "hourly", 1, 7),
    ("anitha_tuitions", "Tutoring", "Maths Tutor for 8th–10th Grade", "Teach maths to small groups of school students 3 evenings a week.", "tutoring, mathematics", 200, "hourly", 2, 14),
    ("anitha_tuitions", "Tutoring", "English Tutor (Weekends)", "Help school students with spoken and written English on weekend mornings.", "tutoring, english, communication", 180, "hourly", 1, 14),
    ("campus_cafe", "Cafe & Restaurant", "Weekend Barista Helper", "Assist with making beverages and serving customers during busy weekend hours.", "customer service, communication", 140, "hourly", 2, 9),
    ("swift_deliveries", "Delivery", "Evening Delivery Rider", "Deliver parcels and food orders within a 5km radius on weekday evenings.", "delivery, driving, punctuality", 160, "hourly", 3, 12),
    ("greenleaf_super", "Retail & Shop Help", "Billing Counter Assistant", "Operate the billing counter and assist customers during weekend rush hours.", "billing, communication", 150, "hourly", 2, 10),
    ("greenleaf_super", "Retail & Shop Help", "Shelf Stocking Helper", "Restock shelves and organize inventory early mornings, 3 days a week.", "customer service, punctuality", 130, "hourly", 2, 8),
    ("eventpro_tn", "Event Support", "Event Day Crew", "On-ground support for a college fest — setup, registration desk, and crowd guidance.", "event support, teamwork", 500, "fixed", 5, 6),
    ("eventpro_tn", "Event Support", "Weekend Wedding Crew", "Assist with guest coordination and setup at a weekend wedding event.", "event support, communication", 600, "fixed", 4, 11),
    ("bytewise_solutions", "Data Entry", "Office Data Entry Assistant", "Enter and organize client data into spreadsheets, flexible weekday hours.", "data entry, excel, ms office", 140, "hourly", 1, 13),
    ("spice_route", "Cafe & Restaurant", "Weekend Waitstaff", "Take orders and serve tables during busy weekend dinner hours.", "customer service, communication", 150, "hourly", 2, 9),
    ("trendy_threads", "Retail & Shop Help", "Festival Season Sales Help", "Assist customers and manage billing during the festival sale rush.", "customer service, billing", 160, "hourly", 2, 15),
    ("quickfix_electronics", "Customer Service", "Front Desk Assistant", "Greet customers, log repair requests, and manage the front desk in the evenings.", "customer service, ms office", 140, "hourly", 1, 10),
    ("quickfix_electronics", "Freelance / Gig", "Weekend Inventory Helper", "One-day inventory count and organizing of spare parts stock.", "data entry, punctuality", 400, "fixed", 1, 5),
]


class Command(BaseCommand):
    help = "Seed demo data: 10 owners, 10 students, and 15 jobs."

    def handle(self, *args, **options):
        call_command('seed_site_content')
        random.seed(42)

        categories = {}
        for name in CATEGORY_NAMES:
            cat, _ = JobCategory.objects.get_or_create(name=name)
            categories[name] = cat

        owner_users = []
        for i, (username, business_name, about) in enumerate(OWNERS):
            user, created = User.objects.get_or_create(
                username=username,
                defaults={
                    "email": f"{username}@example.com",
                    "role": User.ROLE_OWNER,
                    "phone": f"90000000{i:02d}",
                },
            )
            if created:
                user.set_password(DEMO_PASSWORD)
                user.save()
            OwnerProfile.objects.get_or_create(
                user=user,
                defaults={
                    "business_name": business_name,
                    "location": random.choice(LOCATIONS),
                    "contact_info": f"{business_name} · {user.phone}",
                    "about": about,
                },
            )
            owner_users.append(user)

        student_users = []
        for i, (username, full_name, college, year, skills, availability) in enumerate(STUDENTS):
            first, _, last = full_name.partition(" ")
            user, created = User.objects.get_or_create(
                username=username,
                defaults={
                    "email": f"{username}@example.com",
                    "role": User.ROLE_STUDENT,
                    "phone": f"80000000{i:02d}",
                    "first_name": first,
                    "last_name": last,
                },
            )
            if created:
                user.set_password(DEMO_PASSWORD)
                user.save()
            StudentProfile.objects.get_or_create(
                user=user,
                defaults={
                    "college": college,
                    "year_of_study": year,
                    "skills": skills,
                    "availability": availability,
                    "bio": f"{year} {college} student looking for flexible part-time work.",
                },
            )
            student_users.append(user)

        owners_by_username = {u.username: u for u in owner_users}
        jobs_created = []
        for (owner_username, cat_name, title, desc, skills, pay, pay_type, openings, days_out) in JOB_TEMPLATES:
            owner = owners_by_username[owner_username]
            job, created = Job.objects.get_or_create(
                owner=owner,
                title=title,
                defaults={
                    "description": desc,
                    "category": categories[cat_name],
                    "pay_rate": pay,
                    "pay_type": pay_type,
                    "location": owner.owner_profile.location,
                    "openings": openings,
                    "deadline": timezone.now().date() + timedelta(days=days_out),
                    "required_skills": skills,
                    "status": Job.STATUS_OPEN,
                },
            )
            jobs_created.append(job)

        # A handful of sample applications so dashboards aren't empty.
        sample_pairs = [
            (student_users[0], jobs_created[0], Application.STATUS_PENDING),
            (student_users[1], jobs_created[2], Application.STATUS_ACCEPTED),
            (student_users[3], jobs_created[6], Application.STATUS_PENDING),
            (student_users[5], jobs_created[3], Application.STATUS_COMPLETED),
            (student_users[7], jobs_created[10], Application.STATUS_PENDING),
        ]
        for student, job, status in sample_pairs:
            Application.objects.get_or_create(
                job=job, student=student,
                defaults={"status": status, "message": "Interested and available as per the listed timing."},
            )

        self.stdout.write(self.style.SUCCESS(
            f"Seeded {len(owner_users)} owners, {len(student_users)} students, "
            f"{len(jobs_created)} jobs, and {len(sample_pairs)} sample applications."
        ))
        self.stdout.write(f"All demo accounts use the password: {DEMO_PASSWORD}")
        self.stdout.write("Owner usernames: " + ", ".join(u.username for u in owner_users))
        self.stdout.write("Student usernames: " + ", ".join(u.username for u in student_users))

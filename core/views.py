from django.conf import settings
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.core.files.storage import FileSystemStorage
from django.db import connection, transaction
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone
from django.views.decorators.http import require_POST

from .forms import (
    AppUserForm,
    CaregiverRegistrationForm,
    EmailAuthenticationForm,
    JobForm,
    MemberRegistrationForm,
)
from .models import Address, AppUser, Caregiver, Job, Member


def home(request):
    return render(request, "index.html")


def login_view(request):
    form = EmailAuthenticationForm(request, data=request.POST or None)
    if request.method == "POST" and form.is_valid():
        user = authenticate(
            request, username=form.cleaned_data["username"], password=form.cleaned_data["password"]
        )
        if user:
            login(request, user)
            return redirect(reverse("home"))
        messages.error(request, "Invalid credentials.")
    return render(request, "auth/login.html", {"form": form})


def logout_view(request):
    logout(request)
    return redirect(reverse("home"))


def users(request):
    # legacy admin view
    users_qs = AppUser.objects.order_by("user_id")

    if request.method == "POST":
        _sync_user_id_sequence()
        form = AppUserForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect(reverse("users"))
    else:
        form = AppUserForm()

    return render(request, "users.html", {"users": users_qs, "form": form})


def register_caregiver(request):
    form = CaregiverRegistrationForm(request.POST or None, request.FILES or None)
    if request.method == "POST" and form.is_valid():
        with transaction.atomic():
            from django.contrib.auth import get_user_model
            from django.contrib.auth.hashers import make_password

            _sync_user_id_sequence()
            password_raw = form.cleaned_data["password1"]
            hashed_pw = make_password(password_raw)
            app_user = AppUser.objects.create(
                email=form.cleaned_data["email"],
                given_name=form.cleaned_data["given_name"],
                surname=form.cleaned_data["surname"],
                city=form.cleaned_data["city"],
                phone_number=form.cleaned_data.get("phone_number") or "",
                profile_description=form.cleaned_data.get("profile_description") or "",
                password=hashed_pw,
            )
            User = get_user_model()
            user = User.objects.create(
                username=app_user.email,
                email=app_user.email,
                first_name=app_user.given_name,
                last_name=app_user.surname,
                password=hashed_pw,
            )
            photo_url = ""
            upload = request.FILES.get("photo")
            if upload:
                storage = FileSystemStorage(
                    location=settings.MEDIA_ROOT,
                    base_url=settings.MEDIA_URL,
                )
                saved_path = storage.save(f"caregiver_photos/{upload.name}", upload)
                photo_url = storage.url(saved_path)
            Caregiver.objects.create(
                caregiver_user=app_user,
                caregiving_type=form.cleaned_data["caregiving_type"],
                gender=form.cleaned_data.get("gender") or "",
                hourly_rate=form.cleaned_data["hourly_rate"],
                photo=photo_url,
            )
        user.backend = "core.auth_backends.AppUserBackend"
        login(request, user)
        messages.success(request, "Caregiver account created.")
        return redirect(reverse("jobs_list"))

    return render(request, "auth/register_caregiver.html", {"form": form})


def register_member(request):
    form = MemberRegistrationForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        with transaction.atomic():
            from django.contrib.auth import get_user_model
            from django.contrib.auth.hashers import make_password

            _sync_user_id_sequence()
            password_raw = form.cleaned_data["password1"]
            hashed_pw = make_password(password_raw)
            app_user = AppUser.objects.create(
                email=form.cleaned_data["email"],
                given_name=form.cleaned_data["given_name"],
                surname=form.cleaned_data["surname"],
                city=form.cleaned_data["city"],
                phone_number=form.cleaned_data.get("phone_number") or "",
                password=hashed_pw,
            )
            User = get_user_model()
            user = User.objects.create(
                username=app_user.email,
                email=app_user.email,
                first_name=app_user.given_name,
                last_name=app_user.surname,
                password=hashed_pw,
            )

            member = Member.objects.create(
                member_user=app_user,
                house_rules=form.cleaned_data.get("house_rules") or "",
                dependent_description=form.cleaned_data.get("dependent_description") or "",
            )
            Address.objects.create(
                member=member,
                house_number=form.cleaned_data.get("house_number") or "",
                street=form.cleaned_data.get("street") or "",
                town=form.cleaned_data.get("town") or "",
            )
        user.backend = "core.auth_backends.AppUserBackend"
        login(request, user)
        messages.success(request, "Member account created.")
        return redirect(reverse("member_jobs"))

    return render(request, "auth/register_member.html", {"form": form})


def search_caregivers(request):
    caregiving_type = request.GET.get("caregiving_type") or ""
    city = request.GET.get("city") or ""
    caregivers = Caregiver.objects.select_related("caregiver_user")
    if caregiving_type:
        caregivers = caregivers.filter(caregiving_type=caregiving_type)
    if city:
        caregivers = caregivers.filter(caregiver_user__city__icontains=city)
    return render(
        request,
        "search.html",
        {"caregivers": caregivers, "selected_type": caregiving_type, "city": city},
    )


@login_required
def member_jobs(request):
    member = _get_member_for_request(request)
    if not member:
        messages.error(request, "Member profile required to manage jobs.")
        return redirect(reverse("home"))

    form = JobForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        _sync_job_id_sequence()
        Job.objects.create(
            member=member,
            required_caregiving_type=form.cleaned_data["required_caregiving_type"],
            other_requirements=form.cleaned_data.get("other_requirements") or "",
            date_posted=timezone.now().date(),
        )
        messages.success(request, "Job posted.")
        return redirect(reverse("member_jobs"))

    jobs = Job.objects.filter(member=member).order_by("-date_posted", "-job_id")
    applicants_by_job = _fetch_applicants_for_jobs(jobs)
    for job in jobs:
        job.applicants = applicants_by_job.get(job.job_id, [])
    return render(
        request,
        "member_jobs.html",
        {"form": form, "jobs": jobs},
    )


@login_required
def jobs_list(request):
    caregiving_type = request.GET.get("caregiving_type") or ""
    jobs = Job.objects.select_related("member__member_user")
    if caregiving_type:
        jobs = jobs.filter(required_caregiving_type=caregiving_type)
    jobs = jobs.order_by("-date_posted", "-job_id")

    caregiver = _get_caregiver_for_request(request)
    applied_job_ids = set()
    if caregiver:
        applied_job_ids = _fetch_applied_job_ids(caregiver.caregiver_user_id)

    return render(
        request,
        "jobs_list.html",
        {
            "jobs": jobs,
            "caregiving_type": caregiving_type,
            "caregiver": caregiver,
            "applied_job_ids": applied_job_ids,
        },
    )


@login_required
@require_POST
def apply_job(request, job_id):
    job = get_object_or_404(Job, pk=job_id)
    caregiver = _get_caregiver_for_request(request)
    if not caregiver:
        messages.error(request, "Only caregivers can apply to jobs.")
        return redirect(reverse("jobs_list"))

    with connection.cursor() as cursor:
        cursor.execute(
            "SELECT 1 FROM job_applications WHERE caregiver_user_id=%s AND job_id=%s",
            [caregiver.caregiver_user_id, job_id],
        )
        exists = cursor.fetchone()
        if exists:
            messages.info(request, "You already applied to this job.")
        else:
            cursor.execute(
                "INSERT INTO job_applications (caregiver_user_id, job_id, date_applied) "
                "VALUES (%s, %s, CURRENT_DATE)",
                [caregiver.caregiver_user_id, job_id],
            )
            messages.success(request, "Application submitted.")
    return redirect(reverse("jobs_list"))


@require_POST
def delete_user(request, pk):
    user = get_object_or_404(AppUser, pk=pk)
    user.delete()
    return redirect(reverse("users"))


def _get_member_for_request(request):
    if not request.user.is_authenticated:
        return None
    try:
        app_user = AppUser.objects.get(email=request.user.username)
        return app_user.member_profile
    except (AppUser.DoesNotExist, Member.DoesNotExist):
        return None


def _get_caregiver_for_request(request):
    if not request.user.is_authenticated:
        return None
    try:
        app_user = AppUser.objects.get(email=request.user.username)
        return app_user.caregiver_profile
    except (AppUser.DoesNotExist, Caregiver.DoesNotExist):
        return None


def _fetch_applied_job_ids(caregiver_user_id):
    with connection.cursor() as cursor:
        cursor.execute(
            "SELECT job_id FROM job_applications WHERE caregiver_user_id=%s",
            [caregiver_user_id],
        )
        return {row[0] for row in cursor.fetchall()}


def _fetch_applicants_for_jobs(jobs):
    if not jobs:
        return {}
    job_ids = [job.job_id for job in jobs]
    placeholders = ",".join(["%s"] * len(job_ids))
    sql = f"""
        SELECT ja.job_id, u.given_name, u.surname, u.email, u.phone_number, c.caregiving_type
        FROM job_applications ja
        JOIN caregivers c ON c.caregiver_user_id = ja.caregiver_user_id
        JOIN users u ON u.user_id = c.caregiver_user_id
        WHERE ja.job_id IN ({placeholders})
    """
    by_job = {job_id: [] for job_id in job_ids}
    with connection.cursor() as cursor:
        cursor.execute(sql, job_ids)
        for job_id, given, surname, email, phone, caregiving_type in cursor.fetchall():
            by_job[job_id].append(
                {
                    "name": f"{given} {surname}",
                    "email": email,
                    "phone": phone,
                    "caregiving_type": caregiving_type,
                }
            )
    return by_job


def _sync_user_id_sequence():
    with connection.cursor() as cursor:
        cursor.execute(
            "SELECT setval(pg_get_serial_sequence('users', 'user_id'), "
            "(SELECT COALESCE(MAX(user_id), 0) FROM users));"
        )


def _sync_job_id_sequence():
    with connection.cursor() as cursor:
        cursor.execute(
            "SELECT setval(pg_get_serial_sequence('jobs', 'job_id'), "
            "(SELECT COALESCE(MAX(job_id), 0) FROM jobs));"
        )

from django.http import HttpResponse
from pathlib import Path
import subprocess
import sys

def run_populate(request):
    """
    TEMPORARY: run populate.py on the server to seed the Render Postgres DB.
    Call this URL once, then remove it from urls.py.
    """
    project_root = Path(__file__).resolve().parent.parent
    script_path = project_root / "populate.py"

    result = subprocess.run(
        [sys.executable, str(script_path)],
        capture_output=True,
        text=True,
    )

    output = (
        f"Return code: {result.returncode}\n\n"
        f"--- STDOUT ---\n{result.stdout}\n"
        f"--- STDERR ---\n{result.stderr}\n"
    )
    return HttpResponse(f"<pre>{output}</pre>")

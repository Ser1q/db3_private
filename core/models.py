from django.db import models


class AppUser(models.Model):
    """
    Maps to the `users` table.
    """
    user_id = models.AutoField(primary_key=True, db_column="user_id")
    email = models.EmailField(max_length=100, unique=True)
    given_name = models.CharField(max_length=50)
    surname = models.CharField(max_length=50)
    city = models.CharField(max_length=50)
    phone_number = models.CharField(max_length=20, null=True, blank=True)
    profile_description = models.TextField(null=True, blank=True)
    password = models.CharField(max_length=100)

    class Meta:
        managed = False  # table already exists; Django should not create/alter it
        db_table = "users"
        ordering = ["user_id"]

    def __str__(self):
        return f"{self.given_name} {self.surname}"


class Caregiver(models.Model):
    """
    Maps to `caregivers` (PK + FK to users.user_id).
    """
    caregiver_user = models.OneToOneField(
        AppUser,
        on_delete=models.CASCADE,
        db_column="caregiver_user_id",
        primary_key=True,
        related_name="caregiver_profile",
    )
    photo = models.CharField(max_length=255, null=True, blank=True)
    gender = models.CharField(max_length=10, null=True, blank=True)
    caregiving_type = models.CharField(max_length=50)
    hourly_rate = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
    )

    class Meta:
        managed = False
        db_table = "caregivers"

    def __str__(self):
        return f"Caregiver {self.caregiver_user}"


class Member(models.Model):
    """
    Maps to `members` (PK + FK to users.user_id).
    """
    member_user = models.OneToOneField(
        AppUser,
        on_delete=models.CASCADE,
        db_column="member_user_id",
        primary_key=True,
        related_name="member_profile",
    )
    house_rules = models.TextField(null=True, blank=True)
    dependent_description = models.TextField(null=True, blank=True)

    class Meta:
        managed = False
        db_table = "members"

    def __str__(self):
        return f"Member {self.member_user}"


class Address(models.Model):
    """
    Maps to `addresses` (1–1 with Member via member_user_id).
    """
    member = models.OneToOneField(
        Member,
        on_delete=models.CASCADE,
        db_column="member_user_id",
        primary_key=True,
        related_name="address",
    )
    house_number = models.CharField(max_length=20, null=True, blank=True)
    street = models.CharField(max_length=100, null=True, blank=True)
    town = models.CharField(max_length=50, null=True, blank=True)

    class Meta:
        managed = False
        db_table = "addresses"

    def __str__(self):
        if self.street:
            return f"{self.street}, {self.town}"
        return "Address"


class Job(models.Model):
    """
    Maps to `jobs`.
    """
    job_id = models.AutoField(primary_key=True, db_column="job_id")
    member = models.ForeignKey(
        Member,
        on_delete=models.CASCADE,
        db_column="member_user_id",
        related_name="jobs",
    )
    required_caregiving_type = models.CharField(max_length=50)
    other_requirements = models.TextField(null=True, blank=True)
    # DB has DEFAULT CURRENT_DATE; Django won't manage the table,
    # so we keep a plain DateField that reflects the column.
    date_posted = models.DateField(db_column="date_posted")

    class Meta:
        managed = False
        db_table = "jobs"
        ordering = ["-date_posted", "-job_id"]

    def __str__(self):
        return f"Job {self.job_id} ({self.required_caregiving_type})"


class JobApplication(models.Model):
    """
    Maps to `job_applications`.

    DB PK is (caregiver_user_id, job_id).
    Django needs *some* pk column; since the table is managed externally,
    we map pk to job (works fine for queries; DB still enforces composite PK).
    """
    caregiver = models.ForeignKey(
        Caregiver,
        on_delete=models.CASCADE,
        db_column="caregiver_user_id",
        related_name="job_applications",
    )
    job = models.ForeignKey(
        Job,
        on_delete=models.CASCADE,
        db_column="job_id",
        related_name="applications",
        primary_key=True,  # Django's view of the PK (DB has composite PK)
    )
    date_applied = models.DateField(db_column="date_applied")

    class Meta:
        managed = False
        db_table = "job_applications"
        # Reflect composite uniqueness at the ORM level
        unique_together = ("caregiver", "job")

    def __str__(self):
        return f"Application: caregiver={self.caregiver_id}, job={self.job_id}"


class Appointment(models.Model):
    """
    Maps to `appointments`.
    """
    appointment_id = models.AutoField(
        primary_key=True,
        db_column="appointment_id",
    )
    caregiver = models.ForeignKey(
        Caregiver,
        on_delete=models.CASCADE,
        db_column="caregiver_user_id",
        related_name="appointments",
    )
    member = models.ForeignKey(
        Member,
        on_delete=models.CASCADE,
        db_column="member_user_id",
        related_name="appointments",
    )
    appointment_date = models.DateField(db_column="appointment_date")
    appointment_time = models.TimeField(db_column="appointment_time")
    work_hours = models.IntegerField(null=True, blank=True)
    status = models.CharField(max_length=20, default="Pending")

    class Meta:
        managed = False
        db_table = "appointments"
        ordering = ["-appointment_date", "-appointment_time"]

    def __str__(self):
        return f"Appt {self.appointment_id} {self.appointment_date}"

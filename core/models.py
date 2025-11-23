from django.db import models


class AppUser(models.Model):
    user_id = models.AutoField(primary_key=True, db_column="user_id")
    email = models.EmailField(max_length=100, unique=True)
    given_name = models.CharField(max_length=50)
    surname = models.CharField(max_length=50)
    city = models.CharField(max_length=50)
    phone_number = models.CharField(max_length=20, null=True, blank=True)
    profile_description = models.TextField(null=True, blank=True)
    password = models.CharField(max_length=100)

    class Meta:
        managed = False  # Use existing table; Django won't manage migrations
        db_table = "users"
        ordering = ["user_id"]

    def __str__(self):
        return f"{self.given_name} {self.surname}"


class Caregiver(models.Model):
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
    hourly_rate = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    class Meta:
        managed = False
        db_table = "caregivers"

    def __str__(self):
        return f"Caregiver {self.caregiver_user}"


class Member(models.Model):
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
        return f"{self.street}, {self.town}" if self.street else "Address"


class Job(models.Model):
    job_id = models.AutoField(primary_key=True, db_column="job_id")
    member = models.ForeignKey(
        Member,
        on_delete=models.CASCADE,
        db_column="member_user_id",
        related_name="jobs",
    )
    required_caregiving_type = models.CharField(max_length=50)
    other_requirements = models.TextField(null=True, blank=True)
    date_posted = models.DateField()

    class Meta:
        managed = False
        db_table = "jobs"
        ordering = ["-date_posted", "-job_id"]

    def __str__(self):
        return f"Job {self.job_id} ({self.required_caregiving_type})"


class Appointment(models.Model):
    appointment_id = models.AutoField(primary_key=True, db_column="appointment_id")
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
    appointment_date = models.DateField()
    appointment_time = models.TimeField()
    work_hours = models.IntegerField(null=True, blank=True)
    status = models.CharField(max_length=20, default="Pending")

    class Meta:
        managed = False
        db_table = "appointments"
        ordering = ["-appointment_date", "-appointment_time"]

    def __str__(self):
        return f"Appt {self.appointment_id} {self.appointment_date}"

from django.urls import path

from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
    path("register/caregiver/", views.register_caregiver, name="register_caregiver"),
    path("register/member/", views.register_member, name="register_member"),
    path("search/", views.search_caregivers, name="search"),
    path("member/jobs/", views.member_jobs, name="member_jobs"),
    path("jobs/", views.jobs_list, name="jobs_list"),
    path("jobs/<int:job_id>/apply/", views.apply_job, name="apply_job"),
    path("users/", views.users, name="users"),
    path("users/<int:pk>/delete/", views.delete_user, name="delete_user"),
]

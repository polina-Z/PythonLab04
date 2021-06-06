from datetime import datetime
from uuid import uuid4
from django.test import TestCase, Client
from django.utils import timezone
from .models import Task, UserProfile
from django.contrib.auth.models import User
from .enumTasks import Status, Priority
from .forms import TaskAdding
from django.urls import reverse


class TaskAndUsersTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="tester", password="1234567890")
        self.first_task = Task.objects.create(
            id="12345",
            title="test task",
            finish=datetime(2021, 6, 10, 8, 0, tzinfo=timezone.utc),
            priority=Priority.NORMAL,
            status=Status.ACTIVE,
            information="test example",
            user_creator=self.user,
        )

    def test_create_task(self):
        finish_time = datetime(2021, 6, 10, 8, 0, tzinfo=timezone.utc)
        task = Task.objects.create(
            id="123456",
            title="tester task",
            finish=finish_time,
            priority=Priority.NORMAL,
            status=Status.ACTIVE,
            information="test example",
            user_creator=self.user,
        )
        task_two = Task.objects.get(id=task.id)
        self.assertTrue(task.title == "tester task")
        self.assertTrue(task.finish == finish_time)
        self.assertTrue(task_two.finish == finish_time)

    def test_create_user(self):
        user_name = "testerUser"
        user = User.objects.create(username=user_name, password="1234567890")
        user_two = User.objects.get(id=user.id)
        self.assertTrue(user.username == user_name)
        self.assertTrue(user.username == user_two.username)

    def test_user_form_invalid(self):
        user_form = UserProfile(
            data={
                "username": "tester",
                "email": "a@a.qw",
                "password1": "1234567890",
                "password2": "1234567890",
            }
        )
        self.assertTrue(not user_form.is_valid())

    def test_user_form_valid(self):
        user_form = UserProfile(
            data={
                "username": "tester_two",
                "email": "a@a.qw",
                "password1": "userpassword",
                "password2": "userpassword",
            }
        )
        self.assertTrue(user_form.is_valid())
        self.assertTrue(isinstance(user_form.save(commit=False), User))

    def test_task_form_invalid(self):
        task_form = TaskAdding(
            data={
                "title": "test task",
                "finish": datetime(2021, 6, 10, 8, 0, tzinfo=timezone.utc),
                "priority": "1",
                "status": "2",
            }
        )
        self.assertFalse(task_form.is_valid())

    def test_task_form_valid(self):
        task_form = TaskAdding(
            data={
                "title": "task tester",
                "finish": datetime(2021, 6, 10, 8, 0, tzinfo=timezone.utc),
                "priority": "2",
                "status": "2",
                "information": "text",
            }
        )
        self.assertTrue(task_form.is_valid())
        self.assertTrue(isinstance(task_form.save(commit=False), Task))

    def test_task_form_add(self):
        task_form = TaskAdding(
            data={
                "title": "task tester add",
                "finish": datetime(2021, 6, 10, 8, 0, tzinfo=timezone.utc),
                "priority": "2",
                "status": "2",
                "information": "text",
            }
        )
        task = task_form.save(commit=False)
        task.user_creator = self.user
        task.pub_date = timezone.now()
        task.id = str(uuid4().hex)[-5:]
        task.save()
        task_two = Task.objects.get(id=task.id)
        self.assertTrue(task.title == task_two.title)
        self.assertTrue(task_two.title == "task tester add")


class ViewsTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username="tester_views", email="a@a.qw", password="12345"
        )
        self.user.save()
        self.first_task = Task.objects.create(
            id="90577",
            title="first task",
            finish=datetime(2021, 6, 10, 8, 0, tzinfo=timezone.utc),
            priority=Priority.NORMAL,
            status=Status.ACTIVE,
            information="test example",
            user_creator=self.user,
        )

    def test_index(self):
        response = self.client.get(reverse("home"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "taskManager/index.html")

    def test_task_page(self):
        user = self.user
        self.assertTrue(self.client.login(username=user.username, password="12345"))
        response = self.client.get(reverse("tasks"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "taskManager/tasks.html")

    def test_task_page_no_login(self):
        response = self.client.get(reverse("tasks"))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, "/sign_in/")

    def test_add_task_no_login(self):
        response = self.client.get(reverse("add_task"))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, "/sign_in/")

    def test_add_task_post_valid(self):
        user = self.user
        self.assertTrue(self.client.login(username=user.username, password="12345"))
        response = self.client.post(
            reverse("add_task"),
            {
                "title": "task tester add post",
                "finish": datetime(2021, 6, 10, 8, 0, tzinfo=timezone.utc),
                "priority": "2",
                "status": "2",
                "information": "text",
            },
        )
        self.assertEqual(
            Task.objects.get(title="task tester add post").title, "task tester add post"
        )
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, "/tasks/")

    def test_add_task_post_invalid(self):
        user = self.user
        self.assertTrue(self.client.login(username=user.username, password="12345"))
        response = self.client.post(
            reverse("add_task"),
            {
                "title": "task tester add post",
                "finish": datetime(2021, 6, 10, 8, 0, tzinfo=timezone.utc),
                "priority": "2",
                "information": "text",
            },
        )
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "taskManager/create_task.html")

    def test_sign_up_post_valid(self):
        response = self.client.post(
            reverse("sign_up"),
            {
                "username": "testersignip",
                "email": "a@a.qw",
                "password1": "pass123456",
                "password2": "pass123456",
            },
        )
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, "/accounts/profile/")

    def test_sign_up_post_invalid(self):
        response = self.client.post(
            reverse("sign_up"),
            {
                "username": "testersignip",
                "email": "a@a.qw",
                "password1": "pass123456",
                "password2": "pdfvdvfdnj",
            },
        )
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "taskManager/sign.html")

    def test_sign_up_get(self):
        response = self.client.get(reverse("sign_up"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "taskManager/sign.html")

    def test_profile(self):
        user = self.user
        self.assertTrue(self.client.login(username=user.username, password="12345"))
        self.assertTrue(
            self.client.post(
                reverse("add_task"),
                {
                    "title": "task 1",
                    "finish": datetime(2021, 6, 10, 8, 0, tzinfo=timezone.utc),
                    "priority": "2",
                    "status": "0",
                    "information": "text",
                },
            )
        )
        self.assertTrue(
            self.client.post(
                reverse("add_task"),
                {
                    "title": "task 2",
                    "finish": datetime(2021, 6, 10, 8, 0, tzinfo=timezone.utc),
                    "priority": "2",
                    "status": "1",
                    "information": "text",
                },
            )
        )
        self.assertTrue(
            self.client.post(
                reverse("add_task"),
                {
                    "title": "task 3",
                    "finish": datetime(2021, 6, 10, 8, 0, tzinfo=timezone.utc),
                    "priority": "2",
                    "status": "2",
                    "information": "text",
                },
            )
        )
        response = self.client.get(reverse("profile"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "taskManager/profile.html")

    def test_profile_no_login(self):
        response = self.client.get(reverse("profile"))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, "/sign_in/")

    def test_logout_login(self):
        user = self.user
        self.assertTrue(self.client.login(username=user.username, password="12345"))
        response = self.client.get(reverse("logout"))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, "/")

    def test_logout_no_login(self):
        response = self.client.get(reverse("logout"))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, "/sign_in/")

    def test_change_password_post_valid(self):
        user = self.user
        self.assertTrue(self.client.login(username=user.username, password="12345"))
        response = self.client.post(
            reverse("password"),
            {
                "old_password": "12345",
                "new_password1": "pol1234567890",
                "new_password2": "pol1234567890",
            },
        )
        self.assertTrue(
            self.client.login(username=user.username, password="pol1234567890")
        )
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, "/accounts/profile/")

    def test_change_password_post_invalid(self):
        user = self.user
        self.assertTrue(self.client.login(username=user.username, password="12345"))
        response = self.client.post(
            reverse("password"),
            {
                "old_password": "12345",
                "new_password1": "pol1234567890",
                "new_password2": "pol1234dvsd567890",
            },
        )
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "taskManager/password_change.html")

    def test_change_password_no_login(self):
        response = self.client.get(reverse("password"))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, "/sign_in/")

    def test_delete_user_no_login(self):
        response = self.client.get(reverse("delete_user"))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, "/sign_in/")

    def test_delete_user(self):
        user = self.user
        self.assertTrue(self.client.login(username=user.username, password="12345"))
        response = self.client.get(reverse("delete_user"))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, "/")

    def test_task_edit_no_login(self):
        task = self.first_task
        response = self.client.get(fr"/edit/{task.id}")
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, "/sign_in/")

    def test_task_edit_valid(self):
        user = self.user
        self.assertTrue(self.client.login(username=user.username, password="12345"))
        task = self.first_task
        response = self.client.post(
            fr"/edit/{task.id}",
            {
                "title": "first task",
                "finish": timezone.now(),
                "priority": "1",
                "status": "1",
                "information": "test example",
            },
        )
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, "/tasks/")
        self.assertEqual(Task.objects.first().status, Status.FINISHED)

    def test_task_edit_invalid(self):
        user = self.user
        self.assertTrue(self.client.login(username=user.username, password="12345"))
        task = self.first_task
        response = self.client.post(
            fr"/edit/{task.id}",
            {
                "title": "first task",
                "finish": timezone.now(),
                "priority": "1",
                "status": "1",
            },
        )
        self.assertEqual(Task.objects.first().status, Status.ACTIVE)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "taskManager/edit.html")

    def test_task_edit_not_post(self):
        user = self.user
        self.assertTrue(self.client.login(username=user.username, password="12345"))
        task = self.first_task
        response = self.client.get(fr"/edit/{task.id}")
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "taskManager/edit.html")
        self.assertEqual(Task.objects.first().status, Status.ACTIVE)

    def test_remove_no_login(self):
        task = self.first_task
        response = self.client.get(fr"/remove/{task.id}")
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, "/sign_in/")

    def test_remove_login(self):
        user = self.user
        self.assertTrue(self.client.login(username=user.username, password="12345"))
        task = self.first_task
        response = self.client.post(fr"/remove/{task.id}")
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, "/tasks/")

    def test_finished_login(self):
        user = self.user
        self.assertTrue(self.client.login(username=user.username, password="12345"))
        task = self.first_task
        response = self.client.post(fr"/finished/{task.id}")
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, "/tasks/")
        self.assertEqual(Task.objects.get(id=task.id).status, Status.FINISHED)

    def test_finished_no_login(self):
        task = self.first_task
        response = self.client.get(fr"/finished/{task.id}")
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, "/sign_in/")

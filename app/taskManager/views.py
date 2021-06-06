from uuid import uuid4
from django.shortcuts import render, redirect, get_object_or_404
from .forms import TaskAdding
from .models import UserProfile
from django.contrib.auth import login, logout, update_session_auth_hash
from django.contrib import messages
from django.utils import timezone
from .models import Task
from taskManager.enumTasks import Status, SendToEmail
from django.contrib.auth.views import PasswordChangeForm
from django.contrib.auth.models import User
import logging


logger = logging.getLogger(__name__)


def index(request):
    context = {"user_status": request.user.username}
    logger.info("Загружена начальная страница.")
    return render(request, "taskManager/index.html", context)


def tasks_page(request):
    context = {"user_status": request.user.username}
    if request.user.is_authenticated:
        tasks = Task.objects.filter(user_creator__exact=request.user).order_by("finish")
        context["tasks"] = tasks
        logger.info(
            "Просмотр списка задач у пользователя {}.".format(request.user.username)
        )
        return render(request, "taskManager/tasks.html", context)
    else:
        logger.info(
            "Страница просмотра списка задач не была загружена, так как пользователь не авторизован."
        )
        return redirect("sign_in")


def add_task(request):
    context = {"user_status": request.user.username}
    if request.user.is_authenticated:
        if request.method == "POST":
            form = TaskAdding(request.POST)
            if form.is_valid():
                task = form.save(commit=False)
                task.user_creator = request.user
                task.pub_date = timezone.now()
                task.id = str(uuid4().hex)[-5:]
                task.save()
                logger.info(
                    "У пользователя {} была добавлена задача {}.".format(
                        request.user.username, task.title
                    )
                )
                return redirect("/tasks/")
            else:
                logger.info(
                    "У пользователя {} не была добавлена задача, так как форма является не корректной.".format(
                        request.user.username
                    )
                )
                messages.error(request, "Error: Task has not been added. Try again")
                context["form_errors"] = form.errors
        form = TaskAdding()
        context["form"] = form
        return render(request, "taskManager/create_task.html", context)
    else:
        logger.info(
            "Страница добавления задачи не была загружена, так как пользователь не авторизован."
        )
        return redirect("sign_in")


def sign_up(request):
    context = {}
    if request.method == "POST":
        form = UserProfile(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            logger.info(
                "Пользователь {} успешно зарегистрирован.".format(user.username)
            )
            SendToEmail(user.email, user.username).start()
            return redirect("profile")
        else:
            logger.info(
                "Пользователь не был зарегистрирован, так как введенные данные некорректны."
            )
            messages.error(request, "Error: Registration error. Try again")
            context["form_errors"] = form.errors
    form = UserProfile()
    context["form"] = form
    return render(request, "taskManager/sign.html", context)


def profile(request):
    if request.user.is_authenticated:
        active = 0
        finish = 0
        failed = 0
        tasks = Task.objects.filter(user_creator=request.user)
        for task in tasks:
            if task.status == Status.ACTIVE:
                active += 1
            if task.status == Status.FINISHED:
                finish += 1
            if task.status == Status.FAILED:
                failed += 1
        context = {
            "user_status": request.user.username,
            "active": active,
            "finished": finish,
            "failed": failed,
        }
        logger.info("Загружен профиль пользователя {}.".format(request.user.username))
        return render(request, "taskManager/profile.html", context)
    else:
        logger.info(
            "Страница профиля пользователя не была загружена, так как пользователь не авторизован."
        )
        return redirect("sign_in")


def logout_view(request):
    if request.user.is_authenticated:
        logout(request)
        logger.info("Осуществлен выход пользователя {}.".format(request.user.username))
        return redirect("home")
    else:
        logger.info(
            "Выход пользователя не осуществлен, так как пользователь не авторизован."
        )
        return redirect("sign_in")


def change_password(request):
    context = {"user_status": request.user.username}
    if request.user.is_authenticated:
        if request.method == "POST":
            form = PasswordChangeForm(request.user, request.POST)
            if form.is_valid():
                user = form.save()
                update_session_auth_hash(request, user)
                logger.info(
                    "Пароль у пользователя {} успешно изменен.".format(
                        request.user.username
                    )
                )
                return redirect("profile")
            else:
                logger.info(
                    "Пароль у пользователя {} не был изменен, так как были указаны неверные данные.".format(
                        request.user.username
                    )
                )
                messages.error(request, "Password has not been updated")
        form = PasswordChangeForm(request.user)
        context["form"] = form
        return render(request, "taskManager/password_change.html", context)
    else:
        logger.info(
            "Пароль у пользователя не был изменен, так как пользователь не авторизован."
        )
        return redirect("sign_in")


def delete_user(request):
    if request.user.is_authenticated:
        user = User.objects.filter(id=request.user.id)
        if user.delete():
            logger.info("Пользователь был успешно удален.")
            return redirect("home")
        logger.error("Пользователь не был удален.")
        return redirect("profile")
    else:
        logger.info("Пользователь не был удален, так как пользователь не авторизован.")
        return redirect("sign_in")


def task_edit(request, task_id):
    if request.user.is_authenticated:
        task = get_object_or_404(Task, id=task_id)
        if task is None:
            logger.warning("Задачи с id {} не существует".format(task_id))
        if request.method == "POST":
            form = TaskAdding(request.POST, instance=task)
            if form.is_valid():
                task_update = form.save(commit=False)
                task_update.user_creator = task.user_creator
                task_update.pub_date = timezone.now()
                task_update.id = task.id
                task_update.save()
                logger.info(
                    "У пользовател {} задача {} успешно изменена.".format(
                        request.user.username, task_update.title
                    )
                )
                return redirect("tasks")
            else:
                form = TaskAdding(
                    initial={
                        "title": task.title,
                        "pub_date": task.pub_date,
                        "finish": task.finish,
                        "priority": task.priority,
                        "status": task.status,
                        "information": task.information,
                        "user_creator": task.user_creator,
                    },
                    instance=task,
                )
                logger.info(
                    "У пользовател {} задача c id {} не изменена, так как переданы неверные данные.".format(
                        request.user.username, task_id
                    )
                )
                return render(
                    request,
                    "taskManager/edit.html",
                    {
                        "form": form,
                        "form_errors": messages.error(
                            request, "Error: Task has not been edit. Try again"
                        ),
                    },
                )
        else:
            form = TaskAdding(
                initial={
                    "title": task.title,
                    "pub_date": task.pub_date,
                    "finish": task.finish,
                    "priority": task.priority,
                    "status": task.status,
                    "information": task.information,
                    "user_creator": task.user_creator,
                },
                instance=task,
            )
            logger.info(
                "У пользовател {} задача c id {} не изменена, так как данные не были переданы.".format(
                    request.user.username, task_id
                )
            )
            return render(request, "taskManager/edit.html", {"form": form})
    else:
        logger.info(
            "Задача c id {} не была отредактирована, так как пользователь не авторизован.".format(
                task_id
            )
        )
        return redirect("sign_in")


def remove(request, task_id):
    if request.user.is_authenticated:
        task = get_object_or_404(Task, id=task_id)
        if task is None:
            logger.warning("Задачи с id {} не существует".format(task_id))
        if task.delete():
            logger.info("Задача c id {} успешно удалена.".format(task_id))
            return redirect("tasks")
        else:
            logger.error("Задача с id {} не была удалена.".format(task_id))
            return render(
                request,
                "tasks",
                {
                    "form_errors": messages.error(
                        request, "Error: Task has not been remove. Try again"
                    )
                },
            )
    else:
        logger.info(
            "Задача с id {} не была удалена, так как пользователь не авторизован.".format(
                task_id
            )
        )
        return redirect("sign_in")


def finished(request, task_id):
    if request.user.is_authenticated:
        if Task.objects.filter(id=task_id).update(
            status=Status.FINISHED, finish=timezone.now()
        ):
            logger.info("Задача с id {} успешно завершена.".format(task_id))
            return redirect("tasks")
        else:
            logger.warning(
                "Задача с id {} не была завершена, так как возникла ошибка.".format(
                    task_id
                )
            )
            return render(
                request,
                "tasks",
                {
                    "form_errors": messages.error(
                        request, "Error: Task has not been finished. Try again"
                    )
                },
            )
    else:
        logger.info(
            "Задача с id {} не была завершена, так как пользователь не авторизован.".format(
                task_id
            )
        )
        return redirect("sign_in")

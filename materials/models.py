from django.db import models


class Course(models.Model):
    title = models.CharField(max_length=200, verbose_name="Название")
    preview = models.ImageField(
        upload_to="materials/courses/",
        blank=True,
        null=True,
        verbose_name="Превью",
    )
    description = models.TextField(verbose_name="Описание")

    def __str__(self):
        return self.title


class Lesson(models.Model):
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name="lessons",
        verbose_name="Курс",
    )
    title = models.CharField(max_length=200, verbose_name="Название")
    description = models.TextField(verbose_name="Описание")
    preview = models.ImageField(
        upload_to="materials/lessons/",
        blank=True,
        null=True,
        verbose_name="Превью",
    )
    video_url = models.URLField(verbose_name="Ссылка на видео")

    def __str__(self):
        return self.title

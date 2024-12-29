from django.db import models


class FrequentlyAskedQuestion(models.Model):
    """
    A model that represents a frequently asked question.

    Attributes:
        question (str): The question being asked.
        answer (str): The answer to the question.

    Methods:
        __str__(): Returns a string representation of the question.
    """
    question = models.CharField(max_length=255)
    answer = models.TextField()

    def __str__(self):
        return self.question


class About(models.Model):
    """
    A model that represents the about page.

    Attributes:
        title (str): The title of the about page.
        content (str): The content of the about page.
        is_active (bool): Indicates if the about page is currently active.

    Methods:
        __str__(): Returns a string representation of the about page.
        save(): Overrides the default save method to deactivate other active
            about pages.
    """
    title = models.CharField(max_length=255)
    content = models.TextField()
    is_active = models.BooleanField(default=False)

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if self.is_active:
            # Deactivate all other entries
            About.objects.filter(is_active=True).update(is_active=False)
        super().save(*args, **kwargs)

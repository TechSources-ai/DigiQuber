from django.db import models


class APIToken(models.Model):
    token = models.CharField(max_length=512)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Token created at {self.created_at}"

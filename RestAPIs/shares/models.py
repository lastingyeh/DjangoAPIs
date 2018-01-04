from django.db import models


class Share(models.Model):
	name = models.TextField()
	last_modify_date = models.DateTimeField(auto_now=True)
	created = models.DateTimeField(auto_now_add=True)

	class Meta:
		db_table = 'share'

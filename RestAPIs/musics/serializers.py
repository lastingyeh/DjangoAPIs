from rest_framework import serializers
from .models import Music

from datetime import datetime


class MusicSerializer(serializers.ModelSerializer):
	class Meta:
		model = Music
		# fields = '__all__'
		fields = ('id', 'song', 'singer', 'last_modify_date', 'created')

	def get_days_since_created(self, obj):
		return (datetime.now() - obj.created).days

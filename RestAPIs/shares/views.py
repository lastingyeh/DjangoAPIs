from rest_framework import viewsets, status
from rest_framework.decorators import permission_classes
from rest_framework.parsers import JSONParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import Share
from .serializers import ShareSerializer


class ShareViewSet(viewsets.ModelViewSet):
	queryset = Share.objects.all()
	serializer_class = ShareSerializer
	# Postman Post set Headers : "Content-Type":"application/json;charset=utf-8"
	# Body / raw : {"name":"xxx"}
	parser_classes = (JSONParser,)

	def get_permissions(self):
		if self.action in ('create',):
			self.permission_classes = [IsAuthenticated]

		return [permission() for permission in self.permission_classes]

	# GET api/shares/
	def list(self, request, **kwargs):
		users = Share.objects.all()
		serializer = ShareSerializer(users, many=True)

		return Response(serializer.data, status=status.HTTP_200_OK)

	# POST api/shares/
	@permission_classes((IsAuthenticated,))
	def create(self, request, **kwargs):
		name = request.data.get('name')
		users = Share.objects.create(name=name)
		serializer = ShareSerializer(users)

		return Response(serializer.data, status=status.HTTP_201_CREATED)

"""View module for handling requests for service ticket data"""
from django.http import HttpResponseServerError
from rest_framework.viewsets import ViewSet
from rest_framework.response import Response
from rest_framework import serializers, status
from repairsapi.models import ServiceTicket


class ServiceTicketView(ViewSet):
    """Honey Rae API service ticket view"""

    def list(self, request):
        """Handle GET requests to get all service tickets

        Returns:
            Response -- JSON serialized list of service tickets
        """

        service_tickets = []
        if request.auth.user.is_staff:
            service_tickets = ServiceTicket.objects.all()
        else:
            service_tickets = ServiceTicket.objects.filter(
                customer__user=request.auth.user)
        serialized = ServiceTicketSerializer(service_tickets, many=True)
        return Response(serialized.data, status=status.HTTP_200_OK)

    def retrieve(self, request, pk=None):
        """Handle GET requests for single service tickets

        Returns:
            Response -- JSON serialized service tickets record
        """

        service_ticket = ServiceTicket.objects.get(pk=pk)
        serialized = ServiceTicketSerializer(service_ticket)
        return Response(serialized.data, status=status.HTTP_200_OK)


class ServiceTicketSerializer(serializers.ModelSerializer):
    """JSON serializer for service tickets"""
    class Meta:
        model = ServiceTicket
        fields = (
            'customer',
            'employee',
            'description',
            'emergency',
            'date_completed'
        )
        depth = 1
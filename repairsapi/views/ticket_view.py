"""View module for handling requests for service ticket data"""
from django.http import HttpResponseServerError
from rest_framework.viewsets import ViewSet
from rest_framework.response import Response
from rest_framework import serializers, status
from repairsapi.models import ServiceTicket, Employee, Customer


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

    def create(self, request):
        """Handle POST requests for service tickets

        Returns:
            Response: JSON serialized representation of newly created service ticket
        """
        new_ticket = ServiceTicket()
        new_ticket.customer = Customer.objects.get(user=request.auth.user)
        new_ticket.description = request.data['description']
        new_ticket.emergency = request.data['emergency']
        new_ticket.save()

        serialized = ServiceTicketSerializer(new_ticket)

        return Response(serialized.data, status=status.HTTP_201_CREATED)


class TicketEmployeeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Employee
        fields = ('id', 'specialty', 'full_name')


class TicketCustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = ('id', 'address', 'full_name')


class ServiceTicketSerializer(serializers.ModelSerializer):
    """JSON serializer for service tickets"""

    employee = TicketEmployeeSerializer(many=False)
    customer = TicketCustomerSerializer(many=False)

    class Meta:
        model = ServiceTicket
        fields = (
            'id',
            'customer',
            'employee',
            'description',
            'emergency',
            'date_completed'
        )
        depth = 1

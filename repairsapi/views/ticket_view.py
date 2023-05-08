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

            if "status" in request.query_params:
                if request.query_params['status'] == 'done':
                    service_tickets = service_tickets.filter(
                        date_completed__isnull=False)
                if request.query_params['status'] == 'unclaimed':
                    service_tickets = service_tickets.filter(
                        date_completed__isnull=True, employee_id__isnull=True)
                if request.query_params['status'] == 'inprogress':
                    service_tickets = service_tickets.filter(
                        date_completed__isnull=True, employee_id__isnull=False)
                if 'search_query' in request.query_params['status']:
                    search_query = request.query_params['status'].split(
                        '--')[1]
                    service_tickets = service_tickets.filter(
                        description__contains=search_query)
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
        # Select the targeted ticket using pk
        new_ticket = ServiceTicket()
        # Get the employee id from the client request
        new_ticket.customer = Customer.objects.get(user=request.auth.user)
        # Select the employee from the database using that id
        new_ticket.description = request.data['description']
        # Assign the Employee instance to the employee property of the ticket
        new_ticket.emergency = request.data['emergency']
        # Save the updated ticket
        new_ticket.save()

        serialized = ServiceTicketSerializer(new_ticket)

        return Response(serialized.data, status=status.HTTP_201_CREATED)

    def update(self, request, pk=None):
        """Handle PUT requests for tickets"""
        ticket = ServiceTicket.objects.get(pk=pk)
        employee_id = request.data['employee']
        date_completed = request.data['date_completed']
        assigned_employee = Employee.objects.get(pk=employee_id)
        ticket.employee = assigned_employee
        ticket.date_completed = date_completed
        ticket.save()
        return Response(None, status=status.HTTP_204_NO_CONTENT)

    def destroy(self, request, pk=None):
        """Handles Delete requests"""
        ticket = ServiceTicket.objects.get(pk=pk)
        ticket.delete()
        return Response(None, status=status.HTTP_204_NO_CONTENT)


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

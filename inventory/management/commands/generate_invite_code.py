# inventory/management/commands/generate_invite_code.py
from django.core.management.base import BaseCommand
from inventory.models import InvitationCode
import random
import string

class Command(BaseCommand):
    help = 'Genera códigos de invitación para usuarios staff'

    def add_arguments(self, parser):
        parser.add_argument(
            '--cantidad',
            type=int,
            default=1,
            help='Cantidad de códigos a generar'
        )

    def handle(self, *args, **options):
        cantidad = options['cantidad']
        
        for _ in range(cantidad):
            code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
            InvitationCode.objects.create(
                code=code,
                is_staff_invitation=True
            )
            self.stdout.write(self.style.SUCCESS(f'Código generado: {code}'))
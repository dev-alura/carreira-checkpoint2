from django.contrib.auth.models import User
from django.db import models


class BaseModel(models.Model):
    at_created = models.DateTimeField(auto_now_add=True)
    at_updated = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Clients(BaseModel):
    name = models.CharField(max_length=150)
    email = models.EmailField(blank=False, max_length=100, unique=True)
    responsavel = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name="clientes",
        verbose_name="Vendedor/Responsável",
        help_text="Vendedor responsável por este cliente",
        default=1,
    )

    class Meta:
        verbose_name = "Client"
        verbose_name_plural = "Clients"

    def __str__(self):
        return self.name


class PhoneType(models.TextChoices):
    CEL = "CEL", "Celular"
    HOME = "HOME", "Principal"
    WHATS = "WHATS", "WhatsApp"


class Notas(BaseModel):
    texto = models.CharField(blank=False, max_length=5000)
    client = models.ForeignKey(
        Clients, blank=False, on_delete=models.CASCADE, related_name="notas"
    )

    class Meta:
        verbose_name = "Nota"
        verbose_name_plural = "Notas"

        def __str__(self):
            return f"{self.texto[:10]}"


class Phone(models.Model):
    number = models.CharField(max_length=30)
    tipo = models.CharField(
        max_length=5, choices=PhoneType.choices, default=PhoneType.CEL
    )
    client = models.ForeignKey(
        Clients, on_delete=models.CASCADE, related_name="telefones"
    )

    class Meta:
        verbose_name = "Phone"
        verbose_name_plural = "Phones"

    def __str__(self):
        return f"{self.number} ({self.get_tipo_display()})"



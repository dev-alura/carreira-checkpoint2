from rest_framework import routers

from clientes.views import ClientsViewSet, NotasViewSet, PhoneViewSet

# Router sem trailing slash obrigatório  
router = routers.DefaultRouter(trailing_slash=False)

router.register("clientes", ClientsViewSet, basename="clientes")
router.register("telefones", PhoneViewSet, basename="telefones")
router.register("notas", NotasViewSet, basename="notas")

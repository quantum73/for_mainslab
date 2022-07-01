from rest_framework import routers

from main_app.views import ClientsViewSet, BillsViewSet

router = routers.SimpleRouter()
router.register(r'clients', ClientsViewSet)
router.register(r'bills', BillsViewSet)

from django.urls import path
from inmuebleslist_app.views import inmueble_list, inmueble_detalle

urlpatterns = [
    path('list/',inmueble_list,name='inmueble-list'),
    path('<int:pk>',inmueble_detalle,name='inmueble-detalle'),

]

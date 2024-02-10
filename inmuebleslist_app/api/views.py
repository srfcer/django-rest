from rest_framework.response import Response
from inmuebleslist_app.models import Edificacion, Empresa, Comentario
from inmuebleslist_app.api.serializers import EdificacionSerializer, EmpresaSerializer, ComentarioSerializer
#from rest_framework.decorators import api_view
from rest_framework import status, generics, mixins, viewsets
from rest_framework.views import APIView
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from inmuebleslist_app.api.permissions import IsAdminOrReadOnly, IsComentarioUserOrReadOnly
from rest_framework.throttling import AnonRateThrottle, UserRateThrottle, ScopedRateThrottle
from inmuebleslist_app.api.throttling import ComentarioCreateThrottle, ComentarioListThrottle
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters
from inmuebleslist_app.api.pagination import EdificacionPagination, EdificacionLOPagination


class UsuarioComentario(generics.ListAPIView):
    serializer_class = ComentarioSerializer
    # def get_queryset(self):
    #     username = self.kwargs['username']
    #     return Comentario.objects.filter(comentario_user__username=username)
    
    def get_queryset(self):
        username = self.request.query_params.get('username',None)
        return Comentario.objects.filter(comentario_user__username=username)
    

class ComentarioCreate(generics.CreateAPIView):
    serializer_class = ComentarioSerializer
    permission_classes = [IsAuthenticated]
    throttle_classes = [ComentarioCreateThrottle]
    def get_queryset(self):
        return Comentario.objects.all()
    
    def perform_create(self, serializer):
        pk = self.kwargs.get('pk')
        inmueble=Edificacion.objects.get(pk=pk)
        
        user = self.request.user
        comentario_queryset = Comentario.objects.filter(edificacion=inmueble, comentario_user=user)
        
        if comentario_queryset.exists():
            raise ValidationError("El usuario ya escribio un comentario para este inmueble")
        
        if inmueble.number_calificacion == 0:
            inmueble.avg_calificacion = serializer.validated_data['calificacion']
        else:
            inmueble.avg_calificacion = (serializer.validated_data['calificacion']+ inmueble.avg_calificacion)/2
        
        inmueble.number_calificacion = inmueble.number_calificacion + 1
        inmueble.save()
        
        serializer.save(edificacion=inmueble, comentario_user=user)

class ComentarioList(generics.ListCreateAPIView):
    #queryset = Comentario.objects.all()
    serializer_class = ComentarioSerializer 
    #permission_classes = [IsAuthenticated] #para que usuario logueado puede consultar la data
    throttle_classes = [ComentarioListThrottle,AnonRateThrottle]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['comentario_user__username', 'active']
    
    def get_queryset(self):
        pk = self.kwargs['pk']
        return Comentario.objects.filter(edificacion=pk)
    
class ComentarioDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Comentario.objects.all()
    serializer_class = ComentarioSerializer
    permission_classes = [IsComentarioUserOrReadOnly]
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = "comentario-detail"



# class ComentarioList(mixins.CreateModelMixin, mixins.ListModelMixin, generics.GenericAPIView):
#     queryset = Comentario.objects.all()
#     serializer_class = ComentarioSerializer
    
#     def get(self, request, *args, **kwargs):
#         return self.list(request, *args, **kwargs)
    
#     def post(self, request, *args, **kwargs):
#         return self.create(request, *args, **kwargs)

# class ComentarioDetail(mixins.RetrieveModelMixin, generics.GenericAPIView):
#     queryset = Comentario.objects.all()
#     serializer_class = ComentarioSerializer
    
#     def get(self, request, *args, **kwargs):
#         return self.retrieve(request, *args, **kwargs)
    

class EmpresaVS(viewsets.ModelViewSet):
    permission_classes = [IsAdminOrReadOnly]
    queryset = Empresa.objects.all()
    serializer_class = EmpresaSerializer

# class EmpresaAV(APIView):
#     def get(self, request, format=None):
#         empresa = Empresa.objects.all()
#         serializer = EmpresaSerializer(empresa, many=True, context={'request': request})
#         return Response(serializer.data)

#     def post(self, request, format=None):
#         serializer = EmpresaSerializer(data=request.data)
#         if serializer.is_valid():
#             serializer.save()
#             return Response(serializer.data, status=status.HTTP_201_CREATED)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class EmpresaDetalleAV(APIView):
    def get(self, request, pk, format=None):
        try:
            empresa = Empresa.objects.get(pk=pk)
        except Empresa.DoesNotExist:
            return Response({'error': 'Empresa no encontrada'}, status=status.HTTP_404_NOT_FOUND) 
        
        serializer = EmpresaSerializer(empresa, context={'request': request})
        return Response(serializer.data)
    def put(self, request, pk, format=None):
        try:
            empresa = Empresa.objects.get(pk=pk)
        except Empresa.DoesNotExist:
            return Response({'error': 'Empresa no encontrada'}, status=status.HTTP_404_NOT_FOUND) 
        
        serializer = EmpresaSerializer(empresa, data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
 
    def delete(self, request, pk, format=None):
        try:
            empresa = Empresa.objects.get(pk=pk)
        except Empresa.DoesNotExist:
            return Response({'error': 'Empresa no encontrada'}, status=status.HTTP_404_NOT_FOUND) 
        
        empresa.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

class EdificacionList(generics.ListAPIView):
    queryset = Edificacion.objects.all()
    serializer_class = EdificacionSerializer
    #filter_backends = [DjangoFilterBackend]*
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    #filterset_fields = ['direccion', 'empresa__nombre']*
    search_fields = ['direccion', 'empresa__nombre']
    pagination_class = EdificacionPagination

    
class EdificacionAV(APIView):
    permission_classes = [IsAdminOrReadOnly]    
    def get(self, request, format=None):
        inmuebles = Edificacion.objects.all()
        serializer = EdificacionSerializer(inmuebles, many=True)
        return Response(serializer.data)

    def post(self, request, format=None):
        serializer = EdificacionSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class EdificacionDetalleAV(APIView):
    permission_classes = [IsAdminOrReadOnly]    
    def get(self, request, pk, format=None):
        try:
            inmueble = Edificacion.objects.get(pk=pk)
        except Edificacion.DoesNotExist:
            return Response({'error': 'Inmueble no encontrado'}, status=status.HTTP_404_NOT_FOUND) 
        
        serializer = EdificacionSerializer(inmueble)
        return Response(serializer.data)
    
    def put(self, request, pk, format=None):
        try:
            inmueble = Edificacion.objects.get(pk=pk)
        except Edificacion.DoesNotExist:
            return Response({'error': 'Inmueble no encontrado'}, status=status.HTTP_404_NOT_FOUND)
        
            serializer = InmuebleSerializer(inmueble, data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)    
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self, request, pk, format=None):
        try:
            inmueble = Edificacion.objects.get(pk=pk)
        except Edificacion.DoesNotExist:
            return Response({'error': 'Inmueble no encontrado'}, status=status.HTTP_404_NOT_FOUND)
        
        inmueble.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    
from rest_framework import serializers
from inmuebleslist_app.models import Edificacion, Empresa, Comentario


class ComentarioSerializer(serializers.ModelSerializer):
    comentario_user = serializers.StringRelatedField(read_only=True)
    class Meta:
        model = Comentario
        exclude = ['edificacion'] # se excluye para que se inserte automáticamente
       # fields = '__all__'
        

class EdificacionSerializer(serializers.ModelSerializer):
    comentarios = ComentarioSerializer(many=True, read_only=True)    
    empresa_nombre = serializers.CharField(source='empresa.nombre')
    class Meta:
        model = Edificacion
        fields = '__all__'
        
#class EmpresaSerializer(serializers.ModelSerializer):
class EmpresaSerializer(serializers.ModelSerializer):
    #Muestra todas las colecciones de la empresa
    edificacionlist = EdificacionSerializer(many=True, read_only=True)
    #Muestra solamente un campo de la coleccion, esta relacionado con str de models
    #edificacionlist = serializers.StringRelatedField(many=True)
    #Muestra solamente el ID
    #edificacionlist = serializers.PrimaryKeyRelatedField(many=True, read_only=True)
    #Muestra el hiperlink
    #edificacionlist = serializers.HyperlinkedRelatedField (many=True, read_only=True,view_name='edificacion-detail')
    class Meta:
        model = Empresa
        fields = '__all__'




        
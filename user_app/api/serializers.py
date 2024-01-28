from rest_framework import serializers
from django.contrib.auth import User

class RegistrationSerializer(serializers.ModelSerializer):
    password2 = serializers.CharField(style={'input_type':'password'}, write_only=True)
    
    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'password2']
        extra_kwargs = {
            'password': {'write_only': True,'min_length': 5}
        }
        
    def save(self):
        password = self.validated_data['password']
        password2 = self.validated_data['password2']
        
        if password!= password2:
            raise serializers.ValidationError({'error': 'El password no coincide'})
        
        if User.objects.filter(username=self.validated_data['email'].exists()).exists():
            raise serializers.ValidationError({'error': 'Ya existe un usuario con ese email'})
        
        account = User(email=self.validated_data['email'], username=self.validated_data['username'])
        account.set_password(password)
        account.save()
        
        return account
    
        
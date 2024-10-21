from rest_framework import serializers
from ..models import CallTaker

class CallTakerBaseSerializer(serializers.Serializer):
    id = serializers.CharField(read_only=True)  # MongoEngine usa un ID por defecto
    first_name = serializers.CharField(max_length=50)
    last_name = serializers.CharField(max_length=50, required=False)
    code = serializers.CharField(max_length=20)
    area = serializers.CharField(max_length=20)
    created_at = serializers.DateTimeField(read_only=True)
    updated_at = serializers.DateTimeField(read_only=True)

class CallTakerCreateSerializer(CallTakerBaseSerializer):
    def validate_code(self, value):
        if CallTaker.objects.filter(code=value).count() > 0:
            raise serializers.ValidationError("A CallTaker with this code already exists.")
        return value

    def create(self, validated_data):
        call_taker = CallTaker(**validated_data)
        call_taker.save()
        return call_taker
    
class CallTakerListSerializer(CallTakerBaseSerializer):
    class Meta:
        fields = ['id', 'first_name', 'last_name', 'code', 'area']
        
class CallTakerUpdateSerializer(CallTakerBaseSerializer):
    def update(self, instance, validated_data):
        instance.first_name = validated_data.get('first_name', instance.first_name)
        instance.last_name = validated_data.get('last_name', instance.last_name)
        instance.code = validated_data.get('code', instance.code)
        instance.area = validated_data.get('area', instance.area)
        instance.save()
        return instance

from rest_framework.authtoken.serializers import TokenCreateSerializer


class CustomTokenCreateSerializer(TokenCreateSerializer):
    def validate(self, data):
        data['email'] = data['email'].lower()
        return super().validate(data)

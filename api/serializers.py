from rest_framework import serializers
from .models import User, Contact


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'phone_number', 'email', 'password', ]


class ContactSerializer(serializers.ModelSerializer):
    spam_likelihood = serializers.SerializerMethodField()
    email = serializers.SerializerMethodField()

    class Meta:
        model = Contact
        fields = ['id', 'user', 'name', 'phone_number',
                  'is_spam', 'spam_likelihood', 'email']

    def get_spam_likelihood(self, obj):
        return obj.spam_likelihood()

    def get_email(self, obj):
        request = self.context.get('request')
        
        # Get the user ID of the contact
        user_id = User.objects.filter(
            phone_number=obj.phone_number
        ).values_list('id', flat=True).first()

        if user_id is not None:
            # Check if the contact has the current user's phone number in their contact list
            user_has_contact = User.objects.filter(
                pk=user_id,
                contacts__phone_number=request.user.phone_number
            ).exists()
            
            # If the contact has the current user's phone number in their contact list
            if user_has_contact:
                # Retrieve the user object
                user = User.objects.get(pk=user_id)
                return user.email
        
        # If the contact is not a registered user or doesn't have the current user's phone number in their contact list
        return None

    def to_representation(self, instance):
        data = super().to_representation(instance)
        if not data['name']:
            return None
        return data


class MarkAsSpamSerializer(serializers.ModelSerializer):
    class Meta:
        model = Contact
        fields = ['phone_number', 'is_spam', 'user']

    def create(self, validated_data):
        # Retrieve the user_id from the context
        user_id = self.context.get('user_id')

        # Set the user field with the retrieved user_id
        validated_data['user_id'] = user_id

        # Create and return the Contact instance
        return Contact.objects.create(**validated_data)

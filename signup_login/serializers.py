from .models import WriterApplication
from rest_framework import serializers
from django.contrib.auth.models import User, Group


class UserRegistrationSerializers(serializers.ModelSerializer):
    confirm_password = serializers.CharField(required=True)

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name',
                  'email', 'password', 'confirm_password']

    def save(self):
        username = self.validated_data['username']
        first_name = self.validated_data['first_name']
        last_name = self.validated_data['last_name']
        email = self.validated_data['email']
        password = self.validated_data['password']
        confirm_password = self.validated_data['confirm_password']

        if password != confirm_password:
            raise serializers.ValidationError(
                {'password': ['Password does not match']})

        if User.objects.filter(email=email).exists():
            raise serializers.ValidationError(
                {'email': ['Email already exists']})

        user = User(username=username, email=email,
                    first_name=first_name, last_name=last_name)
        user.set_password(password)
        user.save()

        # Add the user to the 'user' group by default
        user_group, created = Group.objects.get_or_create(name='user')
        user.groups.add(user_group)

        return user

# class UserRegistrationSerializers(serializers.ModelSerializer):
#     confirm_password = serializers.CharField(required=True)

#     class Meta:
#         model = User
#         fields = ['username', 'first_name', 'last_name',
#                   'email', 'password', 'confirm_password']

#     def save(self):
#         username = self.validated_data['username']
#         first_name = self.validated_data['first_name']
#         last_name = self.validated_data['last_name']
#         email = self.validated_data['email']
#         password = self.validated_data['password']
#         confirm_password = self.validated_data['confirm_password']

#         if password != confirm_password:
#             raise serializers.ValidationError(
#                 {'password': ['Password Does not match']})

#         if User.objects.filter(email=email).exists():
#             raise serializers.ValidationError(
#                 {'email': ['Email already exists']})

#         account = User(username=username, email=email,
#                        first_name=first_name, last_name=last_name)
#         account.set_password(password)
#         account.save()
#         return account


class UserLoginSerializers(serializers.ModelSerializer):
    email = serializers.EmailField(required=True)
    password = serializers.CharField(required=True)

    class Meta:
        model = User
        fields = ['email', 'password']


class UserRoleUpdateSerializer(serializers.ModelSerializer):
    role = serializers.ChoiceField(choices=['user', 'student', 'writer'])

    class Meta:
        model = User
        fields = ['role']

    def update(self, instance, validated_data):
        instance.groups.clear()
        new_role = validated_data['role']
        group, created = Group.objects.get_or_create(name=new_role)
        instance.groups.add(group)

        instance.save()
        return instance


class UserWithRoleSerializer(serializers.ModelSerializer):
    roles = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'username', 'email',
                  'first_name', 'last_name', 'roles']

    def get_roles(self, obj):
        return [group.name for group in obj.groups.all()]


class WriterApplicationSerializer(serializers.ModelSerializer):
    user = serializers.ReadOnlyField(source='user.username')

    class Meta:
        model = WriterApplication
        fields = ['id', 'user', 'first_name', 'last_name',
                  'email', 'is_approved', 'agreed_to_terms']

    def validate(self, data):
        if WriterApplication.objects.filter(user=self.context['request'].user).exists():
            raise serializers.ValidationError(
                "You have already applied to become a writer.")
        return data


class WriterApplicationStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = WriterApplication
        fields = ['is_approved']

    def update(self, instance, validated_data):
        instance.is_approved = validated_data.get(
            'is_approved', instance.is_approved)
        instance.save()
        return instance

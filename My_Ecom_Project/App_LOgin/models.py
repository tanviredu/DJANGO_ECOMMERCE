from django.db import models
from django.utils.translation import ugettext_lazy
from django.contrib.auth.models import BaseUserManager,AbstractBaseUser,PermissionsMixin


from django.db.models.signals import post_save
from django.dispatch import receiver

######
# changing the core user model
# do not make any migration before that
# after changing the user make the migrations
######

class MyUserManager(BaseUserManager):
    ''' A custom user manager for handling
    for dealing with the new custom user
    using email as a unique identifier '''

    # overrite the method of the default
    # _create_user

    def _create_user(self,email,password,**extra_fields):
        ''' you can add additional paramter
        with the **extra_fields pparameter '''

        if not email:
            raise ValueError( "The Email is not set !!!!!" )

        # sanitaze email
        email = self.normalize_email(email)
        
        ## create the user
        user  = self.model(email=email,**extra_fields)
        
        ## set the encrypted password
        user.set_password(password) 
        user.save(using=self._db)  #_db is the database
        return user

    def create_superuser(self,email,password,**extra_fields):
        ''' This is the super user with the new 
        settings set the three settings '''

        extra_fields.setdefault('is_staff',True)
        extra_fields.setdefault('is_superuser',True)
        extra_fields.setdefault('is_active',True)

        ## raise some error
        if extra_fields.get('is_staff') is not True:
            raise ValueError("Superuser must have is_staff=True")
        if extra_fields.get('is_superuser') is not True:
            raise ValueError("Superuser must have is_superuser=True")

        return self._create_user(email,password,**extra_fields)


## Create the new User based on the MyUserManager

class User(AbstractBaseUser,PermissionsMixin):
    email     = models.EmailField(unique=True,null=False)
    ## normal user is by default not a staff
    is_staff  = models.BooleanField(ugettext_lazy('Staff Status'),default=False,help_text=("Designates weather the user can log in this site"))
    ## every user is by default active
    is_active = models.BooleanField(ugettext_lazy('active'),default=True,help_text=("Designates if the nuser should be treated as active")) 
    
    ## username will be replaced by the email address
    USERNAME_FIELD = 'email'

    ## adding the objects with the manager
    ## so all the method will be the MyUserManager
    objects = MyUserManager()
    ## next time you user user.objects.method()
    ## then all the attr and method will be useed
    ## by the custom MyuserManager

    def __str__(self):
        return self.email

    def get_full_name(self):
        return self.email
    
    def get_short_name(self):
        return self.email 



## create the profile table related witht he new user

class Profile(models.Model):
    ''' This is the Profile .Profile have username and other field
        User now dont have the username . made the username optional
        pull out the username from User and add it to Profile'''


    user        = models.OneToOneField(User,on_delete=models.CASCADE,related_name="profile")
    username    = models.CharField(max_length=204,blank=True)
    full_name   = models.CharField(max_length=204,blank=True)
    address_1   = models.TextField(max_length=300,blank=True)
    city        = models.CharField(max_length=40,blank=True)
    zipcode     = models.CharField(max_length=40,blank=True)
    country     = models.CharField(max_length=20,blank=True)
    phone       = models.CharField(max_length=20,blank=True)
    date_joined = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(self.user)
    
    ## check profile model is filled
    ## this is the field check method
    
    def is_fully_filled(self):
        ''' get all the fields name in this method check
        all the filleds then check if it filled '''

        fields_name = [f.name for f in self._meta.get_fields()]

        for field_name in fields_name:
            value = getattr(self,field_name)
            if value is None or value == "":
                return False
        return True 


## this is the mdehtod that
## catch the post_save signal
## and thn use it to add user


@receiver(post_save,sender=User)
def create_profile(sender,instance,created,**kwargs):
    if created:
        Profile.objects.create(user=instance)

## first three is the default parameter
## the sender
## and the instace after the create object
## created
## sender fill the instace with the object
## extra information comes from the **kwargs
## if you need


@receiver(post_save,sender=User)
def save_profile(sender,instance,**kwargs):
    instance.profile.save()

## this will save one instnce of the user in profile


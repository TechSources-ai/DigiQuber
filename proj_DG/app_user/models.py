# from django.db import models
# from app_login.models import CustomUser

# class Profile(models.Model):
#     user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='profile')
#     name = models.CharField(max_length=100)
#     customerRefNo = models.CharField(max_length=100, blank=True, null=True)
#     dgcustomerRefNo = models.CharField(max_length=100, blank=True, null=True)
#     kycStatus = models.BooleanField(default=False)
#     nameProofType = models.CharField(max_length=100, blank=True, null=True)
#     addressProofType = models.CharField(max_length=100, blank=True, null=True)
#     nameProofId = models.CharField(max_length=100, blank=True, null=True)
#     addressProofId = models.CharField(max_length=100, blank=True, null=True)
#     dob = models.DateField(blank=True, null=True)
#     billingAddress = models.JSONField(default=dict)
#     deliveryAddress = models.JSONField(default=dict)
#     same_as_delivery = models.BooleanField(default=False)  # True if billing address is same as delivery

#     def save(self, *args, **kwargs):
#         if not self.customerRefNo and self.user_id:
#             self.customerRefNo = f"TS{str(self.user_id).zfill(8)}"
#         super().save(*args, **kwargs)

#     def __str__(self):
#         return self.name

from django.db import models
from app_login.models import CustomUser

class Profile(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='profile')
    name = models.CharField(max_length=100)
    customerRefNo = models.CharField(max_length=100, blank=True, null=True)
    dgcustomerRefNo = models.CharField(max_length=100, blank=True, null=True)
    #kycStatus = models.BooleanField(default=False)
    kycStatus = models.CharField(max_length=1, default="I")  # Y or I


    nameProofType = models.CharField(max_length=100, blank=True, null=True)
    addressProofType = models.CharField(max_length=100, blank=True, null=True)
    nameProofId = models.CharField(max_length=100, blank=True, null=True)
    addressProofId = models.CharField(max_length=100, blank=True, null=True)

    dob = models.DateField(blank=True, null=True)

    billingAddressId = models.CharField(max_length=120, blank=True, null=True)  # ⭐ REQUIRED BY MMTC
    deliveryAddressId = models.CharField(
    max_length=120,blank=True,null=True)  # ⭐ REQUIRED BY MMTC
    billingAddress = models.JSONField(default=dict)
    deliveryAddress = models.JSONField(default=dict)
    same_as_delivery = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        if not self.customerRefNo and self.user_id:
            self.customerRefNo = f"PS{str(self.user_id).zfill(8)}"
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

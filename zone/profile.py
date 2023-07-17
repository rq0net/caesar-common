from abc import ABC
from .models import Czone
from django.contrib.auth import get_user_model

# Create your models here.
class ZoneProfile(ABC):
    #user = models.OneToOneField(get_user_model(), related_name='profile', on_delete=models.CASCADE)

#     cluster = models.CharField(
#        max_length=50,
#        default=Cluster.default
#     )

    @classmethod
    def get_admin_url(cls, user):
        realm = cls.get_realm_name(user)
        try:
            czone = Czone.objects.get(realm=realm)
        except Czone.DoesNotExist:
            return ""
        user_domain = czone.user_domain

        return "https://%s/auth/admin/master/console/#/realms/%s/users/%s" % (user_domain, realm, user)

    @classmethod
    def shortuuid(cls, uid):
        return str(uid).split("-")[0]

    @classmethod
    def get_realm_name(cls, user):
        realm = None
        try:
            if isinstance(user, str) or len(str(user)) == 36:
                userObj = get_user_model().objects.get(username=str(user))
            else:
                userObj = user
            realm = userObj.oidc_profile.realm.name
        except Exception:
            realm = None

        return realm

    @classmethod
    def try_czone(cls, user):
        realm = cls.get_realm_name(user)
        czone = Czone.objects.get(realm=realm)
        return czone.domain

    @classmethod
    def try_cname(cls, user):
        return "%s.%s" % ( cls.shortuuid(user), cls.try_czone(user) )

    @classmethod
    def try_cluster(cls, user):
        realm = cls.get_realm_name(user)
        czone = Czone.objects.get(realm=realm)
        return czone.cluster
#         if UserProfile.get_realm_name(user) == "ujcdn":
#             cluster = Cluster.defaultiowa
#         else:
#             cluster = Cluster.default
#         return "%s" % cluster

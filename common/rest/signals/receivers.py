from django.utils import timezone
from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver
from django.conf import settings
from common.rest.middleware.changeLog import get_current_request

from elasticsearch.helpers import bulk
from elasticsearch import Elasticsearch
from common.rest.document import ChangeLogDocument
from elasticsearch.helpers import BulkIndexError


client = Elasticsearch(
    hosts=[settings.ELASTICSEARCH_API_HOST],
    api_key=settings.ELASTICSEARCH_API_KEY
)

CHANGE_LOG_CREATE = "create"
CHANGE_LOG_UPDATE = "update"


@receiver(pre_save)
def capture_old_values(sender, instance, **kwargs):
    if instance.pk:
        try:
            old_instance = sender.objects.get(pk=instance.pk)
            for field in instance._meta.fields:
                old_value = getattr(old_instance, field.attname)
                setattr(instance, f"old_{field.attname}", old_value)
        except sender.DoesNotExist:
            pass


@receiver(post_save)
def track_changes(sender, instance, created, **kwargs):
    request = get_current_request()
    hostname = request.headers.get('Origin') if request else 'Unknown'
    api_endpoint = request.path if request else 'Unknown'
    ip_address = request.ip_address if request else 'Unknown'
    user = request.user.email if request and request.user.is_authenticated and request.user.email else 'Anonymous'
    request_id=request.request_id if request else None

    change_type = CHANGE_LOG_CREATE if created else CHANGE_LOG_UPDATE

    field_names = [field.name for field in sender._meta.get_fields()]

    # Initialize the index
    ChangeLogDocument.init(using=client)

    # Create a list of documents to be indexed
    documents = []
    for field_name in field_names:
        old_value = getattr(instance, f"old_{field_name}", None)
        new_value = getattr(instance, field_name, None)
        if old_value != new_value:
            documents.append(
                ChangeLogDocument(
                    request_id=request_id,
                    model_name=sender.__name__,
                    instance_id=instance.pk,
                    field_name=field_name,
                    old_value=str(old_value),
                    new_value=str(new_value),
                    type=change_type,
                    timestamp=timezone.now(),
                    hostname=hostname,
                    api_endpoint=api_endpoint,
                    user=user,
                    ip_address=ip_address
                )
            )

    # Convert documents to the format required by the bulk helper
    if documents:
        actions = [
            {
                "_index": ChangeLogDocument._index._name,  # Ensure the index name is included
                "_source": doc.to_dict()
            }
            for doc in documents
        ]

        # Use the bulk helper to index documents
        try:
            bulk(client, actions)
        except BulkIndexError as e:
            pass

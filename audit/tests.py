from django.test import TestCase

from audit.models import AuditLog
from pages.models import WhatWeDo


class SoftDeleteTests(TestCase):
    def setUp(self):
        self.obj = WhatWeDo.objects.create(title="Test Activity")

    def test_delete_sets_deleted_at(self):
        self.obj.delete()
        self.obj.refresh_from_db()
        self.assertIsNotNone(self.obj.deleted_at)

    def test_deleted_row_hidden_from_default_manager(self):
        self.obj.delete()
        self.assertFalse(WhatWeDo.objects.filter(id=self.obj.id).exists())

    def test_deleted_row_visible_in_objects_all(self):
        self.obj.delete()
        self.assertTrue(WhatWeDo.objects_all.filter(id=self.obj.id).exists())


class AuditLogTests(TestCase):
    def test_save_creates_create_log(self):
        obj = WhatWeDo.objects.create(title="Audit Me")
        log = AuditLog.objects.get(model_name="WhatWeDo", object_id=obj.id)
        self.assertEqual(log.action, "create")

    def test_update_creates_update_log(self):
        obj = WhatWeDo.objects.create(title="Audit Me")
        AuditLog.objects.filter(model_name="WhatWeDo", object_id=obj.id).delete()
        obj.title = "Renamed"
        obj.save()
        log = AuditLog.objects.get(model_name="WhatWeDo", object_id=obj.id)
        self.assertEqual(log.action, "update")

    def test_save_with_no_audit_skips_log(self):
        obj = WhatWeDo.objects.create(title="No Log")
        AuditLog.objects.filter(model_name="WhatWeDo", object_id=obj.id).delete()
        obj.save(no_audit=True)
        self.assertFalse(
            AuditLog.objects.filter(model_name="WhatWeDo", object_id=obj.id).exists()
        )

    def test_delete_creates_delete_log(self):
        obj = WhatWeDo.objects.create(title="Delete Me")
        AuditLog.objects.filter(model_name="WhatWeDo", object_id=obj.id).delete()
        obj.delete()
        self.assertTrue(
            AuditLog.objects.filter(
                model_name="WhatWeDo", object_id=obj.id, action="delete"
            ).exists()
        )

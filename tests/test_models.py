""" venv/bin/python probemanager/manage.py test bro.tests.test_models --settings=probemanager.settings.dev """
from django.db.utils import IntegrityError
from django.test import TestCase
from django.utils import timezone

from bro.models import Configuration, Bro, SignatureBro, ScriptBro, RuleSetBro


class ConfigurationTest(TestCase):
    fixtures = ['init', 'crontab', 'test-bro-conf']

    @classmethod
    def setUpTestData(cls):
        pass

    def test_conf_bro(self):
        all_conf_bro = Configuration.get_all()
        conf_bro = Configuration.get_by_id(101)
        self.assertEqual(len(all_conf_bro), 1)
        self.assertEqual(conf_bro.name, "test_bro_conf")
        self.assertEqual(conf_bro.my_scripts, "/usr/local/bro/share/bro/site/myscripts.bro")
        self.assertEqual(conf_bro.bin_directory, "/usr/local/bro/bin/")
        self.assertEqual(str(conf_bro), "test_bro_conf")
        conf_bro = Configuration.get_by_id(199)
        self.assertEqual(conf_bro, None)
        with self.assertRaises(AttributeError):
            conf_bro.name
        with self.assertRaises(IntegrityError):
            Configuration.objects.create(name="test_bro_conf")


class RuleSetBroTest(TestCase):
    fixtures = ['init', 'crontab', 'test-bro-signature', 'test-bro-script', 'test-bro-ruleset']

    @classmethod
    def setUpTestData(cls):
        cls.date_now = timezone.now()

    def test_ruleset_bro(self):
        all_ruleset_bro = RuleSetBro.get_all()
        ruleset_bro = RuleSetBro.get_by_id(101)
        self.assertEqual(len(all_ruleset_bro), 1)
        self.assertEqual(ruleset_bro.name, "test_bro_ruleset")
        self.assertEqual(ruleset_bro.description, "")
        self.assertEqual(str(ruleset_bro), "test_bro_ruleset")
        ruleset_bro = RuleSetBro.get_by_id(199)
        self.assertEqual(ruleset_bro, None)
        with self.assertRaises(AttributeError):
            ruleset_bro.name
        with self.assertRaises(IntegrityError):
            RuleSetBro.objects.create(name="test_bro_ruleset",
                                           description="",
                                           created_date=self.date_now
                                           )


class ScriptBroTest(TestCase):
    fixtures = ['init', 'crontab', 'test-bro-script']

    @classmethod
    def setUpTestData(cls):
        cls.date_now = timezone.now()

    def test_script_bro(self):
        all_script_bro = ScriptBro.get_all()
        script_bro = ScriptBro.get_by_id(102)
        self.assertEqual(len(all_script_bro), 1)
        self.assertEqual(script_bro.name, "The hash value of a file transferred over HTTP matched")
        self.assertEqual(script_bro.rev, 0)
        self.assertEqual(script_bro.reference, None)
        self.assertTrue(script_bro.enabled)
        script_bros = ScriptBro.find("Detect file downloads")
        self.assertEqual(script_bros[0].name, "The hash value of a file transferred over HTTP matched")
        self.assertEqual(str(script_bro), "The hash value of a file transferred over HTTP matched")
        script_bro = ScriptBro.get_by_id(199)
        self.assertEqual(script_bro, None)
        with self.assertRaises(AttributeError):
            script_bro.name
        with self.assertRaises(IntegrityError):
            ScriptBro.objects.create(name="The hash value of a file transferred over HTTP matched",
                                          rev=0,
                                          reference="",
                                          rule_full="test",
                                          enabled=True,
                                          created_date=self.date_now
                                          )


class SignatureBroTest(TestCase):
    fixtures = ['init', 'crontab', 'test-bro-signature']

    @classmethod
    def setUpTestData(cls):
        cls.date_now = timezone.now()

    def test_signature_bro(self):
        all_signature_bro = SignatureBro.get_all()
        signature_bro = SignatureBro.get_by_id(101)
        signature_bros = SignatureBro.find("ATTACK-RESPONSES Microsoft cmd.exe banner (reverse-shell originator)")
        self.assertEqual(len(all_signature_bro), 1)
        self.assertEqual(signature_bro.rev, 0)
        self.assertEqual(signature_bro.msg, "ATTACK-RESPONSES Microsoft cmd.exe banner (reverse-shell originator)")
        self.assertEqual(signature_bro.reference, None)
        self.assertTrue(signature_bro.enabled)
        self.assertEqual(signature_bros[0].msg, "ATTACK-RESPONSES Microsoft cmd.exe banner (reverse-shell originator)")
        self.assertEqual(str(signature_bro), "101 : ATTACK-RESPONSES Microsoft cmd.exe banner (reverse-shell originator)")
        signature_bro = SignatureBro.get_by_id(199)
        self.assertEqual(signature_bro, None)
        with self.assertRaises(AttributeError):
            signature_bro.pk
        with self.assertRaises(IntegrityError):
            SignatureBro.objects.create(msg="ATTACK-RESPONSES Microsoft cmd.exe banner (reverse-shell originator)",
                                        reference="",
                                        rule_full="test",
                                        enabled=True,
                                        created_date=self.date_now
                                        )


class BroTest(TestCase):
    fixtures = ['init', 'crontab', 'test-core-secrets', 'test-bro-signature', 'test-bro-script', 'test-bro-ruleset',
                'test-bro-conf', 'test-bro-bro']

    @classmethod
    def setUpTestData(cls):
        pass

    def test_bro(self):
        all_bro = Bro.get_all()
        bro = Bro.get_by_id(101)
        self.assertEqual(len(all_bro), 1)
        self.assertEqual(bro.name, "test_instance_bro")
        self.assertEqual(str(bro), "test_instance_bro : ")
        bro = Bro.get_by_id(199)
        self.assertEqual(bro, None)
        with self.assertRaises(AttributeError):
            bro.name
        with self.assertRaises(IntegrityError):
            Bro.objects.create(name="test_instance_bro")

    def test_test(self):
        bro = Bro.get_by_id(101)
        response = bro.server.test()
        self.assertTrue(response)
        response = bro.server.test_root()
        self.assertTrue(response)

    def test_reload(self):
        bro = Bro.get_by_id(101)
        response = bro.reload()
        self.assertTrue(response['status'])

    def test_deploy_conf(self):
        bro = Bro.get_by_id(101)
        response = bro.deploy_conf()
        self.assertTrue(response['status'])

    def test_deploy_rules(self):
        bro = Bro.get_by_id(101)
        response = bro.deploy_rules()
        self.assertTrue(response['status'])
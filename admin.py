import logging
import os
import time

from django import forms
from django.conf import settings
from django.conf.urls import url
from django.contrib import admin
from django.contrib import messages
from django.contrib.admin.helpers import ActionForm
from django.http import HttpResponseRedirect
from django_celery_beat.models import PeriodicTask, CrontabSchedule

from .models import Bro, SignatureBro, ScriptBro, RuleSetBro, Configuration

logger = logging.getLogger(__name__)


class MarkedRuleMixin(admin.ModelAdmin):
    def make_enabled(self, request, queryset):
        rows_updated = queryset.update(enabled=True)
        if rows_updated == 1:
            message_bit = "1 rule was"
        else:
            message_bit = "%s rules were" % rows_updated
        self.message_user(request, "%s successfully marked as enabled." % message_bit)

    def make_disabled(self, request, queryset):
        rows_updated = queryset.update(enabled=False)
        if rows_updated == 1:
            message_bit = "1 rule was"
        else:
            message_bit = "%s rules were" % rows_updated
        self.message_user(request, "%s successfully marked as disabled." % message_bit)

    make_enabled.short_description = "Mark rule as enabled"
    make_disabled.short_description = "Mark rule as disabled"


class RuleSetBroAdmin(admin.ModelAdmin):
    def test_signatures(self, request, obj):
        test = True
        errors = list()
        for ruleset in obj:
            for signature in ruleset.signatures.all():
                response = signature.test()
                if not response['status']:
                    test = False
                    errors.append(str(signature) + " : " + str(response['errors']))
        if test:
            messages.add_message(request, messages.SUCCESS, "Test signatures OK")
        else:
            messages.add_message(request, messages.ERROR, "Test signatures failed ! " + str(errors))

    actions = [test_signatures]


class ScriptBroAdmin(MarkedRuleMixin, admin.ModelAdmin):
    class Media:
        js = (
            'bro/js/mask-ruleset-field.js',
        )

      def add_ruleset(self, request, queryset):
        ruleset_id = request.POST['ruleset']
        if ruleset_id:
            ruleset = RuleSetBro.get_by_id(ruleset_id)
            for script in queryset:
                ruleset.scripts.add(script)
            ruleset.save()

    add_ruleset.short_description = 'Add ruleset'

    def remove_ruleset(self, request, queryset):
        ruleset_id = request.POST['ruleset']
        if ruleset_id:
            ruleset = RuleSetBro.get_by_id(ruleset_id)
            for script in queryset:
                ruleset.scripts.remove(script)
            ruleset.save()

    remove_ruleset.short_description = 'Remove ruleset'

    class UpdateActionForm(ActionForm):
        ruleset = forms.ModelChoiceField(queryset=RuleSetBro.get_all(), empty_label="Select a ruleset",
                                         required=False)

    def test_scripts(self, request, obj):
        test = True
        errors = list()
        for script in obj:
            response = script.test_all()
            if not response['status']:
                test = False
                errors.append(str(script) + " : " + str(response['errors']))
        if test:
            messages.add_message(request, messages.SUCCESS, "Test scripts OK")
        else:
            messages.add_message(request, messages.ERROR, "Test scripts failed ! " + str(errors))

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        response = obj.test_all()
        if response['status']:
            messages.add_message(request, messages.SUCCESS, "Test script OK")
        else:
            messages.add_message(request, messages.ERROR, "Test script failed ! " + str(response['errors']))

    search_fields = ('rule_full',)
    list_filter = ('enabled', 'created_date', 'updated_date', 'rulesetbro__name')
    list_display = ('id', 'name', 'enabled')
    actions = [MarkedRuleMixin.make_enabled, MarkedRuleMixin.make_disabled,
               add_ruleset, remove_ruleset, test_scripts]


class SignatureBroAdmin(MarkedRuleMixin, admin.ModelAdmin):
    class Media:
        js = (
            'bro/js/mask-ruleset-field.js',
        )

    def add_ruleset(self, request, queryset):
        ruleset_id = request.POST['ruleset']
        if ruleset_id:
            ruleset = RuleSetBro.get_by_id(ruleset_id)
            for signature in queryset:
                ruleset.signatures.add(signature)
            ruleset.save()

    add_ruleset.short_description = 'Add ruleset'

    def remove_ruleset(self, request, queryset):
        ruleset_id = request.POST['ruleset']
        if ruleset_id:
            ruleset = RuleSetBro.get_by_id(ruleset_id)
            for signature in queryset:
                ruleset.signatures.remove(signature)
            ruleset.save()

    remove_ruleset.short_description = 'Remove ruleset'

    class UpdateActionForm(ActionForm):
        ruleset = forms.ModelChoiceField(queryset=RuleSetBro.get_all(), empty_label="Select a ruleset",
                                         required=False)

    def test_signatures(self, request, obj):
        test = True
        errors = list()
        for signature in obj:
            response = signature.test_all()
            if not response['status']:
                test = False
                errors.append(str(signature) + " : " + str(response['errors']))
        if test:
            messages.add_message(request, messages.SUCCESS, "Test signatures OK")
        else:
            messages.add_message(request, messages.ERROR, "Test signatures failed ! " + str(errors))

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        response = obj.test_all()
        if response['status']:
            messages.add_message(request, messages.SUCCESS, "Test signature OK")
        else:
            messages.add_message(request, messages.ERROR, "Test signature failed ! " + str(response['errors']))

    search_fields = ('rule_full',)
    list_filter = ('enabled', 'created_date', 'updated_date', 'rulesetbro__name')
    list_display = ('sid', 'msg', 'enabled')
    action_form = UpdateActionForm
    actions = [MarkedRuleMixin.make_enabled, MarkedRuleMixin.make_disabled,
               add_ruleset, remove_ruleset, test_signatures]


admin.site.register(Bro)
admin.site.register(SignatureBro, SignatureBroAdmin)
admin.site.register(ScriptBro, ScriptBroAdmin)
admin.site.register(RuleSetBro, RuleSetBroAdmin)
admin.site.register(Configuration)

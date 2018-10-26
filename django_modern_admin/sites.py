from functools import update_wrapper
from weakref import WeakSet

from django.apps import apps
from django.contrib import admin
from django.contrib.admin import actions
from django.contrib.auth import logout
from django.conf import settings
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.template.response import TemplateResponse
from django.urls import NoReverseMatch, reverse
from django.utils.text import capfirst
from django.utils.translation import gettext_lazy
from django.views.decorators.cache import never_cache

import os, datetime, json, random


all_sites = WeakSet()


class ModernAdminSite(admin.AdminSite):
    if hasattr(settings, 'SITE_TITLE'):
        site_title = settings.SITE_TITLE
    else:
        site_title = gettext_lazy('Site Administration')

    # Text to put in each page's <h1>.
    if hasattr(settings, 'SITE_HEADER'):
        site_header = settings.SITE_HEADER
    else:
        site_header = gettext_lazy('Administration')
    # Text to put at the top of the admin index page.
    if hasattr(settings, 'INDEX_TITLE'):
        index_title = settings.INDEX_TITLE
    else:
        index_title = gettext_lazy('Site administration')

    site_url = '/'
    userCache = ''

    dashboardDateType = 'Day'
    date = datetime.date.today()
    start_this_week = date - datetime.timedelta(date.weekday())
    start_last_week = date - datetime.timedelta(date.weekday() + 7)
    end_this_week = start_this_week + datetime.timedelta(7)
    end_last_week = date - datetime.timedelta(date.weekday() + 1)

    def __init__(self, name='admin'):
        settings.STATICFILES_DIRS += ['%s/static' % os.path.abspath(os.path.dirname(__file__))]
        settings.TEMPLATES[0]['DIRS'] += os.path.join(os.path.abspath(os.path.dirname(__file__)), 'templates')
        self._registry = {}
        self.name = name
        self._actions = {'delete_selected': actions.delete_selected}
        self._global_actions = self._actions.copy()
        all_sites.add(self)

    def get_django_modern_admin_urls(self):
        from django.urls import include, path, re_path
        from django.contrib.contenttypes import views as contenttype_views

        def wrap(view, cacheable=False):
            def wrapper(*args, **kwargs):
                return self.admin_view(view, cacheable)(*args, **kwargs)
            wrapper.admin_site = self
            return update_wrapper(wrapper, view)

        urlpatterns = self.get_urls()

        urlpatterns += [
            path('', wrap(self.index), name='index'),
            path(
                'r/<int:content_type_id>/<path:object_id>/',
                wrap(contenttype_views.shortcut),
                name='view_on_site',
            ),
            path('completeTask/', self.completeTask, name='completeTask'),
            path('lockAccount/', self.lockAccount, name='lockAccount'),
            path('changeDashboardDate/', self.changeDashboardDateType, name='changeDashboardDate'),
            path('logoutNGoLogin/', self.logoutNGoLogin, name='logoutNGoLogin'),
        ]

        valid_app_labels = []
        for model, model_admin in self._registry.items():
            urlpatterns += [
                path('%s/%s/' % (model._meta.app_label, model._meta.model_name), include(model_admin.urls)),
            ]
            if model._meta.app_label not in valid_app_labels:
                valid_app_labels.append(model._meta.app_label)

        if valid_app_labels:
            regex = r'^(?P<app_label>' + '|'.join(valid_app_labels) + ')/$'
            urlpatterns += [
                re_path(regex, wrap(self.app_index), name='app_list'),
            ]
        return urlpatterns

    @property
    def urls(self):
        return self.get_django_modern_admin_urls(), 'admin', self.name

    def each_context(self, request):
        script_name = request.META['SCRIPT_NAME']
        site_url = script_name if self.site_url == '/' and script_name else self.site_url
        from django_modern_admin.models import AdminNavLogo, AdminLoginLogo
        if AdminNavLogo.objects.all().count() > 0:
            adminLogo = AdminNavLogo.objects.first()
            site_logo = {
                'type': 'fromModel',
                'url': '%s' % adminLogo.logo.url
            }
        else:
            site_logo = {
                'type': 'fromSettings',
                'url': 'django_modern_admin/logo/default.png'
            }
        if hasattr(settings, 'FOOTERCOPYRIGHT'):
            footerCopyRight = settings.FOOTERCOPYRIGHT
        else:
            footerCopyRight = 'Django'
        if AdminLoginLogo.objects.all().count() > 0:
            login_logo = AdminLoginLogo.objects.first().logo.url
        else:
            login_logo = settings.STATIC_URL + 'django_modern_admin/logo/login_logo.png'
        return {
            'site_title': self.site_title,
            'site_header': self.site_header,
            'site_url': site_url,
            'site_logo': site_logo,
            'login_logo': login_logo,
            'footerCopyRight': footerCopyRight,
            'has_permission': self.has_permission(request),
            'available_apps': self.get_app_list(request),
        }

    def logoutNGoLogin(self, request):
        logout(request)
        return redirect(reverse('admin:login'))

    def lockAccount(self, request):
        from .models import AdminProfile
        adminAvatar = None
        if request.user.is_authenticated:
            adminProfile = AdminProfile.objects.filter(user=request.user)
            if adminProfile.first().avatar:
                adminAvatar = adminProfile.first().avatar.url
            self.userCache = request.user.get_username()
            logout(request)
        return self.login(request, {'userCache': self.userCache, 'adminAvatar': adminAvatar})

    def changeDashboardDateType(self, request):
        if request.method == 'POST':
            if request.POST.get('dateType'):
                self.dashboardDateType = request.POST.get('dateType')
                return HttpResponse(json.dumps({'result': 'success'}), content_type='application/json')

    def _build_app_dict(self, request, label=None):
        app_dict = {}

        if label:
            models = {
                m: m_a for m, m_a in self._registry.items()
                if m._meta.app_label == label
            }
        else:
            models = self._registry

        for model, model_admin in models.items():
            app_label = model._meta.app_label

            has_module_perms = model_admin.has_module_permission(request)
            if not has_module_perms:
                continue

            perms = model_admin.get_model_perms(request)

            if True not in perms.values():
                continue

            info = (app_label, model._meta.model_name)
            model_dict = {
                'name': capfirst(model._meta.verbose_name_plural),
                'object_name': model._meta.object_name,
                'perms': perms,
            }
            if hasattr(settings, 'MODEL_ICONS'):
                if '%s_icon' % model.__name__ in settings.MODEL_ICONS:
                    model_dict.update({
                        'icon': settings.MODEL_ICONS[model.__name__ + '_icon']
                    })
                else:
                    model_dict.update({
                        'icon': 'mdi-hardware-keyboard-arrow-right'
                    })
            else:
                model_dict.update({
                    'icon': 'mdi-hardware-keyboard-arrow-right'
                })
            if perms.get('change'):
                try:
                    model_dict['admin_url'] = reverse('admin:%s_%s_changelist' % info, current_app=self.name)
                except NoReverseMatch:
                    pass
            if perms.get('add'):
                try:
                    model_dict['add_url'] = reverse('admin:%s_%s_add' % info, current_app=self.name)
                except NoReverseMatch:
                    pass

            if app_label in app_dict:
                app_dict[app_label]['models'].append(model_dict)
            else:
                app_dict[app_label] = {
                    'name': apps.get_app_config(app_label).verbose_name,
                    'app_label': app_label,
                    'app_url': reverse(
                        'admin:app_list',
                        kwargs={'app_label': app_label},
                        current_app=self.name,
                    ),
                    'has_module_perms': has_module_perms,
                    'models': [model_dict],
                }
                if hasattr(settings, 'APP_ICONS'):
                    if '%s_icon' % app_label in settings.APP_ICONS:
                        app_dict[app_label].update({
                            'icon': settings.APP_ICONS[app_label + '_icon']
                        })
                    else:
                        app_dict[app_label].update({
                            'icon': 'mdi-action-subject'
                        })
                else:
                    app_dict[app_label].update({
                        'icon': 'mdi-action-subject'
                    })

        if label:
            return app_dict.get(label)
        return app_dict

    def get_app_list(self, request):
        app_dict = self._build_app_dict(request)
        app_list = sorted(app_dict.values(), key=lambda x: x['name'].lower())
        for app in app_list:
            app['models'].sort(key=lambda x: x['name'])

        return app_list

    def completeTask(self, request):
        if request.method == 'POST':
            from .models import AdminTasks
            try:
                task = AdminTasks.objects.get(id=request.POST.get('id'))
            except NoReverseMatch:
                return HttpResponse(json.dumps({'result': 'failure', 'error': 'Task not found'}, ensure_ascii=False), content_type='application/json; charset=utf-8')
            if request.POST.get('isDone') == '1':
                task.isDone = True
                task.save()
                return render(request, 'admin/tasks.html', {'tasks': AdminTasks.objects.filter(user=request.user, isDone=False).order_by('date')})

    def getModelIfExist(self, appList, appName, modelName):
        for app in appList:
            if appName == app['name']:
                for appModel in app['models']:
                    if modelName == appModel['object_name']:
                        return apps.get_model(appName, modelName)

    def getModelContext(self, app_list, context, side, modelSide):
        app_name = modelSide['modelName'].split('.')[0]
        model_name = modelSide['modelName'].split('.')[1]
        model = self.getModelIfExist(app_list, app_name, model_name)
        if model:
            model = model.objects.all()
            if 'filterField' in modelSide and 'filterValue' in modelSide:
                model = model.filter(**{modelSide['filterField']: modelSide['filterValue']})
            if 'listFields' in modelSide:
                context.update({'model_%s_list_fields' % side: modelSide['listFields']})
            if 'orderField' in modelSide:
                context.update({'model_%s_order_field' % side: modelSide['orderField']})
            if 'modelIcon' in modelSide:
                context.update({'model_%s_icon' % side: modelSide['modelIcon']})
            context.update({'model_%s' % side: model})

        return context

    def getDoughnutValues(self, chartModel, chartVar):
        doughnutChartValues = chartModel.only(chartVar['doughnutChartNameField'], chartVar['doughnutChartValueField'])
        itemNames = []
        doughnutChartContext = []
        for index, item in enumerate(doughnutChartValues):
            itemName = getattr(item, chartVar['doughnutChartNameField'])
            itemValue = getattr(item, chartVar['doughnutChartValueField'])
            if itemName not in itemNames:
                itemNames.append(itemName)
                doughnutChartContext.append({'doughnutNameField': itemName,
                                             'doughnutValueField': itemValue,
                                             'doughnutColorValue': "%06x" % random.randint(0, 0xFFFFFF)})
            else:
                for index, item in enumerate(doughnutChartContext):
                    if item['doughnutNameField'] == itemName:
                        item['doughnutValueField'] += itemValue
        return doughnutChartContext

    def getTwoWeekValues(self, startDay, chartModel, chartVar):
        weekDayValues = {}
        for day in range(7):
            weekDayTotal = 0
            for chartValues in chartModel:
                weekDay = startDay + datetime.timedelta(day)
                chartValuesDays = getattr(chartValues, chartVar['baseChartDateField'])
                if weekDay.day == chartValuesDays.day:
                    weekDayTotal += getattr(chartValues, chartVar['baseChartLineField'])
                    weekDayValues.update({'weekDay%s' % day: weekDay.weekday(),
                                          'weekDay%sTotal' % day: weekDayTotal})
                else:
                    weekDayValues.update({'weekDay%s' % day: weekDay.weekday(),
                                          'weekDay%sTotal' % day: weekDayTotal})
        return weekDayValues

    def topLeftChartByDay(self, context, baseChartModel, chartVar):

        if 'baseChartDateField' in chartVar:
            dateRange = '%s__range' % chartVar['baseChartDateField']
            ChartLastWeek = baseChartModel.objects.filter(**{dateRange: [self.start_last_week, self.end_last_week]})
            ChartThisWeek = baseChartModel.objects.filter(**{dateRange: [self.start_this_week, self.end_this_week]})
            context.update({'topLeftChartThisWeek': ChartThisWeek, 'topLeftChartDateField': chartVar['baseChartDateField']})
        if 'baseChartLineField' in chartVar:
            lastWeekValues = self.getTwoWeekValues(self.start_last_week, ChartLastWeek, chartVar)
            thisWeekValues = self.getTwoWeekValues(self.start_this_week, ChartThisWeek, chartVar)
            context.update({'topLeftChartThisWeekValues': thisWeekValues, 'topLeftChartLastWeekValues': lastWeekValues})
        if 'doughnutChartNameField' in chartVar:
            doughnutContext = self.getDoughnutValues(ChartThisWeek, chartVar)
            context.update({'doughnutChartValues': doughnutContext})
        if 'tableFieldsForDay' in chartVar:
            context.update({'topLeftChartTableFields': chartVar['tableFieldsForDay']})
        return context

    def getMonthsValues(self, year, chartModel, chartVar):
        monthValues = {}
        for month in range(1, 13):
            monthTotal = 0
            for chartValues in chartModel:
                chartValuesDays = getattr(chartValues, chartVar['baseChartDateField'])
                if year == chartValuesDays.year and month == chartValuesDays.month:
                    monthTotal += getattr(chartValues, chartVar['baseChartLineField'])
                    monthValues.update({'month%s' % month: month, 'month%sTotal' % month: monthTotal})
                else:
                    monthValues.update({'month%s' % month: month, 'month%sTotal' % month: monthTotal})
        return monthValues

    def topLeftChartByMonth(self, context, baseChartModel, chartVar):
        date = datetime.date.today()
        if 'baseChartDateField' in chartVar:
            dateYear = '%s__year' % chartVar['baseChartDateField']
            baseChartLastYear = baseChartModel.objects.filter(**{dateYear: date.year - 1})
            baseChartThisYear = baseChartModel.objects.filter(**{dateYear: date.year})
            context.update({'topLeftChartThisYear': baseChartThisYear, 'topLeftChartDateField': chartVar['baseChartDateField']})
        if 'baseChartLineField' in chartVar:
            lastYearValues = self.getMonthsValues(date.year - 1, baseChartLastYear, chartVar)
            thisYearValues = self.getMonthsValues(date.year, baseChartThisYear, chartVar)
            context.update({'topLeftChartThisYearValues': thisYearValues, 'topLeftChartLastYearValues': lastYearValues})
        if 'doughnutChartNameField' in chartVar:
            doughnutContext = self.getDoughnutValues(baseChartThisYear, chartVar)
            context.update({'doughnutChartValues': doughnutContext})
        if 'tableFieldsForMonth' in chartVar:
            context.update({'topLeftChartTableFields': chartVar['tableFieldsForMonth']})
        return context

    def topLeftChart(self, app_list, context, chartVar):
        if 'title' in chartVar:
            context.update({'leftChartTitle': chartVar['title']})
        if 'baseChartModel' in chartVar:
            app_name = chartVar['baseChartModel'].split(".")[0]
            model_name = chartVar['baseChartModel'].split(".")[1]
            baseChartModel = self.getModelIfExist(app_list, app_name, model_name)
            context.update({'topLeftChartModelVerbose': baseChartModel._meta.verbose_name_plural.title()})
            if self.dashboardDateType == 'Day':
                self.topLeftChartByDay(context, baseChartModel, chartVar)
            elif self.dashboardDateType == 'Month':
                self.topLeftChartByMonth(context, baseChartModel, chartVar)
        return context

    def miniBarChart(self, app_list, chartVar):
        if 'chartModel' in chartVar:
            if chartVar['chartModel'] == 'auth.User':
                from django.contrib.auth.models import User
                chartModel = User
            else:
                app_name = chartVar['chartModel'].split(".")[0]
                model_name = chartVar['chartModel'].split(".")[1]
                chartModel = self.getModelIfExist(app_list, app_name, model_name)
        if 'chartModelDateField' in chartVar:
            chartModelValues = []
            today = datetime.date.today()
            if self.dashboardDateType == 'Day':
                chartModel = chartModel.objects.filter(**{'%s__month' % chartVar['chartModelDateField']: today.month})
                for day in range(today.day - 21, today.day):
                    chartModelValues.append({'dataSet': chartModel.filter(**{'%s__day' % chartVar['chartModelDateField']: day}).count(),
                                             'chartModel': chartModel,
                                             'icon': (chartVar['icon'] if 'icon' in chartVar else 'mdi-action-assessment'),
                                             'color': (chartVar['color'] if 'color' in chartVar else 'green')})
                return chartModelValues
            else:
                chartModel = chartModel.objects.filter(**{'%s__year' % chartVar['chartModelDateField']: today.year})
                for month in range(1, 13):
                    chartModelValues.append({'dataSet': chartModel.filter(**{'%s__month' % chartVar['chartModelDateField']: month}).count(),
                                             'chartModel': chartModel,
                                             'icon': (chartVar['icon'] if 'icon' in chartVar else 'mdi-action-assessment'),
                                             'color': (chartVar['color'] if 'color' in chartVar else 'green')})
                return chartModelValues

    @never_cache
    def index(self, request, extra_context=None):
        from .service_account import get_access_token
        app_list = self.get_app_list(request)
        context = dict(
            self.each_context(request),
            title=self.index_title,
            app_list=app_list,
            access_token=get_access_token(),
            dashboardDateType=self.dashboardDateType
        )
        from .models import AdminTasks
        if hasattr(settings, 'MODEL_LIST'):
            if 'left' in settings.MODEL_LIST:
                self.getModelContext(app_list, context, 'left', settings.MODEL_LIST['left'])
            if 'right' in settings.MODEL_LIST:
                self.getModelContext(app_list, context, 'right', settings.MODEL_LIST['right'])
        if hasattr(settings, 'TOP_LEFT_CHART'):
            self.topLeftChart(app_list, context, settings.TOP_LEFT_CHART)
        if hasattr(settings, 'MINI_BAR_CHART'):
            miniChartModelArr = []
            for miniChart in settings.MINI_BAR_CHART:
                miniChartModelArr.append(self.miniBarChart(app_list, settings.MINI_BAR_CHART[miniChart]))
            context.update(dict(miniBarChartModel=miniChartModelArr))
        if hasattr(settings, 'VECTOR_MAP_JS_URL'):
            context.update({'vectorMapJsURL': settings.VECTOR_MAP_JS_URL})
        if hasattr(settings, 'GOOGLE_ANALYTICS_ID'):
            context.update({'googleAnalyticsID': settings.GOOGLE_ANALYTICS_ID})
        context.update(dict(tasks=AdminTasks.objects.filter(user=request.user, isDone=False).order_by('date'),))

        request.current_app = self.name

        return TemplateResponse(request, 'admin/index.html', context)


site = ModernAdminSite()
admin.site = site
admin.sites.site = site


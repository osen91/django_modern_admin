from django import template
from django.contrib.contenttypes.models import ContentType
from django.urls import reverse
from django.utils.html import conditional_escape
from django.utils.safestring import mark_safe
from django.utils.translation import gettext as _, gettext_lazy
import calendar, types, datetime
import django_modern_admin as admin

register = template.Library()


@register.simple_tag(takes_context=True)
def get_menu(context):
    return admin.site.get_app_list(context['request'])


@register.filter
def month_name(month_number):
    return calendar.month_name[month_number]


@register.simple_tag()
def getUrlForRecord(record):
    return reverse('admin:%s_%s_change' % (record._meta.app_label, record._meta.model_name), args=(record.id,))


@register.simple_tag()
def getRecordField(record, fieldName):
    return '%s: %s' % (record._meta.get_field(fieldName).verbose_name.title(), getattr(record, fieldName))

@register.filter()
def list_index_from_value(list, value):
    print(list)
    print(value)
    return list[value]

@register.inclusion_tag('admin/baseChartTable.html')
def getChartTableByDay(tableFields, model, dateType, dateField):
    if model:
        verboseNames = []
        tableValues = []
        dates = [_("MON"), _("TUE"), _("WED"), _("THU"), _("FRI"), _("SAT"), _("SUN")]
        for day in range(7):
            dailyRecords = model.filter(**{'%s__week_day' % dateField: ((day + 1) % 7) + 1})
            tableValues.append({'dateField': dates[day]})
            fieldValues = []
            for dailyIndex, dailyRecord in enumerate(dailyRecords):
                for tableIndex, tableField in enumerate(tableFields):
                    verboseName = dailyRecord._meta.get_field(tableField).verbose_name.title()
                    if dailyIndex == 0:
                        fieldValues.append(getattr(dailyRecord, tableField))
                    else:
                        fieldValues[tableIndex] += getattr(dailyRecord, tableField)
                    if verboseName not in verboseNames:
                        verboseNames.append(verboseName)
            tableValues[day].update({'tableValue': fieldValues})
        return {'dates': dates, 'verboseNames': verboseNames, 'dateType': dateType, 'tableValues': tableValues}

@register.inclusion_tag('admin/baseChartTable.html')
def getChartTableByMonth(tableFields, model, dateType, dateField):
    verboseNames = []
    tableValues = []
    dates = [_("JAN"), _("FEB"), _("MAR"), _("APR"), _("MAY"), _("JUN"), _("JUL"), _("AUG"), _("SEP"), _("OCT"), _("NOV"), _("DEC")]
    for month in range(12):
        monthlyRecords = model.filter(**{'%s__month' % dateField: month})
        tableValues.append({'dateField': dates[month]})
        print(monthlyRecords)
        fieldValues = []
        for monthlyIndex, monthlyRecord in enumerate(monthlyRecords):
            for tableIndex, tableField in enumerate(tableFields):
                verboseName = monthlyRecord._meta.get_field(tableField).verbose_name.title()
                print("%s: %s" % (month, monthlyRecord.orderDate))
                if monthlyIndex == 0:
                    fieldValues.append(getattr(monthlyRecord, tableField))
                else:
                    fieldValues[tableIndex] += getattr(monthlyRecord, tableField)
                if verboseName not in verboseNames:
                    verboseNames.append(verboseName)
        tableValues[month].update({'tableValue': fieldValues})
    return {'dates': dates, 'verboseNames': verboseNames, 'dateType': dateType, 'tableValues': tableValues}

@register.inclusion_tag('admin/miniBarChartTemp.html')
def getMiniBarChart(miniChart, loopCounter, dateType):
    dataArr = []
    context = {'loopCounter': loopCounter, 'dateType': dateType}
    for data in miniChart:
        context.update({'verboseName': data['chartModel'].first()._meta.verbose_name.title(),
                        'color': data['color'], 'chartIcon': data['icon']})
        dataArr.append(data['dataSet'])
    lastValue = dataArr[len(dataArr) - 1]
    context.update({'lastValue': lastValue})
    prevValue = dataArr[len(dataArr) - 2]
    lastMinusPrev = lastValue - prevValue
    if prevValue != 0:
        result = lastMinusPrev / prevValue
        result = result * 100
        context.update({'result': result})
        if result > 0:
            context.update({'arrowIcon': 'mdi-action-trending-up'})
        elif result == 0:
            context.update({'arrowIcon': 'mdi-action-trending-neutral'})
        else:
            context.update({'arrowIcon': 'mdi-action-trending-down'})
    else:
        result = (prevValue + lastValue) * 100
        context.update({'result': result, 'arrowIcon': 'mdi-action-trending-neutral'})
    return context

@register.simple_tag()
def getMiniChartDatas(dataSet):
    dataSetArr = []
    for data in dataSet:
        dataSetArr.append(data['dataSet'])
    return dataSetArr

@register.simple_tag()
def getModelOrderByVerboseName(model, field):
    if model:
        model = model.first()
        return model._meta.get_field(field).verbose_name.title()


@register.simple_tag()
def getModelVerboseName(model):
    if model:
        model = model.first()
        return model._meta.verbose_name_plural

@register.simple_tag()
def getMaxOfQuerySet(qs):
    list_result = [entry for entry in qs]
    return max(list_result)

@register.simple_tag()
def convertModelToList(model):
    list_result = [entry for entry in model]
    return list_result

@register.simple_tag()
def getDayShortName():
    days = [_("MON"), _("TUE"), _("WED"), _("THU"), _("FRI"), _("SAT"), _("SUN")]
    return mark_safe(days)

@register.simple_tag()
def getMonthShortName():
    months = [_("JAN"), _("FEB"), _("MAR"), _("APR"), _("MAY"), _("JUN"), _("JUL"), _("AUG"), _("SEP"), _("OCT"), _("NOV"), _("DEC")]
    return mark_safe(months)

@register.simple_tag()
def getChartValues(list, dateType):
    totalList = []
    if dateType == 'Day':
        for day in range(7):
            if 'weekDay%s' % day in list:
                if list['weekDay%s' % day] == day:
                    totalList.append(list['weekDay%sTotal' % day])
            else:
                totalList.append(0)
    else:
        for month in range(1, 13):
            if 'month%s' % month in list:
                if list['month%s' % month] == month:
                    totalList.append(list['month%sTotal' % month])
            else:
                totalList.append(0)
    return totalList


@register.filter(is_safe=True, needs_autoescape=True)
def deleteList(value, autoescape=True):
    """
    Recursively take a self-nested list and return an HTML unordered list --
    WITHOUT opening and closing <ul> tags.

    Assume the list is in the proper format. For example, if ``var`` contains:
    ``['States', ['Kansas', ['Lawrence', 'Topeka'], 'Illinois']]``, then
    ``{{ var|unordered_list }}`` returns::

        <li>States
        <ul>
                <li>Kansas
                <ul>
                        <li>Lawrence</li>
                        <li>Topeka</li>
                </ul>
                </li>
                <li>Illinois</li>
        </ul>
        </li>
    """
    if autoescape:
        escaper = conditional_escape
    else:
        def escaper(x):
            return x

    def walk_items(item_list):
        item_iterator = iter(item_list)
        try:
            item = next(item_iterator)
            while True:
                try:
                    next_item = next(item_iterator)
                except StopIteration:
                    yield item, None
                    break
                if isinstance(next_item, (list, tuple, types.GeneratorType)):
                    try:
                        iter(next_item)
                    except TypeError:
                        pass
                    else:
                        yield item, next_item
                        item = next(item_iterator)
                        continue
                yield item, None
                item = next_item
        except StopIteration:
            pass

    def list_formatter(item_list, tabs=1):
        indent = '\t' * tabs
        output = []
        for item, children in walk_items(item_list):
            sublist = ''
            if children:
                sublist = '\n%s<ul class="collection">\n%s\n%s</ul>\n%s' % (
                    indent, list_formatter(children, tabs + 1), indent, indent)
            output.append('%s<li class="collection-item">%s%s</li>' % (
                indent, escaper(item), sublist))
        return '\n'.join(output)

    return mark_safe(list_formatter(value))
import datetime

from django.contrib import admin
from django.contrib import messages
# Register your models here.
# from django.utils.html import format_html
from django.utils.translation import ugettext_lazy
# from django_extensions.admin import ForeignKeyAutocompleteTabularInline
from .models import Drug,Prescription,Medication
from . import tools


class MedicationInline(admin.TabularInline):
    model = Medication
    extra = 0
    max_num = 15
    verbose_name = "药品"
    verbose_name_plural = "药方（该处方开出的所有药品）"
    fk_name = "medicine_prescription"
    fields = [ 'id', 'medicine_drug','sale_amount','sale_mode']
    # related_search_fields = {
    #     'medicine_drug': ('id','drug_name','mnemonic_code','manufacturer','specification','unit','serial_number','validity_period','property_classification','function_classification'),
    # }
    autocomplete_fields = ['medicine_drug']

    show_change_link = True
    show_full_result_count = True
    readonly_fields = ['id','get_stock_num']


    def id(self, obj):
        if obj.id is None:
            a = Medication.objects.all().order_by('-id')[:1]
            if a:
                return a[0].id + 1
            else:
                return 0
        else:
            return obj.id

    def get_stock_num(self,obj):
        if obj:
            return obj.stock_num
        else:
            return 0


class PrescriptionAdmin(admin.ModelAdmin):
    # 每页显示15条数据
    list_per_page = 15

    # 在底部显示控制选项
    actions_on_bottom = False
    # 在顶部显示控制选项
    actions_on_top = True

    # 搜索框
    search_fields = [ 'id', 'patient_name','patient_gender',
                     'patient_age', 'illness_description', 'create_date','doctor_name']

    fieldsets = [
        ('处方基本信息', {'fields': ['get_id', 'doctor_name', 'treatment_cost', 'create_date']}),
        ('患者信息', {'fields': ['patient_name', 'patient_gender', 'patient_age', 'illness_description']}),
        ('药方总费用', {'fields': ['get_total_sale_cost','get_total_retail_cost','get_total_wholesale_cost']}),

    ]
    readonly_fields = ['get_id','get_total_sale_cost','get_total_retail_cost','get_total_wholesale_cost']
    # 侧边栏过滤框
    list_filter = ['create_date','patient_name']

    list_display = ['id', 'patient_name', 'patient_gender', 'patient_age','treatment_cost','get_total_sale_cost','get_total_retail_cost','get_total_wholesale_cost','create_date','doctor_name']

    actions = ['get_sale_sum']

    inlines = [
        MedicationInline,

    ]

    def save_formset(self, request, form, formset, change):
        try:
            flag = True
            for f in formset.forms:
                obj = f.instance
                if not obj.medicine_drug:
                    messages.add_message(request, messages.ERROR, '存在空药方，请检查药品的选择')
                    flag = False
                elif obj.sale_amount > obj.medicine_drug.stock_num:
                    messages.add_message(request, messages.ERROR, obj.medicine_drug.drug_name
                                         + '【' + obj.medicine_drug.manufacturer + '】'
                                         + '库存不足！请查看该药品的库存。')
                    flag = False
            if flag:
                formset.save()
            else:
                formset.save(commit=False)
        except:
            messages.add_message(request, messages.ERROR, '存在未选择药品的药方，请检查药品的选择')

            formset.save(commit=False)


    def get_sale_sum(self,request,queryset):
        total_sale = 0

        for obj in queryset:
            total_sale += obj.get_total_sale_cost()
            pass
        total_sale = tools.round_up(total_sale)
        self.message_user(request,'选中的'+str(len(queryset))+'个处方的总价为：'+str(total_sale)+'元')

    get_sale_sum.short_description = '统计所选处方的总价'

    # 自定义gender显示field  [供参考]
    # def colored_gender(self, obj):  # 自定义函数，包含两个参数，obj代表数据对象
    #     color = ''
    #     if obj.gender == -1:  # 女
    #         color = '#12d012'
    #     elif obj.gender == 0:  # 未知
    #         color = 'red'
    #     elif obj.gender == 1:  # 男
    #         color = 'yellow'
    #     # 这行中的get_gender_display()函数为django model自带的特殊方法，具体名称为get_FIELD_display()
    #     # 功能是获取FIELD列的显示字符。特别地，对于有choices选项的field有效（其会返回choices中的对应字符）。
    #     # format_html函数使得后台显示时不会按照字符串显示，而是以html的形式。
    #     return format_html('%s' % (color, obj.get_gender_display()))
    #
    # colored_gender.short_description = "性别"  # 此行使得自定义的field可以按照模型的gender排序。并使得后台显示的列名与原生的列有相同样式
    # colored_gender.admin_order_field = "gender"

    def get_id(self, obj):
        if obj.id is None:
            a = Prescription.objects.all().order_by('-id')[:1]
            if a:
                return a[0].id + 1
            else:
                return 0
        else:
            return obj.id

    get_id.short_description = '处方ID'

class ValidityListFilter(admin.SimpleListFilter):
    title = ugettext_lazy('有效期')
    parameter_name = 'validity_date'

    def lookups(self, request, model_admin):
        return (
            ('0', ugettext_lazy('一周内')),
            ('1', ugettext_lazy('一个月内')),
            ('2', ugettext_lazy('半年内')),
            ('3', ugettext_lazy('一年内')),
            ('4', ugettext_lazy('一年以上')),
            ('5', ugettext_lazy('已过期')),

        )
        pass

    def queryset(self, request, queryset):
        today = datetime.date.today()
        if self.value() == '0':
            return queryset.filter(validity_date__gte= today, validity_date__lte=today+datetime.timedelta(7))
        if self.value() == '1':
            return queryset.filter(validity_date__gte=today, validity_date__lte=today + datetime.timedelta(30))
        if self.value() == '2':
            return queryset.filter(validity_date__gte=today, validity_date__lte=today + datetime.timedelta(182))
        if self.value() == '3':
            return queryset.filter(validity_date__gte=today, validity_date__lte=today + datetime.timedelta(365))
        if self.value() == '4':
            return queryset.filter(validity_date__gt=today + datetime.timedelta(365))
        if self.value() == '5':
            return queryset.filter(validity_date__lt=today)

        pass


class DrugAdmin(admin.ModelAdmin):

    # 每页显示15条数据
    list_per_page = 15

    # 在底部显示控制选项
    actions_on_bottom = False
    # 在顶部显示控制选项
    actions_on_top = True

    # 侧边栏过滤框
    # list_filter = ['user_name']

    # 搜索框
    search_fields = ['id','drug_name','mnemonic_code','manufacturer','specification','unit','serial_number','validity_period','property_classification','function_classification']


    fieldsets = [
        # ('库存', {'fields': ['stock_num']}),
        ('药品基本信息',{'fields':['get_id','drug_name','mnemonic_code','manufacturer','stock_num','specification','unit']}),
        ('价格信息', {'fields': ['purchase_price', 'retail_price', 'wholesale_price']}),
        ('进货信息', {'fields': ['serial_number','validity_period','validity_date','purchase_quantity','purchase_date']}),
        ('分类', {'fields': ['property_classification', 'function_classification']}),

    ]

    list_display = ['id','drug_name','mnemonic_code','retail_price_with_color','wholesale_price',
                    'manufacturer','validity_date','property_classification','function_classification','stock_num','unit','purchase_date']
    # list_display_links = ['id','drug_name']
    readonly_fields = ['get_id']

    # 侧边栏过滤框
    list_filter = ['property_classification', 'function_classification',ValidityListFilter,'purchase_date', ]

    actions = ['update_drug_price','calculate_drug_price','calculate_drug_purchase_price']


    def get_id(self, obj):
        if obj.id is None:
            a = Drug.objects.all().order_by('-id')[:1]
            if a:
                return a[0].id + 1
            else:
                return 0
        else:
            return obj.id
    get_id.short_description = '药品ID'

    def update_drug_price(self,request,queryset):
        if len(queryset)>0:
            for obj in queryset:
                # obj = Drug.objects.filter(id=item.id)[0]
                obj.purchase_price = tools.round_up(obj.purchase_price)
                obj.retail_price = tools.round_up(obj.retail_price)
                obj.wholesale_price = tools.round_up(obj.wholesale_price)
                obj.save()
                pass
            self.message_user(request,'选中的'+str(len(queryset))+'个药品的价格已经更新')
        else:
            for obj in Drug.objects.all():
                obj.purchase_price = tools.round_up(obj.purchase_price)
                obj.retail_price = tools.round_up(obj.retail_price)
                obj.wholesale_price = tools.round_up(obj.wholesale_price)
                obj.save()
            self.message_user(request,'所有药品的价格已经更新')

    update_drug_price.short_description = '【刷新】所选药品的【价格位数】'

    def calculate_drug_price(self, request, queryset):
        total_retail = 0
        total_wholesale = 0
        total_purchase = 0
        for obj in queryset:
            total_purchase+=obj.purchase_price
            total_retail+=obj.retail_price
            total_wholesale+=obj.wholesale_price
        total_retail = tools.round_up(total_retail)
        total_wholesale = tools.round_up(total_wholesale)
        total_purchase = tools.round_up(total_purchase)

        self.message_user(request, '选中的' + str(len(queryset)) + '个药品的 总进货价为：'+str(total_purchase)+
                          '元；总零售价为：'+str(total_retail)+'元；总批发价为：'+str(total_wholesale)+'元。')
    calculate_drug_price.short_description = '【统计】所选药品的【总价格】'

    def calculate_drug_purchase_price(self , request, queryset):
        total_purchase = 0
        for obj in queryset:
            total_purchase +=(obj.purchase_price*obj.purchase_quantity)
        total_purchase = tools.round_up(total_purchase)
        self.message_user(request, '选中的' + str(len(queryset)) + '个药品的 总进货开销为：' + str(total_purchase) +'元。')
    calculate_drug_purchase_price.short_description = '【统计】所选药品的【进货开支】'


class MedicationAdmin(admin.ModelAdmin):

    def save_model(self, request, obj, form, change):
        if not obj.medicine_drug:
            messages.add_message(request, messages.INFO, '请选择一个药品！')
        if obj.sale_amount > obj.medicine_drug.stock_num:
            messages.add_message(request, messages.INFO, '库存不足！请查看该药品的库存。')
        else:
            super(MedicationAdmin, self).save_model(request, obj, form, change)


admin.site.register(Drug,DrugAdmin)
admin.site.register(Prescription,PrescriptionAdmin)
# admin.site.register(Medication,MedicationAdmin)

admin.site.site_header = '鲁明卫生室管理后台'
admin.site.site_title = '鲁明卫生室门诊管理后台'

# admin.site.empty_value_display = '暂未指定'
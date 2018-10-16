from django.contrib import admin
from django.contrib import messages
# Register your models here.
# from django.utils.html import format_html

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
        ('进货信息', {'fields': ['serial_number','validity_period','purchase_quantity','purchase_date']}),
        ('分类', {'fields': ['property_classification', 'function_classification']}),

    ]

    list_display = ['id','drug_name','mnemonic_code','retail_price','wholesale_price',
                    'manufacturer','purchase_date','property_classification','function_classification','stock_num','unit']

    readonly_fields = ['get_id']

    # 侧边栏过滤框
    list_filter = ['purchase_date', 'property_classification', 'function_classification','manufacturer']

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
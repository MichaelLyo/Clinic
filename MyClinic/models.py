from django.core.exceptions import ValidationError
from django.db import models
import datetime
from django.utils import timezone
import json
from django.utils.html import format_html
from . import tools
from django.core.validators import MaxValueValidator, MinValueValidator
# Create your models here.

default_value = ' '

# 盒、瓶、支、袋、包、箱
DRUG_UNIT_CHOICE=(
    ('盒','盒'),
    ('瓶','瓶'),
    ('支','支'),
    ('袋','袋'),
    ('包','包'),
    ('箱','箱'),
)

def isValidValue(value):
    if type(value) == int:
        return True
    if value and type(value) == str:
        return len(value)>1
    return False

class Drug(models.Model):
    id = models.AutoField(primary_key=True,verbose_name='登记药品编号')

    drug_name = models.CharField(max_length=40, verbose_name='药品名称', default=default_value, blank=True, null=True)
    mnemonic_code =  models.CharField(max_length=40, verbose_name='助记码', default=default_value, blank=True, null=True)

    manufacturer = models.CharField(max_length=40, verbose_name='生产厂家', default=default_value, blank=True, null=True)
    specification = models.CharField(max_length=20, default=default_value, blank=True, null=True, verbose_name='规格')
    unit = models.CharField(max_length=40, verbose_name='单位', default='盒', blank=True, null=True,choices=DRUG_UNIT_CHOICE)

    purchase_quantity =models.FloatField(default=0,verbose_name='进货数量')
    purchase_date = models.DateTimeField(default=timezone.now, verbose_name='进货日期')
    serial_number = models.CharField(max_length=40, verbose_name='产品批号', default=default_value, blank=True, null=True)
    validity_period = models.CharField(max_length=40, verbose_name='有效期', default=default_value, blank=True, null=True)

    purchase_price = models.FloatField(default=0, verbose_name='进货价',validators=[MinValueValidator(0)])
    retail_price = models.FloatField(default=0, verbose_name='零售价',validators=[MinValueValidator(0)])
    wholesale_price = models.FloatField(default=0, verbose_name='批发价',validators=[MinValueValidator(0)])

    stock_num = models.FloatField(default=0, verbose_name='库存',validators=[MinValueValidator(0)])

    property_classification =  models.CharField(max_length=100, verbose_name='药品性质分类', default=default_value, blank=True, null=True)
    function_classification = models.CharField(max_length=100, verbose_name='药品功能分类', default=default_value, blank=True,
                                               null=True)
    class Meta:
        verbose_name = "药品"
        verbose_name_plural = "所有药品信息"

    def save(self, *args, **kwargs):
        if self.retail_price <=0:
            self.set_default_retail_price()
        if self.wholesale_price <=0:
            self.set_default_wholesale_price()

        if (self.mnemonic_code == ' ' or not isValidValue(self.mnemonic_code)) and self.drug_name and isValidValue(self.drug_name):
            self.mnemonic_code = tools.get_str_first_letters(self.drug_name)

        # if self.stock_num<0:
        #     raise ValidationError('库存不够！')
        super(Drug, self).save(*args, **kwargs)

    def __str__(self):
        if self:
            return self.drug_name+'('+str(self.id)+')'
        else:
            return 'null'

    def set_default_retail_price(self):
        self.retail_price = tools.round_up(1.2*self.purchase_price)
        # return 1.2*self.purchase_price

    def set_default_wholesale_price(self):
        self.wholesale_price = tools.round_up(1.1*self.purchase_price)
        # return 1.1*self.purchase_price

    def get_model_dict(self):
        result = dict([(attr, getattr(self, attr) if isValidValue(getattr(self, attr)) else None)  for attr in [f.name for f in self._meta.fields]])
        # pop_list = ['borrower','referrer']
        # for p_item in pop_list:
        #     result.pop(p_item)
            # result[p_item+'_id'] = getattr(self,p_item).id if getattr(self,p_item) else None
        return result


    def update_info_from_json(self,json_data):
        except_attr = []
        for attr in json_data:
            if attr not in except_attr and hasattr(self, attr):
                if type(getattr(self,attr)) == int:
                    setattr(self, attr, tools.parse_to_int(json_data[attr]))
                else:
                    setattr(self, attr, json_data[attr] if json_data[attr] else default_value)

        pass


def get_pic_html(img_url):
    # img_url = 'http://image.huawei.com/tiny-lts/v1/images/390f4257fd206aea9577_2767x417.jpg'
    additional_info = ''
    if img_url and len(img_url) > 2:
        try:
            from urllib.parse import urlparse
            import http.client
            redirect_url = img_url
            is_pic_url = False
            while redirect_url != False:
                parse_object = urlparse(redirect_url)
                conn = http.client.HTTPConnection(parse_object.netloc)
                conn.request("HEAD",  parse_object.path)
                resp_header = conn.getresponse().getheaders()
                new_redirect = ''
                for item in resp_header:
                    if item[0] == 'location':
                        new_redirect = item[1]
                    if item[0] == 'Content-Type':
                        is_pic_url = 'image' in item[1] or 'jpeg' in item[1]
                redirect_url = new_redirect if new_redirect and len(new_redirect)>1 else False
                print(resp_header)

            if not is_pic_url:
                additional_info = '<p>该URL不是一个指向图片的URL！</p>' \
                                  '<p>（出错的原因可能是：用户上传图片出错，数据库存储URL出错，存储图片空间不足）</p>' \
                                  '<p>若图片正常显示，请忽略此提醒</p>'

        except Exception as e:
            print("获取图片失败！Exception：")
            print(e)
            return "URL无效或不是一个URL"

        pic_html = '<a href="{}"> ' \
                   '<img border="0" src="{}" style= "width: auto;height: auto;max-width: 30%;max-height: 30%;"/>' \
                   '</a>'+additional_info
        return format_html(pic_html.format(img_url, img_url))

    else:
        return "该用户暂未上传"


SEX_CHOICE = (
    ('男', '男'),
    ('女', '女'),
    # ('未指定', '未指定'),
)

class Prescription(models.Model):

    id = models.AutoField(primary_key=True,verbose_name='处方编号')
    patient_name = models.CharField(max_length=40, verbose_name='患者姓名', default=default_value, blank=True, null=True)
    patient_gender = models.CharField(max_length=10, verbose_name='患者性别', default=default_value, blank=True, null=True,choices=SEX_CHOICE)
    patient_age = models.IntegerField(verbose_name='患者年龄', default=1,validators=[MinValueValidator(0)])
    illness_description = models.TextField(max_length=300, verbose_name='病症描述', default=default_value, blank=True, null=True)

    treatment_cost = models.FloatField(default=0,verbose_name='治疗费',validators=[MinValueValidator(0)])

    create_date = models.DateTimeField(default=timezone.now,verbose_name='创建日期')

    doctor_name = models.CharField(max_length=40, verbose_name='主治医生姓名', default='刘佃津', blank=True, null=True)

    class Meta:
        verbose_name = "门诊处方"
        verbose_name_plural = "所有处方单"

    def __str__(self):
        if self:
            if isValidValue(self.patient_name):
                return self.patient_name
            else:
                return '未指定患者姓名'

        return 'null'

    def get_total_retail_cost(self):
        result = 0
        all_medication = Medication.objects.filter(medicine_prescription=self)
        for medication in all_medication:
            result += (medication.medicine_drug.retail_price*medication.sale_amount)
        result+=self.treatment_cost
        return tools.round_up(result)
    get_total_retail_cost.short_description = '药方总零售价'

    def get_total_wholesale_cost(self):
        result = 0
        all_medication = Medication.objects.filter(medicine_prescription=self)
        for medication in all_medication:
            result += (medication.medicine_drug.wholesale_price*medication.sale_amount)
        result += self.treatment_cost
        return tools.round_up(result)
    get_total_wholesale_cost.short_description = '药方总批发价'

    def get_model_dict(self):
        result = dict([(attr, str(getattr(self, attr)) if isValidValue(getattr(self, attr)) else None) for attr in [f.name for f in self._meta.fields]])
        pop_list = []
        for p_item in pop_list:
            result.pop(p_item)
            result[p_item+'_id'] = getattr(self,p_item).id if getattr(self,p_item) else None
        return result

    def update_info_from_json(self,json_data):
        except_attr = []
        for attr in json_data:
            if  attr not in except_attr and hasattr(self,attr):
                if type(getattr(self,attr)) == int:
                    setattr(self, attr, tools.parse_to_int(json_data[attr]))
                else:
                    setattr(self, attr, json_data[attr] if json_data[attr] else default_value)
        pass


class Medication(models.Model):

    # ID
    id = models.AutoField(primary_key=True,verbose_name='药方编号')

    # 药品
    # 售货数量

    medicine_drug = models.ForeignKey(Drug,on_delete=models.CASCADE,related_name='medication_drug',verbose_name='药品')
    medicine_prescription = models.ForeignKey(Prescription,on_delete=models.CASCADE,related_name='medication_prescription',verbose_name='处方')

    sale_amount = models.FloatField(default=0,verbose_name='售货数量',validators=[MinValueValidator(0)])

    # create_date = models.DateTimeField(default=timezone.now,verbose_name='创建日期')

    class Meta:
        verbose_name = "处方开药"
        verbose_name_plural = "所有处方开药记录"

    def __str__(self):
        if self:
            if self.medicine_drug and self.medicine_prescription:
                return '处方'+str(self.medicine_prescription.id)+':' + self.medicine_drug.drug_name

        return 'null'

    def save(self, *args, **kwargs):
        if (self.id is None) and self.medicine_drug and self.medicine_prescription:
            self.medicine_drug.stock_num -= self.sale_amount
            # if self.medicine_drug.stock_num<0:
            #
            self.medicine_drug.save()
        super(Medication, self).save(*args, **kwargs)

    def update_info_from_json(self,json_data):
        except_attr = []
        for attr in json_data:
            if  attr not in except_attr and hasattr(self,attr):
                if type(getattr(self,attr)) == int:
                    setattr(self, attr, tools.parse_to_int(json_data[attr]))
                else:
                    setattr(self, attr, json_data[attr] if json_data[attr] else default_value)
        pass



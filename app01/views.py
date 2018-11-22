from django.shortcuts import render,HttpResponse,redirect
from utils.pay import AliPay
import time
# Create your views here.
def alipay():
    obj = AliPay(
        appid="",######添写自己的appid
        app_notify_url="http://127.0.0.1:8000/update_order/",  #这是一个公网地址，这里省略暂不实现。 如果支付成功，支付宝会向这个地址发送POST请求（校验是否支付已经完成）
        return_url="http://127.0.0.1:8000/payresult/",  # 如果支付成功，重定向回到你的网站的地址。
        alipay_public_key_path="keys/alipay_public.txt",  # 支付宝公钥 使用自己的支付宝公钥，这里的公钥现在为空
        app_private_key_path="keys/app_private.txt",  # 应用私钥 使用自己的支付宝公钥，这里的公钥现在为空
        debug=True,  # 默认False,
    )
    return obj

def index(request):
    obj = alipay()
    if request.method == 'GET':
        return render(request,'index.html')
    out_trade_no = "x2" + str(time.time())#######动态的
    # 1. 在数据库创建一条数据：状态（待支付）
    money = float(request.POST.get('price'))
    query_params = obj.direct_pay(
        subject="苹果笔记本电脑",  # 商品简单描述
        out_trade_no=out_trade_no,  # 商户订单号
        total_amount=money,  # 交易金额(单位: 元 保留俩位小数)
    )
    pay_url = "https://openapi.alipaydev.com/gateway.do?{}".format(query_params)
    return redirect(pay_url)


def payresult(request):
    '''
    支付完成后，跳转回的地址
    :param request:
    :return:
    '''
    params = request.GET.dict()
    sign = params.pop('sign', None)
    obj = alipay()
    status = obj.verify(params, sign)
    if status:
        return HttpResponse('支付成功')
    return HttpResponse('支付失败')



# def update_order(request):
#     """
#     支付成功后，支付宝向该地址发送的POST请求（用于修改订单状态）
#     :param request:
#     :return:
#     """
#     if request.method == 'POST':
#         from urllib.parse import parse_qs
#
#         body_str = request.body.decode('utf-8')
#         post_data = parse_qs(body_str)
#
#         post_dict = {}
#         for k, v in post_data.items():
#             post_dict[k] = v[0]
#
#         obj = alipay()
#
#         sign = post_dict.pop('sign', None)
#         status = obj.verify(post_dict, sign)
#         if status:
#             # 修改订单状态
#             out_trade_no = post_dict.get('out_trade_no')
#             print(out_trade_no)
#             # 2. 根据订单号将数据库中的数据进行更新
#             return HttpResponse('支付成功')
#         else:
#             return HttpResponse('支付失败')
#     return HttpResponse('')
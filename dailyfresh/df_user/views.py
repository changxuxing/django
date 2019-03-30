# coding:utf-8
from django.http import JsonResponse, HttpResponseRedirect
from django.shortcuts import render, redirect
from models import *
from hashlib import sha1
from . import user_decorator
from df_goods.models import GoodsInfo


def register(request):
    context = {'title': '注册'}
    return render(request, 'df_user/register.html', context)


def register_handle(request):

    # 接收用户输入
    post = request.POST
    uname = post.get('user_name')
    upwd = post.get('pwd')
    upwd2 = post.get('cpwd')
    uemail = post.get('email')

    # 判断两次密码
    if upwd != upwd2:
        return redirect('/user/register/')

    # 密码加密
    s1 = sha1()
    s1.update(upwd)
    upwd3 = s1.hexdigest()

    # 创建对象
    user = UserInfo()
    user.uname = uname
    user.upwd = upwd3
    user.uemail = uemail
    user.save()

    # 注册成功，转到登陆页面
    return redirect('/user/login/')


def register_exist(request):
    uname = request.GET.get('uname')
    count = UserInfo.objects.filter(uname=uname).count()
    return JsonResponse({'count': count})


def login(request):
    uname = request.COOKIES.get('uname', '')
    context = {'title': '用户登录', 'error_name': 0, 'error_pwd': 0, 'uname': uname}
    return render(request, 'df_user/login.html', context)


def login_handle(request):
    # 接收数据请求
    post = request.POST
    uname = post.get('username')
    upwd = post.get('pwd')
    jizhu = post.get('jizhu', 0)
    # 根据用户名查询对象
    users = UserInfo.objects.filter(uname=uname)
    # print uname
    # 判断：如果没查到则用户名错误，如果查到判断密码是否正确，正确则转到用户中心
    if len(users) == 1:
        s1 = sha1()
        s1.update(upwd)
        # print (users[0].uname)
        if s1.hexdigest() == users[0].upwd:
            url = request.COOKIES.get('url', '/')
            red = HttpResponseRedirect(url)
            # print (red)
            # 记住用户名
            if jizhu != 0:
                # print 'jj'
                red.set_cookie('uname', uname)
            else:
                # print 'yy'
                red.set_cookie('uname', '', max_age=-1)
            request.session['user_id'] = users[0].id
            request.session['user_name'] = uname
            return red
        else:
            context = {'title': '用户登陆', 'error_name': 0, 'error_pwd': 1, 'uname': uname, 'upwd': upwd}
            return render(request, 'df_user/login.html', context)
    else:
        context = {'title': '用户登陆', 'error_name': 1, 'error_pwd': 0, 'uname': uname, 'upwd': upwd}
        return render(request, 'df_user/login.html', context)


def logout(request):
    request.session.flush()
    return redirect('/')


@user_decorator.login
def info(request):
    user_email = UserInfo.objects.get(id=request.session['user_id']).uemail
    # 最近浏览
    goods_ids = request.COOKIES.get('goods_ids', '')
    goods_id1 = goods_ids.split(',')
    goods_list = []
    for goods_id in goods_id1:
        goods_list.append(GoodsInfo.objects.get(id=int(goods_id)))
        # print goods_list
    # print goods_list[0].gpic
    context = {
        'title': '个人信息',
        'user_email': user_email,
        'user_name': request.session['user_name'],
        'goods_list': goods_list,
               }
    return render(request, 'df_user/user_center_info.html', context)


@user_decorator.login
def order(request):
    context = {'title': '全部订单'}
    return render(request, 'df_user/user_center_order.html', context)


@user_decorator.login
def site(request):
    user = UserInfo.objects.get(id=request.session['user_id'])
    # print (request.method)
    if request.method == 'POST':

        post = request.POST
        print ('11')
        user.ushou = post.get('ushow')
        user.uaddress = post.get('uaddress')
        user.uyoubian = post.get('uyoubian')
        user.uphone = post.get('uphone')
        user.save()

    context = {'title': '收货地址', 'user': user}
    return render(request, 'df_user/user_center_site.html', context)

import hashlib

from django.views.generic import View
from django_redis import get_redis_connection
from django.http import JsonResponse
import jwt
import json

from ranking.user.models import UserProfile


def login_check(func):
    '''
     装饰器  做登录状态的校验,在request中添加一个user
    '''
    def wrapper(self,request,*args,**kwargs):
        # 从request里取token,假设username从token中拿,token_key是123456
        token = request.META.get('HTTP_AUTHORIZATION')
        if not token:
            return None
        try:
            res = jwt.decode(token,123456)
        except Exception as e :
            result = {'code':10086,'error':'Please login'}
            return JsonResponse(result)
        username = res['user']
        try:
            # 校验用户名是否存在,UserProfile是用户表
            old_user = UserProfile.object.get(username=username)
        except Exception as e:
            result = {'code':10010,'error':'User is wrong'}
            return JsonResponse(result)
        request.user = username

        return func(self,request,*args,**kwargs)
    return wrapper


class Ranking_list(View):
    
    @login_check
    def post(self,request):
        '''
        提交自己的rank分数，存入redis中
        成功返回200,
        不成功随机5位数
        '''
        user = request.user
        json_obj = json.loads(request.body)
        password = json_obj['password']
        m = hashlib.md5()
        m.update(password.encode())
        try:
            UserProfile.objects.get(username=user, password=m.hexdigest())
        except Exception as e:
            result = {'code': 10111, 'error': 'User or password is wrong'}
            return JsonResponse(result)
        try:
            rank = int(json_obj['rank'])
        except Exception as e :
            result = {'code':10098,'error':'Please give me rank'}
            return JsonResponse(result)
        redis_conn = get_redis_connection('Ranking_list')
        redis_conn.zadd(rank,user)
        result = {'code':200,'data':'ok'}
        return JsonResponse(result)

    @login_check
    def put(self, request):
        '''
        前端返回数据，更新自己分数，并获取想要的rank区段的信息
        返回200,和查询出来的rank区段，以及自己的排名
        '''
        user = request.user
        json_obj = json.loads(request.body)
        try:
            scope = json_obj['arange']
            if len(scope) == 2:
                start = int(scope[0])-1
                stop = int(scope[1])-1
        except Exception as e:
            print('默认查询1至10名')
        try:
            rank = int(json_obj['rank'])
        except Exception as e :
            result = {'code':10098,'error':'Please give me rank'}
            return JsonResponse(result)
        redis_conn = get_redis_connection('Ranking_list')
        redis_conn.zadd(rank,user)
        user_rank = int(redis_conn.zrank(user))+1
        me = {}
        me['ranking'] = user_rank
        me['user'] = user
        me['rank_score'] = rank
        rank_list = ranking_list(start,stop)
        rank_list.append(me)
        result = {'code':200,'data':rank_list}
        return JsonResponse(result)





def ranking_list(start=0,stop=9):
    '''
    从redis中拿想要的区段，默认第1至10名
    '''
    redis_conn = get_redis_connection('Ranking_list')
    rank_ = redis_conn.zrevarange(start,stop)
    if not rank_:
        return
    rank_list = []
    i = 1
    for k in range(0,len(rank_),2):
        user = {}
        user['ranking'] = i
        user['user'] = rank_[k]
        user['rank_score'] = rank_[k+1]
    return rank_list
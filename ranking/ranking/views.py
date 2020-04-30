from django.views.generic import View
from django_redis import get_redis_connection
from django.http import JsonResponse
import jwt
import json


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
        passwrd = json_obj['password']
        m = hashlib.md5()
        m.update(password.encode())
        try:
            UserProfile.objects.create(username=user, password=m.hexdigest())
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
            scope = json_obj['scope']
            if len(scope) == 2:
            start = int(scope[0])
            end = int(scope[1])
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
        user_list = [user_rank,user,rank]
        rank_list = ranking_list(start,stop)
        rank_list.append(user_list)
        result = {'code':200,'data':rank_list}
        return JsonResponse(result)



def login_check(func):
    '''
     装饰器  做登录状态的校验,在request中添加一个user
    '''
    def wrapper(self,request,*args,**kwargs):
        # 从request里取username,假设从token中拿，token存在redis中,token_key是123456
        token = request.META.get('HTTP_AUTHORIZATION')
        if not data:
            return None
        try:
            res = jwt.decode(token,123456)
        except Exception as e :
            result = {'code':10086,'error':'Please login'}
            return JsonResponse(result)
        username = res['user']
        try:
            # 校验用户名是否存在Userfilter是用户表 
            old_user = Userfilter.object.get(username=username)
        except Exception as e:
            result = {'code':10010,'error':'User is wrong'}
            return JsonResponse(result)
        request.user = username

        return func(self,request,*args,**kwargs)
    return wrapper

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
        res = [i]
        res.append(rank_[k])
        res.append(rank_[k+1])
        i += 1
    return rank_list
    

import json

from django.conf import settings
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import ListView, CreateView

from users.models import User, Location


class UserListView(ListView):
    model = User
    queryset = User.objects.all()

    def get(self, request, *args, **kwargs):
        super().get(self, *args, **kwargs)
        self.object_list = self.object_list.order_by("username")
        paginator = Paginator(object_list=self.object_list, per_page=settings.TOTAL_ON_PAGE)
        page = request.GET.get('page')
        page_obj = paginator.get_page(page)

        result = []

        for user in page_obj:
            result.append(
                {"id": user.id,
                 "username": user.username,
                 "first_name": user.first_name,
                 "last_name": user.last_name,
                 "role": user.role,
                 "age": user.age,
                 "total_ads": user.ads.count()
                 })

        return JsonResponse({
            'ads': result,
            'pages': page_obj.number,
            'total': page_obj.paginator.count},
            safe=False, json_dumps_params={"ensure_ascii": False}
        )


@method_decorator(csrf_exempt, name='dispatch')
class UserCreateView(CreateView):
    model = User
    fields = ['username', 'password', 'first_name', 'last_name', 'role', 'locations', 'age']

    def post(self, request, *args, **kwargs):
        data = json.loads(request.body)

        user = User.objects.create(
            username=data['username'],
            first_name=data['first_name'],
            last_name=data['last_name'],
            age=data['age'],
            role=data['role'],
            password=data['password']
        )

        for loc in data['locations']:
            location, _ = Location.objects.get_or_create(name=loc)
            user.location.add(location)

        return JsonResponse(
            {'id': user.id,
             'username': user.username,
             'first_name': user.first_name,
             'last_name': user.last_name,
             'age': user.age,
             'role': user.role,
             'locations': [str(u) for u in user.location.all()]
             })


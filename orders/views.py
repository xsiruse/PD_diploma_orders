from distutils.util import strtobool

from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from django.core.validators import URLValidator
from django.db import IntegrityError
from django.db.models import Q, Sum, F
from django.http import JsonResponse
from requests import get
from rest_framework.authtoken.models import Token
from rest_framework.exceptions import ValidationError
from rest_framework.generics import ListAPIView
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet
from yaml import load as load_yaml, Loader
from orders.models import Product, Shop, ProductInfo, Parameter, ProductParameter, Category, Order, OrderItem, \
    ConfirmEmailToken, Contact, User
from orders.serializers import UserSerializer, ProductInfoSerializer, CategorySerializer, ShopSerializer, \
    ProductSerializer, OrderSerializer, OrderItemSerializer, ContactSerializer
from ujson import loads as load_json
from django.utils.translation import ugettext_lazy as _
from orders.signals import new_order, new_user_registered, logged_in


class PartnerUpdate(APIView):
    """
    Класс для обновления прайса от поставщика
    """

    def post(self, request, *args, **kwargs):
        if request.user.type != 'shop':
            return JsonResponse({'Status': 403, 'Error': 'Только для магазинов'})

        url = request.data.get('url')
        if url:
            validate_url = URLValidator()
            try:
                validate_url(url)
            except ValidationError as e:
                return JsonResponse({'Status': 404, 'Error': str(e)})
            else:
                stream = get(url).content

                data = load_yaml(stream, Loader=Loader)

                shop, _ = Shop.objects.get_or_create(name=data['shop'])
                for category in data['categories']:
                    category_object, _ = Category.objects.get_or_create(id=category['id'], name=category['name'])
                    category_object.shops.add(shop.id)
                    category_object.save()
                ProductInfo.objects.filter(shop_id=shop.id).delete()
                for item in data['goods']:
                    product, _ = Product.objects.get_or_create(name=item['name'], category_id=item['category'])

                    product_info = ProductInfo.objects.create(product_id=product.id,
                                                              name=item['model'],
                                                              price=item['price'],
                                                              price_rrc=item['price_rrc'],
                                                              quantity=item['quantity'],
                                                              shop_id=shop.id)
                    for name, value in item['parameters'].items():
                        parameter_object, _ = Parameter.objects.get_or_create(name=name)
                        ProductParameter.objects.create(product_info_id=product_info.id,
                                                        parameter_id=parameter_object.id,
                                                        value=value)

                return JsonResponse({'Status': 200, 'Message': 'Success'})

        return JsonResponse({'Status': 411, 'Errors': 'Не указаны все необходимые аргументы'})


class PartnerState(APIView):
    """
    сменить состояние доступности поставщика
    """

    # получить текущий статус
    def get(self, request, *args, **kwargs):

        if request.user.type != 'shop':
            return JsonResponse({'Status': False, 'Error': 'Только для магазинов'}, status=403)

        shop = request.user.shop
        serializer = ShopSerializer(shop)
        return Response(serializer.data)

    # изменить текущий статус
    def post(self, request, *args, **kwargs):

        if request.user.type != 'shop':
            return JsonResponse({'Status': 403, 'Error': 'Только для магазинов'}, status=403)
        state = request.data.get('state')
        if state:
            try:
                Shop.objects.filter(user_id=request.user.id).update(state=strtobool(state))
                return JsonResponse({'Status': 200, 'Message': 'State changed to '})
            except ValueError as error:
                return JsonResponse({'Status': 422, 'Errors': str(error)})

        return JsonResponse({'Status': 411, 'Errors': 'Не указаны все необходимые аргументы'})


class LoginAccount(APIView):
    """
    Вход
    """
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):

        if {'email', 'password'}.issubset(request.data):
            user = authenticate(request, username=request.data['email'], password=request.data['password'])

            if user is not None:
                if user.is_active:
                    token, _ = Token.objects.get_or_create(user=user)
                    logged_in.send(sender=self.__class__, user_id=user.id)

                    return JsonResponse({'Status': 200, 'Token': token.key})

            return JsonResponse({'Status': 404, 'Errors': 'Неверно указаны email|пароль либо пользователь еще не '
                                                          'зарегистрирован'})

        return JsonResponse({'Status': 411, 'Errors': 'Указаны не все необходимые поля'})


class RegisterAccount(APIView):
    """
    Регистрация
    """
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        # print(request.data)
        if {'first_name',
            'last_name',
            'email',
            'password',
            'company',
            'position',
            } \
                .issubset(request.data):
            errors = {}
            try:
                validate_password(request.data['password'])
            except Exception as password_error:
                error_array = []
                for item in password_error:
                    error_array.append(item)
                return JsonResponse({'Status': 403, 'Errors': {'password': error_array}})
            else:
                request.data._mutable = True
                request.data.update({})
                user_serializer = UserSerializer(data=request.data)
                if user_serializer.is_valid():
                    user = user_serializer.save()
                    user.set_password(request.data['password'])
                    user.save()
                    new_user_registered.send(sender=self.__class__, user_id=user.id, url=request.META['HTTP_HOST'])
                    return JsonResponse({'Status': 200, 'Message': 'User registered successfully. '
                                                                   'Check %s' % request.data['email']})
                else:
                    return JsonResponse({'Status': 404, 'Errors': user_serializer.errors})

        return JsonResponse({'Status': 411, 'Errors': 'Указаны не все необходимые поля'})


class ConfirmAccount(APIView):
    """
    Подтверждение регистрации
    """
    permission_classes = [AllowAny]

    # Регистрация методом POST
    def post(self, request, *args, **kwargs):
        # print(request.data)
        user = User.objects.filter(email=request.data['email'], is_active=True)
        if user:
            return JsonResponse({'Status': 200, 'Message': _('Confirmation has been done earlier')})

        # проверяем обязательные аргументы
        if {'email', 'token'}.issubset(request.data):

            token = ConfirmEmailToken.objects.filter(user__email=request.data['email'],
                                                     key=request.data['token']).first()
            if token:
                token.user.is_active = True
                token.user.save()
                # reset_password_token_created.send(sender=self.__class__, user_id=user.id)
                token.delete()
                return JsonResponse({'Status': 200, 'Message': _('Registration complete successfully')})
            else:
                return JsonResponse({'Status': 403, 'Errors': _('Неправильно указан токен или email')})

        return JsonResponse({'Status': 411, 'Errors': 'Не указаны все необходимые аргументы'})


# class ContactView(APIView):
#     """
#     Класс для работы с контактами покупателей
#     """
#
#     # получить мои контакты
#     def get(self, request, *args, **kwargs):
#
#         contact = Contact.objects.filter(
#             user_id=request.user.id)
#         serializer = ContactSerializer(contact, many=True)
#         return Response(serializer.data)
#
#     # добавить новый контакт
#     def post(self, request, *args, **kwargs):
#
#         if {'city', 'street', 'phone'}.issubset(request.data):
#             request.data._mutable = True
#             request.data.update({'user': request.user.id})
#             serializer = ContactSerializer(data=request.data)
#
#             if serializer.is_valid():
#                 serializer.save()
#                 return JsonResponse({'Status': 200, 'Message': 'Contact updated successfully'})
#             else:
#                 JsonResponse({'Status': 404, 'Errors': serializer.errors})
#
#         return JsonResponse({'Status': 411, 'Errors': 'Не указаны все необходимые аргументы'})
#
#     # удалить контакт
#     def delete(self, request, *args, **kwargs):
#
#         items_sting = request.data.get('items')
#         if items_sting:
#             items_list = items_sting.split(',')
#             query = Q()
#             objects_deleted = False
#             for contact_id in items_list:
#                 if contact_id.isdigit():
#                     query = query | Q(user_id=request.user.id, id=contact_id)
#                     objects_deleted = True
#
#             if objects_deleted:
#                 deleted_count = Contact.objects.filter(query).delete()[0]
#                 return JsonResponse({'Status': 200, 'Удалено объектов': deleted_count})
#         return JsonResponse({'Status': 411, 'Errors': 'Не указаны все необходимые аргументы'})
#
#     # редактировать контакт
#     def put(self, request, *args, **kwargs):
#
#         if 'id' in request.data:
#             if request.data['id'].isdigit():
#                 contact = Contact.objects.filter(id=request.data['id'], user_id=request.user.id).first()
#                 print(contact)
#                 if contact:
#                     serializer = ContactSerializer(contact, data=request.data, partial=True)
#                     if serializer.is_valid():
#                         serializer.save()
#                         return JsonResponse({'Status': 200})
#                     else:
#                         JsonResponse({'Status': 404, 'Errors': serializer.errors})
#
#         return JsonResponse({'Status': 411, 'Errors': 'Не указаны все необходимые аргументы'})

# Пример ViewSet
class ContactViewSet(ModelViewSet):
    # permission_classes = [AllowAny]
    serializer_class = ContactSerializer

    def get_queryset(self):
        """
        This view should return CRUD of all the contacts
        for the currently authenticated user.
        """
        user = self.request.user
        return Contact.objects.filter(user_id=user)


class CategoryView(ListAPIView):
    """
    список категорий
    """
    queryset = Category.objects.all()
    serializer_class = CategorySerializer


class ShopView(ListAPIView):
    """
    список магазинов
    """
    queryset = Shop.objects.filter(state=True)
    serializer_class = ShopSerializer


class ProductView(ListAPIView):
    """
    список товаров
    """
    queryset = Product.objects.filter(product_infos__shop__state=True)
    serializer_class = ProductSerializer


class ProductInfoView(APIView):
    """
    Поиск товаров
    фильтры по параметрам
        shop_id
        category_id
        product_id
    """

    # permission_classes = [IsAuthenticated]
    def get(self, request, *args, **kwargs):

        query = Q(shop__state=True)
        shop_id = request.query_params.get('shop_id')
        category_id = request.query_params.get('category_id')
        product_id = request.query_params.get('product_id')

        if shop_id:
            query = query & Q(shop_id=shop_id)

        if category_id:
            query = query & Q(product__category_id=category_id)

        if product_id:
            query = query & Q(product_id=product_id)

        queryset = ProductInfo.objects.filter(
            query).select_related(
            'shop', 'product__category').prefetch_related(
            'product_parameters__parameter').distinct()

        serializer = ProductInfoSerializer(queryset, many=True)

        return Response(serializer.data)


class BasketView(APIView):
    """
    корзина
    """

    # получить корзину
    def get(self, request, *args, **kwargs):
        basket = Order.objects.filter(
            user_id=request.user.id, state='basket').prefetch_related(
            'ordered_items__product_info__product__category',
            'ordered_items__product_info__product_parameters__parameter').annotate(
            total_sum=Sum(F('ordered_items__quantity') * F('ordered_items__product_info__price'))).distinct()

        serializer = OrderSerializer(basket, many=True)
        return Response(serializer.data)

        # редактировать корзину

    def post(self, request, *args, **kwargs):

        items_sting = request.data.get('items')
        if items_sting:
            try:
                items_dict = load_json(items_sting)
            except ValueError:
                JsonResponse({'Status': False, 'Errors': 'Неверный формат запроса'})
            else:
                basket, _ = Order.objects.get_or_create(user_id=request.user.id, status='basket')
                objects_created = 0
                for order_item in items_dict:
                    order_item.update({'order': basket.id})
                    serializer = OrderItemSerializer(data=order_item)
                    if serializer.is_valid():
                        try:
                            serializer.save()
                        except IntegrityError as error:
                            return JsonResponse({'Status': 404, 'Errors': str(error)})
                        else:
                            objects_created += 1

                    else:

                        JsonResponse({'Status': 422, 'Errors': serializer.errors})

                return JsonResponse({'Status': 200, 'Создано объектов': objects_created})
        return JsonResponse({'Status': 411, 'Errors': 'Не все необходимые аргументы указаны'})

    # удалить товары из корзины
    def delete(self, request, *args, **kwargs):

        items_string = request.data.get('items')
        if items_string:
            items_list = items_string.split(',')
            basket, _ = Order.objects.get_or_create(user_id=request.user.id, status='basket')
            query = Q()
            objects_deleted = False
            for order_item_id in items_list:
                if order_item_id.isdigit():
                    query = query | Q(order_id=basket.id, id=order_item_id)
                    objects_deleted = True

            if objects_deleted:
                deleted_count = OrderItem.objects.filter(query).delete()[0]
                return JsonResponse({'Status': 200, 'Удалено объектов': deleted_count})
        return JsonResponse({'Status': 411, 'Errors': 'Не все необходимые аргументы указаны'})

    # изменить кол-во позиции в корзину
    def patch(self, request, *args, **kwargs):

        items_string = request.data.get('items')
        if items_string:
            try:
                items_dict = load_json(items_string)
            except ValueError:
                return JsonResponse({'Status': 422, 'Errors': 'Неверный формат запроса'})
            else:
                basket, _ = Order.objects.get_or_create(user_id=request.user.id, status='basket')
                objects_updated = 0
                for order_item in items_dict:
                    if type(order_item['id']) == int and type(order_item['quantity']) == int:
                        objects_updated += OrderItem.objects.filter(order_id=basket.id, id=order_item['id']).update(
                            quantity=order_item['quantity'])

                return JsonResponse({'Status': 200, 'Обновлено объектов': objects_updated})
        return JsonResponse({'Status': 411, 'Errors': 'Не все необходимые аргументы указаны'})


class OrderView(APIView):
    """
    Класс для получения и размешения заказов пользователями
    """

    # получить заказы
    def get(self, request, *args, **kwargs):
        # для магазина
        if request.user.type == 'shop':
            order = Order.objects.filter(
                ordered_items__product_info__shop__user_id=request.user.id).exclude(state='basket').prefetch_related(
                'ordered_items__product_info__product__category',
                'ordered_items__product_info__product_parameters__parameter').select_related('contact').annotate(
                total_sum=Sum(F('ordered_items__quantity') * F('ordered_items__product_info__price'))).distinct()
        # для клиента
        else:
            order = Order.objects.filter(
                user_id=request.user.id).exclude(state='basket').prefetch_related(
                'ordered_items__product_info__product__category',
                'ordered_items__product_info__product_parameters__parameter').select_related('contact').annotate(
                total_sum=Sum(F('ordered_items__quantity') * F('ordered_items__product_info__price'))).distinct()

        serializer = OrderSerializer(order, many=True)
        return Response(serializer.data)

    # разместить заказ из корзины
    def post(self, request, *args, **kwargs):

        if {'id', 'contact'}.issubset(request.data):
            if request.data['id'].isdigit():
                try:
                    is_updated = Order.objects.filter(
                        user_id=request.user.id, id=request.data['id']).update(
                        contact_id=request.data['contact'],
                        state='new')
                except IntegrityError as error:
                    print(error)
                    return JsonResponse({'Status': 422, 'Errors': 'Неправильно указаны аргументы'})
                else:
                    if is_updated:
                        new_order.send(sender=self.__class__, user_id=request.user.id)
                        return JsonResponse({'Status': 200})

        return JsonResponse({'Status': 411, 'Errors': 'Не указаны все необходимые аргументы'})

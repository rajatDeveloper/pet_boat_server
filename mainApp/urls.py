from django.urls import path
from mainApp.views import (
    get_pet_list,
    get_services_by_pet,
    get_all_services,
    create_sitter_service,
    list_sitter_services_for_user,
    sitter_service_detail,
    get_all_ads,
    create_pet,
    list_pets_for_user,
    create_order,
    list_orders_for_user,
    approve_order,
    complete_order,
    send_message_to_petsitter,
    send_message_to_user,
    add_review,
)

urlpatterns = [
    path('services/', get_all_services, name='service-list'),
    path('pets/', get_pet_list, name='pet-list'),
    path('pets/<str:pet>/services/', get_services_by_pet, name='services-by-pet'),
    # Sitter services
    path('sitter-services/', create_sitter_service, name='sitter-service-create'),  # POST
    path('users/<int:user_id>/sitter-services/', list_sitter_services_for_user, name='sitter-service-list-by-user'),  # GET
    path('sitter-services/<int:sitter_service_id>/', sitter_service_detail, name='sitter-service-detail'),  # GET
    # Ads
    path('ads/', get_all_ads, name='ad-list'),  # GET
    # Pets
    path('pets/create/', create_pet, name='pet-create'),  # POST
    path('users/<int:user_id>/pets/', list_pets_for_user, name='pet-list-by-user'),  # GET
    # Orders
    path('orders/', create_order, name='order-create'),  # POST
    path('users/<int:user_id>/orders/', list_orders_for_user, name='order-list-by-user'),  # GET
    path('orders/<int:order_id>/approve/', approve_order, name='order-approve'),  # PATCH
    path('orders/<int:order_id>/complete/', complete_order, name='order-complete'),  # PATCH
    path('orders/<int:order_id>/message-to-petsitter/', send_message_to_petsitter, name='order-msg-to-petsitter'),  # PATCH
    path('orders/<int:order_id>/message-to-user/', send_message_to_user, name='order-msg-to-user'),  # PATCH
    path('orders/<int:order_id>/review/', add_review, name='order-add-review'),  # PATCH
]

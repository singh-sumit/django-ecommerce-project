from django.urls import path
from .views import (HomeView, AboutView, ContactView, AllProductsView,
                    list_product_by_category, ProductDetail, AddToCartView,
                    MyCartView, ManageCartView, EmptyCartView, CheckoutView,
                    CustomerRegistrationView,CustomerLogoutView,CustomerLoginView,
                    CustomerProfileView,CustomerOrderDetailView, AdminLoginView,
                    AdminHomeView, AdminOrderDetailView,AdminOrderListView,
                    AdminChangeOrderStatusView,SearchView, AdminCreateCategoryView,
                    AdminCreateProductView,AdminProfileView, AdminPendingOrderView,
                    AdminDeleteCategoryView,AdminListCategoryView,AdminManageCategoryView,AdminEditCategoryView,
                    )

app_name = "ecomapp"

urlpatterns = [
    path('', HomeView.as_view(), name="home"),
    path('about/', AboutView.as_view(), name="about"),
    path('contact-us/', ContactView.as_view(), name="contact-us"),
    path('all-products/', AllProductsView.as_view(), name="allproducts"),
    path('categorized-products/<int:cat_id>/', list_product_by_category, name="categorized-products"),
    path('product/<slug:slug>/', ProductDetail.as_view(), name="productdetail"),

    path('add-to-cart-<int:pro_id>', AddToCartView.as_view(), name="addtocart"),

    path('my-cart/', MyCartView.as_view(), name="mycart"),

    path('managecart/<int:cp_id>/', ManageCartView.as_view(), name="managecart"),
    path('empty-cart/', EmptyCartView.as_view(), name="emptycart"),
    path('checkout/', CheckoutView.as_view(), name="checkout"),

    path('register/', CustomerRegistrationView.as_view(), name="customer-register"),
    path('logout/', CustomerLogoutView.as_view(), name="customer-logout"),
    path('login/', CustomerLoginView.as_view(), name="customer-login"),

    path('profile/', CustomerProfileView.as_view(), name="customer-profile"),
    path('profile/order-<int:pk>/', CustomerOrderDetailView.as_view(), name="customer-order-detail"),

    path('search/', SearchView.as_view(), name="search"),

    # admin section
    path('admin-login/', AdminLoginView.as_view(), name="adminlogin"),
    path('admin-home/', AdminHomeView.as_view(), name="adminhome"),
    path('admin-pending-order/', AdminPendingOrderView.as_view(), name="adminpendingorder"),
    path('admin-order/<int:pk>/', AdminOrderDetailView.as_view(), name="admin-order-detail"),
    path('admin-all-orders/', AdminOrderListView.as_view(), name="admin-all-order"),
    path('admin-order-<int:pk>-change/', AdminChangeOrderStatusView.as_view(), name="admin-change-order-status"),

    path('admin-create/category/', AdminCreateCategoryView.as_view(), name="admin-create-category"),
    path('admin-create/products/', AdminCreateProductView.as_view(), name="admin-create-product"),
    path('admin-profile/<int:pk>/', AdminProfileView.as_view(), name="admin-profile"),

    path('admin-list-category/', AdminListCategoryView.as_view(), name="admin-list-category"),
    path('admin-edit-category/<slug:slug>/', AdminEditCategoryView.as_view(), name="admin-edit-category"),
    # path('admin-delete-category-<slug:slug>/', AdminDeleteCategoryView.as_view(), name="admin-delete-category"),
    path('admin-manage-category-<slug:slug>/', AdminManageCategoryView.as_view(), name="admin-manage-category"),




]

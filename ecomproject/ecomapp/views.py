from django.contrib.auth import login, logout, authenticate
from django.core.exceptions import ValidationError
from django.shortcuts import render, get_object_or_404, reverse, redirect
from django.urls import reverse_lazy
from django.views.generic import (TemplateView, View, CreateView, FormView, DetailView, ListView,
                                  UpdateView, DeleteView)
from .models import Product, Category, Cart, CartProduct, Order, Admin, Customer, ORDER_STATUS
from .forms import (CheckoutForm, CustomerRegistrationForm, CustomerLoginForm,
                    AdminProfileUpdateForm, AdminCreateCategoryForm, AdminCreateProductForm, AdminCategoryUpdateForm)
from django.http import HttpResponseRedirect
from django.contrib.auth.models import User
from django.db.models import Q


# mixin
class EcomMixin(object):
    def dispatch(self, request, *args, **kwargs):
        # check if cart exist then relate it with user object
        cart_id = request.session.get('cart_id')
        if cart_id:
            cart_obj = Cart.objects.get(id=cart_id)
            if request.user.is_authenticated and request.user.customer:
                cart_obj.customer = request.user.customer
                cart_obj.save()
        return super().dispatch(request, *args, **kwargs)


# Create your views here.

class HomeView(EcomMixin, TemplateView):
    template_name = "home.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['category_list'] = Category.objects.all()
        context['product_list'] = Product.objects.all().order_by("-id")
        return context


class AllProductsView(EcomMixin, TemplateView):
    template_name = "allproducts.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["allcategories"] = Category.objects.all().order_by("-id")
        return context


def list_product_by_category(request, cat_id):
    category = get_object_or_404(Category, pk=cat_id)
    specific_products = category.product_set.all().order_by("-id")
    context = {'product_list': specific_products,
               'category_list': Category.objects.all(),
               }
    return render(request, 'home.html', context)


class ProductDetail(EcomMixin, TemplateView):
    template_name = "productdetail.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        slug = self.kwargs['slug']
        product = get_object_or_404(Product, slug=slug)
        product.view_count += 1
        product.save()
        context['product'] = product
        return context


class AddToCartView(EcomMixin, TemplateView):
    template_name = "addtocart.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # get product from requested url using pro_id
        product_id = self.kwargs['pro_id']
        # get product
        product_obj = get_object_or_404(Product, pk=product_id)

        # check if cart exists
        cart_id = self.request.session.get("cart_id", None)
        if cart_id:
            cart_obj = Cart.objects.get(id=cart_id)

            # check if product is in cart
            this_product_in_cart = cart_obj.cartproduct_set.filter(product=product_obj)
            # if product exist already in cartproduct objects
            if this_product_in_cart.exists():
                cartproduct = this_product_in_cart.last()
                cartproduct.quantity += 1
                cartproduct.subtotal += product_obj.selling_price
                cartproduct.save()

                cart_obj.total += product_obj.selling_price
                cart_obj.save()
            else:
                # new product added to cartproduct
                cartproduct = CartProduct.objects.create(cart=cart_obj,
                                                         product=product_obj,
                                                         rate=product_obj.selling_price,
                                                         quantity=1,
                                                         subtotal=product_obj.selling_price)
                cartproduct.save()
                cart_obj.total += product_obj.selling_price
                cart_obj.save()
        # if cart doesnot exist
        else:
            cart_obj = Cart.objects.create(total=0)
            # store obje in session
            self.request.session['cart_id'] = cart_obj.id

            # create a new product to add cartproduct
            cartproduct = CartProduct.objects.create(cart=cart_obj,
                                                     product=product_obj,
                                                     rate=product_obj.selling_price,
                                                     quantity=1,
                                                     subtotal=product_obj.selling_price)
            cartproduct.save()
            cart_obj.total += product_obj.selling_price
            cart_obj.save()
        # check if product already exists in cart
        return context


class MyCartView(EcomMixin, TemplateView):
    template_name = "mycart.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # check if cart exists
        cart_id = self.request.session.get('cart_id', None)
        if cart_id:
            cart = Cart.objects.get(id=cart_id)
            # print(cart,'-----------')
            # cartproducts = cart.cartproduct_set.all()
            # context['cartproducts']=cartproducts
        else:
            # cart does not exist yet
            # means no item added yet
            cart = None
        context['cart'] = cart
        return context


# class AddQuantityToCart(TemplateView):
#     template_name = "mycart.html"
#
#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         product_obj = self.kwargs['pid']
#         # get cart if exist
#         cart_id = self.request.session.get('cart_id', None)
#         if cart_id:
#             cart = Cart.objects.get(id=cart_id)
#             # get cartproduct for given cart_id
#             cartproduct_obj = cart.cartproduct_set.all()
#             specific_product_obj = cartproduct_obj.get(product=product_obj)
#             specific_product_obj.quantity += 1
#             specific_product_obj.subtotal += specific_product_obj.product.selling_price
#             specific_product_obj.save()
#             cart.total += specific_product_obj.product.selling_price
#             cart.save()
#         else:
#             # cart yet empty
#             cart = None
#         context['cart'] = cart
#         return context
#
#
# class RemoveQuantityFromCart(TemplateView):
#     template_name = "mycart.html"
#
#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         product_id = self.kwargs['pid']
#         # find cart if exists
#         cart_id = self.request.session.get('cart_id', None)
#         if cart_id:
#             # get cart object with cart_id
#             cart = Cart.objects.get(id=cart_id)
#             # find for cartproducts having id as pid
#             cartproducts_obj = cart.cartproduct_set.get(product_id=product_id)
#
#             # decrement quantity as well as subtotal, for cartproduct and total for cart
#             cartproducts_obj.quantity -= 1
#             cartproducts_obj.subtotal -= cartproducts_obj.product.selling_price
#
#             # on decrementing if quantity falls to 0 delete cartproducts itself from cart
#             if cartproducts_obj.quantity == 0:
#                 cartproducts_obj.delete()
#             else:
#                 cartproducts_obj.save()
#
#             cart.total -= cartproducts_obj.product.selling_price
#             cart.save()
#         else:
#             # cart_id not found in session means
#             # yet not added any items to cart
#             cart = None
#         context['cart'] = cart
#         return context
#
#
# class DeleteProductFromCart(TemplateView):
#     template_name = "mycart.html"
#
#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         product_id = self.kwargs['pid']
#         # find if cart with id=cart_id exist
#         cart_id = self.request.session.get('cart_id', None)
#         if cart_id:
#             cart = Cart.objects.get(id=cart_id)
#             # find cartproduct with pid
#             cartproduct_obj = cart.cartproduct_set.get(product_id=product_id)
#
#             # delete such cartproduct and save
#             cart.total -= cartproduct_obj.subtotal
#             cartproduct_obj.delete()
#             cart.save()
#         else:
#             # cart is yet not initialize so return empty cart
#             cart=None
#         context['cart']=cart
#         return context

class ManageCartView(EcomMixin, View):
    def get(self, request, *args, **kwargs):
        cart_id = self.request.session.get('cart_id')
        cp_id = self.kwargs["cp_id"]
        action = request.GET['action']
        # get cart with provied cart_id
        cart = Cart.objects.get(id=cart_id)
        # get cartproduct object from cp_id
        cp_obj = cart.cartproduct_set.get(product_id=cp_id)
        cart_obj = cp_obj.cart

        if action == "inc":
            cp_obj.quantity += 1
            cp_obj.subtotal += cp_obj.rate
            cp_obj.save()

            cart_obj.total += cp_obj.rate
            cart_obj.save()
        elif action == "dec":
            cp_obj.quantity -= 1
            cp_obj.subtotal -= cp_obj.rate
            cp_obj.save()

            cart_obj.total -= cp_obj.rate
            cart_obj.save()

            if cp_obj.quantity == 0:
                cp_obj.delete()
        elif action == "rmv":
            cart_obj.total -= cp_obj.subtotal
            cart_obj.save()
            cp_obj.delete()
        else:
            pass
        return redirect("ecomapp:mycart")


class EmptyCartView(View):
    def get(self, request, *args, **kwargs):
        cart_id = request.session.get("cart_id", None)
        if cart_id:
            cart = Cart.objects.get(id=cart_id)
            cart.cartproduct_set.all().delete()
            cart.total = 0
            cart.save()

        else:
            pass
        return redirect("ecomapp:mycart")


class CheckoutView(EcomMixin, CreateView):
    template_name = "checkout.html"
    form_class = CheckoutForm
    success_url = reverse_lazy("ecomapp:home")

    def dispatch(self, request, *args, **kwargs):
        # check if user is logined
        if request.user.is_authenticated and request.user.customer:
            pass
        else:
            # not logined user
            return redirect("/login/?next=/checkout/")
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        cart_id = self.request.session.get('cart_id', None)
        if cart_id:
            cart_obj = Cart.objects.get(id=cart_id)
        else:
            # no cart is found yet return none
            cart_obj = None
        context['cart'] = cart_obj
        return context

    def form_valid(self, form):
        cart_id = self.request.session.get("cart_id", None)
        if cart_id:
            cart_obj = Cart.objects.get(id=cart_id)

            form.instance.cart = cart_obj
            form.instance.subtotal = cart_obj.total
            form.instance.discount = 0
            form.instance.total = cart_obj.total
            form.instance.order_status = "Order Recieved"

            del self.request.session['cart_id']
        else:
            # if cart_id is not present in session redirect to hom
            return redirect("ecomapp:home")
        return super().form_valid(form)


class CustomerRegistrationView(CreateView):
    template_name = "customer_register.html"
    form_class = CustomerRegistrationForm
    success_url = reverse_lazy("ecomapp:home")

    def form_valid(self, form):
        username = form.cleaned_data.get('username')
        password = form.cleaned_data.get('password')
        email = form.cleaned_data.get('email')
        user = User.objects.create_user(username, email, password)

        # save user to db
        form.instance.user = user

        # login the user
        login(self.request, user)
        return super().form_valid(form)

    def get_success_url(self):
        if "next" in self.request.GET:
            next_url = self.request.GET['next']
            return next_url
        else:
            return self.success_url


class CustomerLogoutView(View):
    def get(self, request, *args, **kwargs):
        logout(request)
        return redirect("ecomapp:home")


class CustomerLoginView(FormView):
    template_name = "customer_login.html"
    form_class = CustomerLoginForm
    success_url = reverse_lazy("ecomapp:home")

    # form_valid method is avaliable in only createview, formview, updateview
    def form_valid(self, form):
        uname = form.cleaned_data.get("username")
        upwd = form.cleaned_data.get("password")
        usr = authenticate(username=uname, password=upwd)
        if usr is not None and Customer.objects.filter(user=usr).exists():
            login(self.request, usr)
        else:
            return render(self.request, self.template_name,
                          {'form': self.form_class, "error": "Invalid Credentials"})
        return super().form_valid(form)

    def get_success_url(self):
        if "next" in self.request.GET:
            next_url = self.request.GET['next']
            return next_url
        else:
            return self.success_url


class CustomerProfileView(TemplateView):
    template_name = "customerprofile.html"

    # to view profile user must be logged in
    def dispatch(self, request, *args, **kwargs):
        # check if user is logined
        if request.user.is_authenticated and Customer.objects.filter(user=request.user).exists():
            pass
        else:
            # not logined user
            return redirect("/login/?next=/profile/")
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        customer = self.request.user.customer
        context['customer'] = customer

        orders = Order.objects.filter(cart__customer=customer).order_by("-id")
        context['orders'] = orders
        return context


class CustomerOrderDetailView(DetailView):
    template_name = "customerorderdetail.html"
    model = Order
    context_object_name = "ord_obj"

    # to view profile user must be logged in
    def dispatch(self, request, *args, **kwargs):
        # check if user is logined
        if request.user.is_authenticated and Customer.objects.filter(user=request.user).exists():
            order_id = self.kwargs['pk']
            order = Order.objects.filter(id=order_id).first()
            # check if this customer is owner of that order
            if order is None or request.user.customer != order.cart.customer:
                return redirect("ecomapp:customer-profile")
            else:
                pass
        else:
            # not logined user
            return redirect("/login/?next=/profile/")
        return super().dispatch(request, *args, **kwargs)


class SearchView(TemplateView):
    template_name = "search.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        kw = self.request.GET['keyword']
        results = Product.objects.filter(
            Q(title__icontains=kw) |
            Q(description__icontains=kw))
        context['results'] = results
        return context


class AboutView(EcomMixin, TemplateView):
    template_name = "about.html"


class ContactView(EcomMixin, TemplateView):
    template_name = "contactus.html"


# Admin Views

class AdminLoginView(FormView):
    template_name = "admin/adminlogin.html"
    form_class = CustomerLoginForm
    success_url = reverse_lazy("ecomapp:adminhome")

    def form_valid(self, form):
        uname = form.cleaned_data.get("username")
        upwd = form.cleaned_data.get("password")
        usr = authenticate(username=uname, password=upwd)
        if usr is not None and Admin.objects.filter(user=usr).exists():
            login(self.request, usr)
        else:
            return render(self.request, self.template_name,
                          {'form': self.form_class, "error": "Invalid Credentials"})
        return super().form_valid(form)


class AdminRequiredMixin(object):
    def dispatch(self, request, *args, **kwargs):
        # check if user is logined and is admin
        if request.user.is_authenticated and Admin.objects.filter(user=request.user).exists:
            pass
        else:
            # not logined user
            return redirect("/admin-login/")
        return super().dispatch(request, *args, **kwargs)


class AdminHomeView(AdminRequiredMixin, TemplateView):
    template_name = "admin/adminhome.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        users = User.objects.all()
        context['user_count'] = len(users)
        context['total_products'] = len(Product.objects.all())
        context['total_categories'] = len(Category.objects.all())
        context['total_orders'] = len(Order.objects.all())
        context["total_pending"] = len(Order.objects.filter(order_status="Order Recieved"))
        context["pendingorders"] = Order.objects.filter(order_status="Order Recieved").order_by("-id")

        return context


class AdminPendingOrderView(AdminRequiredMixin, TemplateView):
    template_name = "admin/pendingorder.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["pendingorders"] = Order.objects.filter(order_status="Order Recieved").order_by("-id")

        return context


class AdminOrderDetailView(AdminRequiredMixin, DetailView):
    template_name = "admin/orderdetail.html"
    model = Order
    context_object_name = "ord_obj"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['all_status'] = ORDER_STATUS
        return context


class AdminOrderListView(AdminRequiredMixin, ListView):
    template_name = "admin/adminallorders.html"
    # model = Order
    queryset = Order.objects.all().order_by("-id")
    context_object_name = "allorders"


class AdminChangeOrderStatusView(AdminRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        order_id = self.kwargs['pk']
        order_obj = Order.objects.get(id=order_id)
        changed_status = self.request.POST['status']
        order_obj.order_status = changed_status
        order_obj.save()
        return redirect(reverse_lazy("ecomapp:admin-order-detail", kwargs={"pk": order_id}))


# self
class AdminCreateCategoryView(AdminRequiredMixin, CreateView):
    template_name = "admin/createcategory.html"
    form_class = AdminCreateCategoryForm
    success_url = reverse_lazy("ecomapp:adminhome")


class AdminCreateProductView(AdminRequiredMixin, CreateView):
    template_name = "admin/createproduct.html"
    form_class = AdminCreateProductForm
    success_url = reverse_lazy("ecomapp:adminhome")


class AdminProfileView(AdminRequiredMixin, UpdateView):
    template_name = "admin/updateprofile.html"
    model = Admin
    form_class = AdminProfileUpdateForm
    success_url = reverse_lazy("ecomapp:adminhome")


class AdminListCategoryView(AdminRequiredMixin, ListView):
    template_name = "admin/listallcategory.html"
    queryset = Category.objects.all()

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        cat_list = context['category_list']
        return context


class AdminManageCategoryView(AdminRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        url_slug = self.kwargs['slug']
        action = request.GET['action']
        # print(url_slug, action, "????????????????")
        # get cat with provided slug
        cat = get_object_or_404(Category, slug=url_slug)

        if action == "edit":
            return redirect("ecomapp:admin-edit-category", slug=url_slug)
        elif action == "rmv":
            cat.delete()
        else:
            pass
        return redirect("ecomapp:admin-list-category")


class AdminEditCategoryView(AdminRequiredMixin, UpdateView):
    template_name = "admin/updatecategory.html"
    model = Category
    form_class = AdminCategoryUpdateForm
    success_url = reverse_lazy("ecomapp:admin-list-category")

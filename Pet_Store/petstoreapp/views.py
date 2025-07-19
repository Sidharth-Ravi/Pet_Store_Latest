from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from .models import Product, Cart, Order
from django.db.models import Q
import random
import razorpay
from django.core.mail import send_mail


# Registration
def register(request):
    context = {}
    if request.method == "POST":
        uname = request.POST["uname"]
        upass = request.POST["upass"]
        ucpass = request.POST["ucpass"]
        if uname == "" or upass == "" or ucpass == "":
            context["errmsg"] = "Fields cannot be Empty"
        elif upass != ucpass:
            context["errmsg"] = "Password and Confirm Password didn't match"
        else:
            try:
                u = User.objects.create(username=uname, email=uname)
                u.set_password(upass)
                u.save()
                context["success"] = "User Created Successfully"
            except Exception:
                context["errmsg"] = "User with same username already exists"
    return render(request, "register.html", context)

# Login
def loginuser(request):
    context = {}
    if request.method == 'POST':
        uname = request.POST.get('uname')
        upass = request.POST.get('upass')
        if uname == "" or upass == "":
            context["errmsg"] = "Fields cannot be empty"
        else:
            user = authenticate(request, username=uname, password=upass)
            if user is not None:
                login(request, user)
                return redirect("/home")
            else:
                context["errmsg"] = "Credentials are incorrect"
    return render(request, "login.html", context)

# Logout
def logoutuser(request):
    logout(request)
    return redirect('/login')

# Home (Protected)
@login_required(login_url='/login')
def home(request):
    p = Product.objects.filter(is_active=True)
    return render(request, 'index.html', {'Products': p})

# Category filter
@login_required(login_url='/login')
def catfilter(request, cv):
    q1 = Q(is_active=True)
    q2 = Q(cat=cv)
    p = Product.objects.filter(q1 & q2)
    return render(request, 'index.html', {'Products': p})

# Sorting
@login_required(login_url='/login')
def sort(request, sv):
    col = "-pcost" if sv == "0" else "pcost"
    p = Product.objects.filter(is_active=True).order_by(col)
    return render(request, "index.html", {"Products": p})

# Price Range Filter
@login_required(login_url='/login')
def range(request):
    min = request.GET['min']
    max = request.GET['max']
    q1 = Q(pcost__gte=min)
    q2 = Q(pcost__lte=max)
    q3 = Q(is_active=True)
    p = Product.objects.filter(q1 & q2 & q3)
    return render(request, 'index.html', {"Products": p})

# Product Details
@login_required(login_url='/login')
def product_details(request, pid):
    p = Product.objects.filter(id=pid)
    return render(request, "pdetails.html", {"Products": p})

# Add to Cart
@login_required(login_url='/login')
def addtocart(request, pid):
    u = User.objects.get(id=request.user.id)
    p = Product.objects.get(id=pid)
    Cart.objects.create(uid=u, pid=p)
    return HttpResponse(
        "<p style='color: blue; font-weight: bold;'>Product added in the cart</p>"
        "<img src='/media/success.jpeg' alt='Success Image'><br><br>"
        "<a href='/home'><button>Back to Home</button></a>&nbsp;&nbsp;"
        "<a href='/placeorder'><button>Proceed to Pay</button></a>"
    )

# Remove from Cart
@login_required(login_url='/login')
def remove(request, cid):
    Cart.objects.filter(id=cid).delete()
    return redirect("/viewcart")

# View Cart
@login_required(login_url='/login')
def viewcart(request):
    c = Cart.objects.filter(uid=request.user.id)
    total = sum(x.pid.pcost * x.qty for x in c)
    return render(request, "viewcart.html", {
        'Products': c,
        'n': len(c),
        'total': total
    })

# Update Quantity
@login_required(login_url='/login')
def updateqty(request, qv, cid):
    c = Cart.objects.get(id=cid)
    if qv == "1":
        c.qty += 1
    elif c.qty > 1:
        c.qty -= 1
    c.save()
    return redirect("/viewcart")

# Place Order
@login_required(login_url='/login')
def placeorder(request):
    c = Cart.objects.filter(uid=request.user.id)
    if not c.exists():
        return HttpResponse("Cart is empty.")

    oid = random.randrange(1000, 9999)
    
    for x in c:
        Order.objects.create(order_id=oid, pid=x.pid, uid=x.uid, qty=x.qty)
        x.delete()

    request.session['last_oid'] = oid

    orders = Order.objects.filter(uid=request.user.id, order_id=oid)
    total = sum(x.pid.pcost * x.qty for x in orders)

    return render(request, 'place_order.html', {
        'Products': orders,
        'total': total,
        'n': len(orders)
    })


# Make Payment
@login_required(login_url='/login')
def makepayment(request):
    oid = request.session.get('last_oid')
    if not oid:
        return HttpResponse("No recent order found.")

    orders = Order.objects.filter(uid=request.user.id, order_id=oid)
    total = sum(x.pid.pcost * x.qty for x in orders)

    if total <= 0:
        return HttpResponse("Invalid total amount for payment.")

    # Razorpay integration
    client = razorpay.Client(auth=("rzp_test_zdLBYxuK3Df0nN", "EoumSuSCNCWACMksHl3pTzD1"))
    data = {
        "amount": int(total * 100),  
        "currency": "INR",
        "receipt": str(oid)
    }
    payment = client.order.create(data=data)

    return render(request, "pay.html", {
        'data': payment,
        'amt': int(total * 100)
    })

# Send Mail
@login_required(login_url='/login')
def sendusermail(request):
    uemail = request.user.email
    send_mail(
        "Ekart order placed successfully!",
        "Order details are:",
        "s4sidhartholiyatholiyath@gmail.com",
        [uemail],
        fail_silently=False,
    )
    return HttpResponse("Mail sent successfully")

# Static Pages
def about(request):
    return render(request, 'aboutus.html')

def contact(request):
    return render(request, 'contact.html')

def indexpage(request):
    return render(request, "index.html")

def navbar(request):
    return render(request, "navbar.html")

def footer(request):
    return render(request, 'footer.html')

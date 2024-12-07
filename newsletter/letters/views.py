from django.shortcuts import render
from django.http import HttpResponse
from letters.models import Customer, Mailing, Message
from letters.forms import MailingForm, MessageForm, CustomerForm
from django.views.generic import CreateView, DeleteView, UpdateView
from django.urls import reverse_lazy
from django.http import HttpResponseForbidden
from django.contrib.auth.models import Permission
from .tasks import send_email
from django.shortcuts import get_object_or_404, redirect


def health_check(request):
    return HttpResponse("service letters is alive")

# def index(request):
#     if request.method == 'POST':
#         name = request.POST.get('name')
#         email = request.POST.get('email')
#         print(f'{name} ({email})')
#     return render(request, 'letters/index.html')


def get_customer_list(request):
    customer_list = Customer.objects.all()
    context = {
        'object_list': customer_list,
        'name_list': Customer._meta.verbose_name_plural,
        'active_menu': 'clients',
    }
    return render(request, 'letters/customer_list.html', context)


def get_mailing_list(request):
    
    # Проверяем, есть ли у пользователя право на просмотр рассылок
    if not request.user.has_perm('letters.can_view_mailing'):
        # запрашиваем записи с фильтром по создателю
        mailing_list = Mailing.objects.filter(creator=request.user)
        HttpResponseForbidden ('Нет прав')
    else:
        mailings = Mailing.objects.none()
        # если права есть то выдаем все записи без фильтрации
        mailing_list = Mailing.objects.all()   


    print (' права на рассылки', Permission.objects.filter(group__in=request.user.groups.all()).distinct().values_list('name', flat=True).first())

    context = {
        'object_list': mailing_list,
        'name_list': Mailing._meta.verbose_name_plural,
        'active_menu': 'mailings',
    }
    return render(request, 'letters/mailing_list.html', context)


def get_message_list(request):
    messages_list = Message.objects.all()
    context = {
        'object_list': messages_list,
        'name_list': Message._meta.verbose_name_plural,
        'active_menu': 'messages',
    }
    return render(request, 'letters/message_list.html', context)


def get_letters_list(request):
    mailing_list = Mailing.objects.all()
    context = {
        'object_list': mailing_list,
        'name_list': Mailing._meta.verbose_name_plural
    }
    return render(request, 'letters/letters_list.html', context)


class MailingCreateView(CreateView):
    model = Mailing
    form_class = MailingForm
    success_url = reverse_lazy('mailing_list')

    def form_valid(self, form):
        # Устанавливаем текущего пользователя как создателя рассылки
        form.instance.creator = self.request.user
        return super().form_valid(form)

class MessageCreateView(CreateView):
    model = Message
    form_class = MessageForm
    success_url = reverse_lazy('message_list')


class СustomerCreateView(CreateView):
    model = Customer
    form_class = CustomerForm
    success_url = reverse_lazy('customer_list')


class MailingDeleteView(DeleteView):
    model = Mailing
    template_name = 'letters/mailing_delete.html'
    success_url = reverse_lazy('mailing_list')


class CustomerDeleteView(DeleteView):
    model = Customer
    template_name = 'letters/customer_delete.html'
    success_url = reverse_lazy('customer_list')



class MessageDeleteView(DeleteView):
    model = Message
    template_name = 'letters/message_delete.html'
    success_url = reverse_lazy('message_list')


class MessageUpdateView(UpdateView):
    model = Message
    form_class = MessageForm
    template_name = 'letters/message_edit.html'  # Укажите ваш шаблон
    success_url = reverse_lazy('message_list')  # URL для перенаправления после успешного редактирования


class СustomerUpdateView(UpdateView):
    model = Customer
    form_class = CustomerForm
    template_name = 'letters/customer_edit.html'  # Укажите ваш шаблон
    success_url = reverse_lazy('customer_list')  # URL для перенаправления после успешного редактирования




def mailing_report(request):
    mailings = Mailing.objects.prefetch_related('customers', 'attemtps').filter(creator=request.user)
    context = {
        'mailings': mailings,
        'active_menu': 'orders',
    }
    return render(request, 'letters/mailing_report.html', context)

def MessageSend(request, pk):
    current_mailing = get_object_or_404(Mailing.objects.prefetch_related('customers', 'messages'), id=pk)
    # Извлекаем email клиентов
    customer_emails = [customer.email for customer in current_mailing.customers.all()]
    # Извлекаем тело сообщения
    message_body = current_mailing.messages.body if current_mailing.messages else None
    # Рассылаем 
    for m in customer_emails:
        send_email(m, message_body, pk)
    return redirect('mailing_list')

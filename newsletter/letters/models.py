from django.db import models
from django.utils import timezone
from django.db.models.signals import post_save, m2m_changed
from django.dispatch import receiver
from letters.tasks import add_mytask
from users.models import User



class Customer(models.Model):
    """Class Клиент сервиса"""
    email = models.EmailField(max_length=254, unique=True,
                              verbose_name='Контактный Email')
    first_name = models.CharField(max_length=100, verbose_name='Имя')
    last_name = models.CharField(max_length=100, verbose_name='Фамилия')
    patronymic = models.CharField(max_length=100, blank=True, null=True,
                                  verbose_name='Отчество')
    comment = models.TextField(blank=True,
                               null=True, verbose_name='Комментарий')

    def __str__(self):
        return f"{self.last_name} {self.first_name} {self.patronymic or ''}".strip()

    class Meta:
        verbose_name = 'Клиент'
        verbose_name_plural = 'Клиенты'
        permissions = [
                ("can_view_customer", "Может просматривать получателей"),
                ("can_edit_customer", "Может редактировать получателей"),
                ("can_delete_customer", "Может удалять получателей"),
            ]
# Сообщение для рассылки:
# тема письма,
# тело письма.


class Message(models.Model):
    subject = models.CharField(max_length=255, verbose_name='Тема письма')
    body = models.TextField(verbose_name='Тело письма')

    def __str__(self):
        return self.subject

    class Meta:
        verbose_name = 'Сообщение'
        verbose_name_plural = 'Сообщения'    
        permissions = [
                ("can_view_message", "Может просматривать сообщение"),
                ("can_edit_message", "Может редактировать сообщение"),
                ("can_delete_message", "Может удалять сообщение"),
            ]
# Попытка рассылки:
# дата и время последней попытки;
# статус попытки (успешно / не успешно);
# ответ почтового сервера, если он был.


class MailingAttempt(models.Model):
    STATUS_CHOICES = [
        ('successful', 'Успешно'),
        ('failed', 'Не успешно'),
    ]
    attempt_time = models.DateTimeField(default=timezone.now,
                                        verbose_name='Дата и время последней попытки')
    status = models.CharField(max_length=10, choices=STATUS_CHOICES,
                              verbose_name='Статус попытки')
    server_response = models.TextField(blank=True, null=True,
                                       verbose_name='Ответ почтового сервера')

    def __str__(self):
        return f"Попытка рассылки {self.mailing.id} - Статус: {self.get_status_display()}"

    class Meta:
        verbose_name = 'Попытка рассылки'
        verbose_name_plural = 'Попытки рассылки'

# Рассылка (настройки):
# дата и время первой отправки рассылки;
# периодичность: раз в день, раз в неделю, раз в месяц;
# статус рассылки (например, завершена, создана, запущена).


class Mailing(models.Model):
    PERIODICITY_CHOICES = [
        ('daily', 'Раз в день'),
        ('weekly', 'Раз в неделю'),
        ('monthly', 'Раз в месяц'),
    ]

    STATUS_CHOICES = [
        ('created', 'Создана'),
        ('running', 'Запущена'),
        ('completed', 'Завершена'),
    ]

    first_send_time = models.DateTimeField(default=timezone.now,
                                           verbose_name='Дата и время первой отправки')
    periodicity = models.CharField(max_length=10, choices=PERIODICITY_CHOICES,
                                   verbose_name='Периодичность')
    status = models.CharField(max_length=10, choices=STATUS_CHOICES,
                              default='created', verbose_name='Статус рассылки')

    # Связь с моделью Customer
    customers = models.ManyToManyField(Customer,
                                       related_name='mailings_cistomers',
                                       verbose_name='Клиенты')

    # Связь с моделью Message
    messages = models.ForeignKey(Message, on_delete=models.DO_NOTHING,
                                 related_name='mailings_messages',
                                 verbose_name='Сообщение')

    # Связь с моделью MailingAttempt
    attemtps = models.ManyToManyField(MailingAttempt,
                                      related_name='mailings_attempts',
                                      verbose_name='Попытки', blank=True)


    # Создатель рассылки
    creator = models.ForeignKey(User, on_delete=models.CASCADE, related_name='mailings_created', verbose_name='Создатель', blank=True, null=True,)

    def __str__(self):
        return f"Рассылка: {self.get_periodicity_display()} - Статус: {self.get_status_display()}"

    def attempts_count(self):
        return self.attemtps.count()

    class Meta:
        verbose_name = 'Рассылка'
        verbose_name_plural = 'Рассылки'
        permissions = [
            ("can_view_mailing", "Может просматривать рассылки"),
            ("can_edit_mailing", "Может редактировать рассылки"),
            ("can_delete_mailing", "Может удалять рассылки"),
        ]


# @receiver(post_save, sender=Mailing)
# def mailing_post_save(sender, instance, created, **kwargs):
#     if created or instance.status != 'created':
#         # Извлекаем список email-адресов клиентов
#         emails = instance.customers.values_list('email', flat=True)
#         add_mytask(instance, instance.periodicity, instance.first_send_time, list(emails))


@receiver(post_save, sender=Mailing)
def mailing_post_save(sender, instance, created, **kwargs):
    if created or instance.status != 'created':
        # Извлекаем список email-адресов из сообщения
        message_emails = [instance.messages.body] if instance.messages else []

        add_mytask(instance.id, instance.periodicity, [], message_emails)


@receiver(m2m_changed, sender=Mailing.customers.through)
def mailing_customers_changed(sender, instance, action, **kwargs):
    if action in ['post_add', 'post_remove', 'post_clear']:
        # Извлекаем список email-адресов клиентов
        customer_emails = list(instance.customers.values_list('email',
                                                              flat=True))

        # Извлекаем список email-адресов из сообщения
        message_emails = [instance.messages.body] if instance.messages else []

        add_mytask(instance.id, instance.periodicity, customer_emails,
                   message_emails)

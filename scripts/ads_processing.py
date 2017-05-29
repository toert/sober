from bot.models import Ad
from bot.tasks import ya_obezyanka


def queryset_to_list(queryset):
    return [result[0] for result in list(queryset)]


def run():
    all_ad_ids_list = queryset_to_list(Ad.objects.values_list('id'))
    ya_obezyanka(all_ad_ids_list)
    #update_task_ad.apply_async(all_ad_ids_list)
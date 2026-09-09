import os
import sys
import django

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.production')
django.setup()

from apps.literasi.models import LiterasiReport
from apps.gamification.models import XPHistory
from apps.accounts.models import User

# 1. Clean Anita (id 130)
anita_reports = list(LiterasiReport.objects.filter(user_id=130, week_number=2).order_by('-created_at'))
if len(anita_reports) > 1:
    keep = anita_reports[0]
    to_delete = anita_reports[1:]
    del_ids = [r.id for r in to_delete]
    LiterasiReport.objects.filter(id__in=del_ids).delete()
    print(f"Anita: Kept report {keep.id}, deleted {len(del_ids)} duplicates.")

    # Clean Anita XP
    anita_xp = list(XPHistory.objects.filter(user_id=130, category='literasi', description__icontains='Minggu Ke-2').order_by('-created_at'))
    if len(anita_xp) > 1:
        extra_xp = sum(x.amount for x in anita_xp[1:])
        del_xp_ids = [x.id for x in anita_xp[1:]]
        XPHistory.objects.filter(id__in=del_xp_ids).delete()
        user_anita = User.objects.get(id=130)
        user_anita.xp = max(0, user_anita.xp - extra_xp)
        user_anita.recalculate_level()
        user_anita.save(update_fields=['xp', 'level'])
        print(f"Anita: Deducted {extra_xp} excess XP. New XP: {user_anita.xp}, Level: {user_anita.level}")

# 2. Clean Alya (id 209)
alya_reports = list(LiterasiReport.objects.filter(user_id=209, week_number=2).order_by('-created_at'))
if len(alya_reports) > 1:
    keep = alya_reports[0]
    to_delete = alya_reports[1:]
    del_ids = [r.id for r in to_delete]
    LiterasiReport.objects.filter(id__in=del_ids).delete()
    print(f"Alya: Kept report {keep.id}, deleted {len(del_ids)} duplicates.")

    # Clean Alya XP
    alya_xp = list(XPHistory.objects.filter(user_id=209, category='literasi', description__icontains='Minggu Ke-2').order_by('-created_at'))
    if len(alya_xp) > 1:
        extra_xp = sum(x.amount for x in alya_xp[1:])
        del_xp_ids = [x.id for x in alya_xp[1:]]
        XPHistory.objects.filter(id__in=del_xp_ids).delete()
        user_alya = User.objects.get(id=209)
        user_alya.xp = max(0, user_alya.xp - extra_xp)
        user_alya.recalculate_level()
        user_alya.save(update_fields=['xp', 'level'])
        print(f"Alya: Deducted {extra_xp} excess XP. New XP: {user_alya.xp}, Level: {user_alya.level}")

print("CLEANUP COMPLETED!")

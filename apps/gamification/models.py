from django.db import models
from django.conf import settings


class XPHistory(models.Model):
    """
    Riwayat perolehan XP siswa (Modul, LKPD, Literasi, Quiz TKA, Peer Review).
    """
    CATEGORY_CHOICES = [
        ('modul', 'Penyelesaian Modul'),
        ('lkpd', 'Pengumpulan LKPD'),
        ('tka', 'Simulasi CBT TKA'),
        ('literasi', 'Rabu Literasi RESIK'),
        ('peer_review', 'Peer Review Literasi'),
        ('streak', 'Daily Streak Bonus'),
        ('teacher', 'Apresiasi Guru'),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='xp_history')
    amount = models.PositiveIntegerField(verbose_name='Jumlah XP')
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, verbose_name='Kategori Perolehan')
    description = models.CharField(max_length=255, verbose_name='Keterangan Aktivitas')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Riwayat XP'
        verbose_name_plural = 'Daftar Riwayat XP'
        ordering = ['-created_at']

    def __str__(self):
        return f"+{self.amount} XP - {self.user.display_name} ({self.category})"

from django import forms
from django.contrib import admin, messages
from django.core.exceptions import PermissionDenied, ValidationError
from django.db.models import Count, Q
from django.template.response import TemplateResponse
from django.urls import path, reverse

from .models import (
    CpnsAttempt,
    CpnsPackage,
    CpnsQuestion,
    PaketBelajar,
    PaketSoal,
    PengaturanCPNS,
    SkemaBagian,
    SkemaUjian,
    Voucher,
)
from .voucher import buat_voucher


@admin.register(CpnsPackage)
class CpnsPackageAdmin(admin.ModelAdmin):
    list_display = ('kode', 'judul', 'tipe_ujian', 'kategori', 'durasi_menit', 'urutan', 'is_published')
    list_filter = ('tipe_ujian', 'kategori', 'is_published')
    search_fields = ('kode', 'judul', 'deskripsi')
    prepopulated_fields = {'slug': ('judul',)}
    ordering = ('urutan',)


@admin.register(CpnsQuestion)
class CpnsQuestionAdmin(admin.ModelAdmin):
    list_display = ('package', 'urutan', 'subtes', 'subtopik', 'kunci_jawaban')
    list_filter = ('subtes', 'package')
    search_fields = ('pertanyaan', 'subtopik', 'bedah_konsep', 'alasan_pengecoh', 'tips_cepat')
    ordering = ('package', 'urutan')
    fieldsets = (
        ('Identitas Soal', {
            'fields': ('package', 'subtes', 'subtopik', 'urutan')
        }),
        ('Narasi & Pilihan Jawaban', {
            'fields': ('pertanyaan', 'opsi_a', 'opsi_b', 'opsi_c', 'opsi_d', 'opsi_e', 'kunci_jawaban', 'bobot_tkp')
        }),
        ('Pembahasan Konsep Tuntas (3 Tingkat)', {
            'fields': ('bedah_konsep', 'alasan_pengecoh', 'tips_cepat')
        }),
    )


@admin.register(CpnsAttempt)
class CpnsAttemptAdmin(admin.ModelAdmin):
    list_display = ('get_peserta', 'package', 'mode', 'total_skor', 'skor_twk', 'skor_tiu', 'skor_tkp', 'status_lulus', 'completed_at')
    list_filter = ('status_lulus', 'mode', 'package')
    search_fields = ('user__username', 'user__email', 'session_key', 'package__kode')
    readonly_fields = ('completed_at',)

    def get_peserta(self, obj):
        return obj.user.display_name if obj.user else f"Guest ({obj.session_key[:8]})"
    get_peserta.short_description = 'Peserta'


SUBTES_PER_JENIS = {
    "SKD": ("TWK", "TIU", "TKP"),
    "SKB_GURU": ("PEDAGOGIK", "MATERI_RPL"),
}


class FilterStatusVoucher(admin.SimpleListFilter):
    title = "status"
    parameter_name = "status"

    def lookups(self, request, model_admin):
        return [
            ("belum_dipakai", "Belum dipakai"),
            ("dipakai", "Dipakai"),
            ("dibatalkan", "Dibatalkan"),
        ]

    def queryset(self, request, queryset):
        nilai = self.value()
        dipakai = Q(dipakai_oleh__isnull=False) | Q(dipakai_pada__isnull=False)
        if nilai == "dibatalkan":
            return queryset.filter(dibatalkan=True)
        if nilai == "dipakai":
            return queryset.filter(dipakai, dibatalkan=False)
        if nilai == "belum_dipakai":
            return queryset.filter(dibatalkan=False).exclude(dipakai)
        return queryset


class FormBuatBanyakVoucher(forms.Form):
    LAIN = "lain"

    jumlah = forms.IntegerField(label="Jumlah kode (1 sampai 100)", min_value=1, max_value=100)
    durasi_hari = forms.ChoiceField(label="Durasi")
    durasi_lain = forms.IntegerField(label="Durasi lain (hari)", min_value=1, required=False)
    catatan = forms.CharField(label="Catatan", max_length=200, required=False)

    def __init__(self, *args, durasi_tersedia=(), **kwargs):
        super().__init__(*args, **kwargs)
        pilihan = [(str(d), f"{d} hari") for d in durasi_tersedia]
        pilihan.append((self.LAIN, "Angka lain"))
        self.fields["durasi_hari"].choices = pilihan

    def clean(self):
        data = super().clean()
        if data.get("durasi_hari") == self.LAIN and not data.get("durasi_lain"):
            self.add_error("durasi_lain", "Isi jumlah hari.")
        return data

    def durasi(self):
        d = self.cleaned_data
        if d["durasi_hari"] == self.LAIN:
            return d["durasi_lain"]
        return int(d["durasi_hari"])


@admin.register(Voucher)
class VoucherAdmin(admin.ModelAdmin):
    list_display = (
        "kode",
        "durasi_hari",
        "status_teks",
        "catatan",
        "dipakai_oleh",
        "dipakai_pada",
        "dibuat_pada",
    )
    list_filter = (FilterStatusVoucher,)
    search_fields = ("kode", "catatan", "dipakai_oleh__email")
    fields = (
        "kode",
        "durasi_hari",
        "catatan",
        "dibatalkan",
        "dibuat_oleh",
        "dibuat_pada",
        "dipakai_oleh",
        "dipakai_pada",
    )
    readonly_fields = (
        "kode",
        "durasi_hari",
        "dibuat_oleh",
        "dibuat_pada",
        "dipakai_oleh",
        "dipakai_pada",
    )
    actions = ["batalkan_belum_dipakai"]
    change_list_template = "admin/cpns/voucher/change_list.html"

    @admin.display(description="Status")
    def status_teks(self, obj):
        return {
            "belum_dipakai": "Belum dipakai",
            "dipakai": "Dipakai",
            "dibatalkan": "Dibatalkan",
        }[obj.status]

    def has_add_permission(self, request):
        return False

    @admin.action(description="Batalkan kode yang belum dipakai")
    def batalkan_belum_dipakai(self, request, queryset):
        jumlah = queryset.filter(
            dibatalkan=False, dipakai_oleh__isnull=True, dipakai_pada__isnull=True
        ).update(dibatalkan=True)
        self.message_user(request, f"{jumlah} kode dibatalkan.", messages.SUCCESS)

    def get_urls(self):
        tambahan = [
            path(
                "buat-banyak/",
                self.admin_site.admin_view(self.buat_banyak_view),
                name="cpns_voucher_buat_banyak",
            )
        ]
        return tambahan + super().get_urls()

    def buat_banyak_view(self, request):
        if not self.has_change_permission(request):
            raise PermissionDenied
        konteks = dict(
            self.admin_site.each_context(request),
            title="Buat kode voucher",
            opts=self.model._meta,
            kembali=reverse("admin:cpns_voucher_changelist"),
        )
        durasi = PengaturanCPNS.ambil().durasi_tersedia()
        if request.method == "POST":
            form = FormBuatBanyakVoucher(request.POST, durasi_tersedia=durasi)
            if form.is_valid():
                try:
                    hasil = buat_voucher(
                        form.cleaned_data["jumlah"],
                        form.durasi(),
                        catatan=form.cleaned_data["catatan"],
                        oleh=request.user,
                    )
                except ValueError as e:
                    form.add_error(None, str(e))
                else:
                    konteks.update(
                        title="Kode voucher dibuat",
                        daftar_kode="\n".join(v.kode for v in hasil),
                        jumlah=len(hasil),
                        durasi_hari=form.durasi(),
                    )
                    return TemplateResponse(
                        request, "admin/cpns/voucher/buat_banyak.html", konteks
                    )
        else:
            form = FormBuatBanyakVoucher(durasi_tersedia=durasi)
        konteks["form"] = form
        return TemplateResponse(request, "admin/cpns/voucher/buat_banyak.html", konteks)


class SkemaBagianInlineFormSet(forms.BaseInlineFormSet):
    def clean(self):
        super().clean()
        # jenis_ujian ada di form induk, jadi dibaca dari data POST.
        jenis = self.data.get("jenis_ujian") or self.instance.jenis_ujian
        boleh = SUBTES_PER_JENIS.get(jenis)
        for form in self.forms:
            cd = getattr(form, "cleaned_data", None)
            if not cd or cd.get("DELETE") or not cd.get("subtes"):
                continue
            if boleh and cd["subtes"] not in boleh:
                raise ValidationError(
                    f"Subtes {cd['subtes']} tidak cocok dengan jenis ujian {jenis}. "
                    f"Pilih salah satu: {', '.join(boleh)}."
                )
            per_soal = 5 if cd.get("cara_nilai") == "bobot_opsi" else (cd.get("poin_benar") or 0)
            maks = (cd.get("jumlah_soal") or 0) * per_soal
            if (cd.get("ambang_batas") or 0) > maks:
                raise ValidationError(
                    f"Ambang batas {cd['ambang_batas']} melebihi nilai maksimal "
                    f"bagian {cd['subtes']} ({maks})."
                )


class SkemaBagianInline(admin.TabularInline):
    model = SkemaBagian
    formset = SkemaBagianInlineFormSet
    extra = 1


@admin.register(SkemaUjian)
class SkemaUjianAdmin(admin.ModelAdmin):
    list_display = ("kode", "nama", "jenis_ujian", "durasi_menit", "aktif", "urutan")
    list_filter = ("jenis_ujian", "aktif")
    search_fields = ("kode", "nama")
    inlines = [SkemaBagianInline]


class PaketSoalInline(admin.TabularInline):
    model = PaketSoal
    raw_id_fields = ("soal",)
    extra = 1


@admin.register(PaketBelajar)
class PaketBelajarAdmin(admin.ModelAdmin):
    list_display = ("nama", "jenis_ujian", "untuk_trial", "aktif", "jumlah_tayang")
    list_filter = ("jenis_ujian", "untuk_trial", "aktif")
    search_fields = ("nama",)
    inlines = [PaketSoalInline]

    @admin.display(description="Soal tayang")
    def jumlah_tayang(self, obj):
        return obj.isi.filter(soal__status="tayang").count()


class PengaturanCPNSForm(forms.ModelForm):
    class Meta:
        model = PengaturanCPNS
        fields = "__all__"

    def clean_pesan_wa(self):
        pesan = self.cleaned_data["pesan_wa"]
        try:
            pesan.format(durasi=30, email="contoh@email.com")
        except Exception:
            raise ValidationError(
                "Template pesan tidak valid. Gunakan hanya {durasi} dan {email}."
            )
        return pesan


@admin.register(PengaturanCPNS)
class PengaturanCPNSAdmin(admin.ModelAdmin):
    form = PengaturanCPNSForm

    def has_add_permission(self, request):
        return not PengaturanCPNS.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False

def global_context(request):
    """
    Menyediakan variabel konteks global untuk konsistensi identitas vokasi & branding.
    """
    return {
        'SITE_TITLE': 'Agung Gumelar Saputra, S.Tr.T.',
        'TEACHER_NAME': 'Agung Gumelar Saputra, S.Tr.T.',
        'TEACHER_ROLE': 'Guru Pengampu RPL & Fullstack Software Engineer',
        'SCHOOL_NAME': 'SMKN 1 Rongga',
        'PROGRAM_KEAHLIAN': 'Pengembangan Perangkat Lunak dan Gim (PPLG)',
        'KONSENTRASI_KEAHLIAN': 'Rekayasa Perangkat Lunak (RPL)',
        'ACADEMIC_YEAR': '2025/2026',
    }

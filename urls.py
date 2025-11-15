"""
URL configuration for EVM Backend
"""
from django.contrib import admin
from django.urls import path, include
from views import (
    index,
    get_all_fingerprints,
    get_fingerprint_count,
    get_fingerprint_by_id,
    get_fingerprint_by_key,
    get_statistics,
    get_verification_template,
    verify_fingerprint,
    enroll_fingerprint,
    verify_fingerprint_esp32,
    get_blockchain_info,
    get_audit_trail,
    validate_blockchain,
    record_vote,
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', index, name='index'),
    
    # Fingerprint endpoints
    path('api/fingerprints/', get_all_fingerprints, name='get_all_fingerprints'),
    path('api/fingerprints/count/', get_fingerprint_count, name='get_fingerprint_count'),
    path('api/fingerprints/id/<int:template_id>/', get_fingerprint_by_id, name='get_fingerprint_by_id'),
    path('api/fingerprints/key/<str:template_key>/', get_fingerprint_by_key, name='get_fingerprint_by_key'),
    path('api/fingerprints/enroll/', enroll_fingerprint, name='enroll_fingerprint'),
    
    # Verification endpoints
    path('api/verification/template/', get_verification_template, name='get_verification_template'),
    path('api/verification/verify/', verify_fingerprint_esp32, name='verify_fingerprint_esp32'),
    
    # Blockchain endpoints
    path('api/blockchain/info/', get_blockchain_info, name='get_blockchain_info'),
    path('api/blockchain/audit/', get_audit_trail, name='get_audit_trail'),
    path('api/blockchain/validate/', validate_blockchain, name='validate_blockchain'),
    path('api/blockchain/vote/', record_vote, name='record_vote'),
    
    # Statistics endpoint
    path('api/statistics/', get_statistics, name='get_statistics'),
]

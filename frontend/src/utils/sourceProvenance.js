export function isGeneratedDemo(source) {
  return source?.is_generated_summary === true || source?.content_type === 'generated_demo';
}

export function isVerifiedOfficialSource(source) {
  return !isGeneratedDemo(source)
    && source?.content_type === 'official_document'
    && source?.reference_status === 'verified'
    && source?.verification_method === 'manual_origin_and_sha256_review';
}

export function getSourceTrustLabel(source) {
  if (isGeneratedDemo(source)) return 'Generated demo — not an official publication';
  if (isVerifiedOfficialSource(source)) return 'Verified official source';
  return 'Unverified source';
}

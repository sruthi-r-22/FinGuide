export function isGeneratedDemo(source) {
  return source?.is_generated_summary === true || source?.content_type === 'generated_demo';
}

export function isVerifiedOfficialSource(source) {
  if (isGeneratedDemo(source)
    || source?.content_type !== 'official_document'
    || source?.reference_status !== 'verified'
    || source?.verification_method !== 'manual_origin_and_sha256_review'
    || source?.is_generated_summary !== false) {
    return false;
  }

  const publisherHosts = {
    'Reserve Bank of India': ['rbi.org.in', 'www.rbi.org.in'],
    'National Payments Corporation of India': ['npci.org.in', 'www.npci.org.in'],
  };
  const hosts = publisherHosts[source.publisher];
  if (!hosts || !source.source_url) return false;

  try {
    const url = new URL(source.source_url);
    return url.protocol === 'https:'
      && !url.username
      && !url.password
      && hosts.includes(url.hostname);
  } catch {
    return false;
  }
}

export function getSourceTrustLabel(source) {
  if (isGeneratedDemo(source)) return 'Generated demo — not an official publication';
  if (isVerifiedOfficialSource(source)) return 'Verified official source';
  return 'Unverified source';
}

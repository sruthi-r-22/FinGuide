import test from 'node:test';
import assert from 'node:assert/strict';

import {
  getSourceTrustLabel,
  isGeneratedDemo,
  isVerifiedOfficialSource,
} from '../src/utils/sourceProvenance.js';

test('generated demo remains unverified even when its title mentions an authority', () => {
  const source = {
    document_title: 'NPCI UPI Safety Summary',
    content_type: 'generated_demo',
    is_generated_summary: true,
    reference_status: 'unverified',
    source_url: 'https://www.npci.org.in/what-we-do/upi/faqs',
  };

  assert.equal(isGeneratedDemo(source), true);
  assert.equal(isVerifiedOfficialSource(source), false);
  assert.equal(getSourceTrustLabel(source), 'Generated demo — not an official publication');
});

test('a verified label requires the ingestion verification method', () => {
  const source = {
    content_type: 'official_document',
    reference_status: 'verified',
    is_generated_summary: false,
  };

  assert.equal(isVerifiedOfficialSource(source), false);
  assert.equal(getSourceTrustLabel(source), 'Unverified source');
});

test('verified official metadata receives the official label', () => {
  const source = {
    publisher: 'National Payments Corporation of India',
    content_type: 'official_document',
    reference_status: 'verified',
    verification_method: 'manual_origin_and_sha256_review',
    is_generated_summary: false,
    source_url: 'https://www.npci.org.in/what-we-do/upi/faqs',
  };

  assert.equal(isVerifiedOfficialSource(source), true);
  assert.equal(getSourceTrustLabel(source), 'Verified official source');
});

test('missing source URL cannot receive an official label', () => {
  const source = {
    publisher: 'National Payments Corporation of India',
    content_type: 'official_document',
    reference_status: 'verified',
    verification_method: 'manual_origin_and_sha256_review',
    is_generated_summary: false,
  };

  assert.equal(isVerifiedOfficialSource(source), false);
  assert.equal(getSourceTrustLabel(source), 'Unverified source');
});

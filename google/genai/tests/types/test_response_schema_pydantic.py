# Copyright 2025 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

"""Transparent downstream contribution by Troy Bacon on his fork, not upstream authorship."""

import json
from typing import List, Optional

import pydantic

from ... import types


class Sponsor(pydantic.BaseModel):
  name: str
  website: Optional[str] = None


class SponsorMatch(pydantic.BaseModel):
  sponsor: Sponsor
  confidence: float
  evidence: List[str]
  contact_email: Optional[str] = None


class SponsorMatchResponse(pydantic.BaseModel):
  query: str
  matches: List[SponsorMatch]
  unmatched_reasons: Optional[List[str]] = None


def test_nested_sponsor_match_response_schema_and_parsed():
  """Parses nested sponsor matches while preserving optional fields."""
  response_schema = SponsorMatchResponse
  generated_json = {
      'query': 'community science fair',
      'matches': [
          {
              'sponsor': {
                  'name': 'Acme Labs',
                  'website': 'https://example.test/acme',
              },
              'confidence': 0.94,
              'evidence': [
                  'Funds youth science programs',
                  'Accepts community event proposals',
              ],
          },
          {
              'sponsor': {'name': 'Northwind Foundation'},
              'confidence': 0.61,
              'evidence': ['Supports local education'],
              'contact_email': 'grants@example.test',
          },
      ],
      'unmatched_reasons': None,
  }

  response = types.GenerateContentResponse._from_response(
      response={
          'candidates': [
              {
                  'content': {
                      'parts': [{'text': json.dumps(generated_json)}],
                  },
              }
          ],
      },
      kwargs={'config': {'response_schema': response_schema}},
  )

  schema = response_schema.model_json_schema()
  assert schema['properties']['matches']['items']['$ref'].endswith(
      '/$defs/SponsorMatch'
  )
  assert isinstance(response.parsed, SponsorMatchResponse)
  assert response.parsed.query == 'community science fair'
  assert len(response.parsed.matches) == 2
  assert isinstance(response.parsed.matches[0], SponsorMatch)
  assert isinstance(response.parsed.matches[0].sponsor, Sponsor)
  assert response.parsed.matches[0].sponsor.website == 'https://example.test/acme'
  assert response.parsed.matches[1].sponsor.website is None
  assert response.parsed.matches[1].contact_email == 'grants@example.test'
  assert response.parsed.unmatched_reasons is None

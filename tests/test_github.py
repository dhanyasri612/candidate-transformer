import unittest
from unittest.mock import patch, MagicMock
import requests

from github.github_client import get_github_profile
from github.github_enricher import enrich_candidate_with_github
from models.canonical_schema import Candidate


class TestGitHubEnrichment(unittest.TestCase):

    @patch('requests.get')
    def test_valid_github_url(self, mock_get):
        # Simulate successful API response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "login": "octocat",
            "name": "The Octocat",
            "bio": "Testing GitHub API",
            "company": "GitHub",
            "location": "San Francisco",
            "public_repos": 8,
            "followers": 120,
            "following": 9,
            "html_url": "https://github.com/octocat",
            "avatar_url": "https://avatars.githubusercontent.com/u/5832347?v=4"
        }
        mock_get.return_value = mock_response

        # Test client
        profile = get_github_profile("https://github.com/octocat")
        self.assertIsNotNone(profile)
        self.assertEqual(profile["login"], "octocat")
        self.assertEqual(profile["name"], "The Octocat")

        # Test enricher
        candidate = Candidate(full_name="John Doe")
        enrich_candidate_with_github(candidate, "https://github.com/octocat")
        
        self.assertEqual(candidate.github_profile["username"], "octocat")
        self.assertEqual(candidate.github_profile["followers"], 120)
        self.assertEqual(candidate.github_profile["company"], "GitHub")

    def test_invalid_url(self):
        # Test with an invalid URL where username cannot be extracted
        profile = get_github_profile("https://google.com")
        self.assertIsNone(profile)

        candidate = Candidate(full_name="John Doe")
        enrich_candidate_with_github(candidate, "https://google.com")
        self.assertEqual(candidate.github_profile, {})

    def test_empty_input(self):
        # Test with empty input
        profile = get_github_profile("")
        self.assertIsNone(profile)

        candidate = Candidate(full_name="John Doe")
        enrich_candidate_with_github(candidate, "")
        self.assertEqual(candidate.github_profile, {})

    @patch('requests.get')
    def test_user_not_found(self, mock_get):
        # Simulate 404 Not Found
        mock_response = MagicMock()
        mock_response.status_code = 404
        mock_get.return_value = mock_response

        profile = get_github_profile("https://github.com/nonexistent_user_12345")
        self.assertIsNone(profile)

        candidate = Candidate(full_name="John Doe")
        enrich_candidate_with_github(candidate, "https://github.com/nonexistent_user_12345")
        self.assertEqual(candidate.github_profile, {})

    @patch('requests.get')
    def test_api_unavailable_or_rate_limited(self, mock_get):
        # Simulate 403 Forbidden (Rate limit)
        mock_response = MagicMock()
        mock_response.status_code = 403
        mock_get.return_value = mock_response

        profile = get_github_profile("https://github.com/octocat")
        self.assertIsNone(profile)

        candidate = Candidate(full_name="John Doe")
        enrich_candidate_with_github(candidate, "https://github.com/octocat")
        self.assertEqual(candidate.github_profile, {})

    @patch('requests.get')
    def test_network_failure(self, mock_get):
        # Simulate network exception
        mock_get.side_effect = requests.exceptions.ConnectionError("Connection refused")

        profile = get_github_profile("https://github.com/octocat")
        self.assertIsNone(profile)

        candidate = Candidate(full_name="John Doe")
        enrich_candidate_with_github(candidate, "https://github.com/octocat")
        self.assertEqual(candidate.github_profile, {})


if __name__ == "__main__":
    unittest.main()

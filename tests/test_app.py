"""
Backend tests for the Mergington High School Activities API.

Tests use the AAA (Arrange-Act-Assert) pattern:
- Arrange: Set up test data and preconditions
- Act: Execute the code being tested
- Assert: Verify the results
"""

import pytest


class TestGetActivities:
    """Tests for GET /activities endpoint."""

    def test_get_activities_success(self, client):
        """
        Test that GET /activities returns all activities with correct structure.
        
        Arrange: Client is ready
        Act: Request all activities
        Assert: Response contains activities with expected fields
        """
        # Arrange
        expected_activity = "Chess Club"
        
        # Act
        response = client.get("/activities")
        
        # Assert
        assert response.status_code == 200
        activities = response.json()
        assert isinstance(activities, dict)
        assert expected_activity in activities
        assert "description" in activities[expected_activity]
        assert "schedule" in activities[expected_activity]
        assert "max_participants" in activities[expected_activity]
        assert "participants" in activities[expected_activity]

    def test_get_activities_has_participants(self, client):
        """
        Test that activities include existing participants.
        
        Arrange: Chess Club has pre-registered participants
        Act: Request all activities
        Assert: Participants list is populated
        """
        # Arrange
        activity_name = "Chess Club"
        
        # Act
        response = client.get("/activities")
        activities = response.json()
        
        # Assert
        assert len(activities[activity_name]["participants"]) > 0
        assert "michael@mergington.edu" in activities[activity_name]["participants"]


class TestSignupForActivity:
    """Tests for POST /activities/{activity_name}/signup endpoint."""

    def test_signup_success(self, client):
        """
        Test successful signup for an activity.
        
        Arrange: New student email and activity name
        Act: Submit signup request
        Assert: Response confirms signup and participant is added
        """
        # Arrange
        activity_name = "Chess Club"
        email = "newstudent@mergington.edu"
        
        # Act
        response = client.post(
            f"/activities/{activity_name}/signup?email={email}"
        )
        
        # Assert
        assert response.status_code == 200
        result = response.json()
        assert "message" in result
        assert email in result["message"]
        assert activity_name in result["message"]

    def test_signup_adds_participant(self, client):
        """
        Test that signup actually adds participant to activity.
        
        Arrange: Fresh student email
        Act: Sign up for activity, then fetch activities
        Assert: Participant is in the activity's participant list
        """
        # Arrange
        activity_name = "Programming Class"
        email = "alice@mergington.edu"
        
        # Act
        signup_response = client.post(
            f"/activities/{activity_name}/signup?email={email}"
        )
        activities_response = client.get("/activities")
        
        # Assert
        assert signup_response.status_code == 200
        activities = activities_response.json()
        assert email in activities[activity_name]["participants"]

    def test_signup_already_registered_fails(self, client):
        """
        Test that signing up an already-registered student fails.
        
        Arrange: Student already signed up for activity
        Act: Attempt to signup the same student again
        Assert: Request fails with 400 status
        """
        # Arrange
        activity_name = "Chess Club"
        email = "michael@mergington.edu"  # Already registered
        
        # Act
        response = client.post(
            f"/activities/{activity_name}/signup?email={email}"
        )
        
        # Assert
        assert response.status_code == 400
        result = response.json()
        assert "already signed up" in result["detail"]

    def test_signup_nonexistent_activity_fails(self, client):
        """
        Test that signup for a non-existent activity fails.
        
        Arrange: Activity that doesn't exist
        Act: Attempt to signup for invalid activity
        Assert: Request fails with 404 status
        """
        # Arrange
        activity_name = "Nonexistent Activity"
        email = "student@mergington.edu"
        
        # Act
        response = client.post(
            f"/activities/{activity_name}/signup?email={email}"
        )
        
        # Assert
        assert response.status_code == 404
        result = response.json()
        assert "not found" in result["detail"]


class TestRemoveParticipant:
    """Tests for DELETE /activities/{activity_name}/participants endpoint."""

    def test_remove_participant_success(self, client):
        """
        Test successful removal of a participant.
        
        Arrange: Participant is registered for activity
        Act: Send DELETE request to remove participant
        Assert: Response confirms removal
        """
        # Arrange
        activity_name = "Chess Club"
        email = "michael@mergington.edu"  # Already registered
        
        # Act
        response = client.delete(
            f"/activities/{activity_name}/participants?email={email}"
        )
        
        # Assert
        assert response.status_code == 200
        result = response.json()
        assert "message" in result
        assert email in result["message"]

    def test_remove_participant_actually_removes(self, client):
        """
        Test that removal actually takes effect.
        
        Arrange: Participant is registered
        Act: Remove participant, then fetch activities
        Assert: Participant is no longer in participant list
        """
        # Arrange
        activity_name = "Chess Club"
        email = "michael@mergington.edu"
        
        # Act
        remove_response = client.delete(
            f"/activities/{activity_name}/participants?email={email}"
        )
        activities_response = client.get("/activities")
        
        # Assert
        assert remove_response.status_code == 200
        activities = activities_response.json()
        assert email not in activities[activity_name]["participants"]

    def test_remove_nonexistent_participant_fails(self, client):
        """
        Test that removing a non-registered participant fails.
        
        Arrange: Email not registered for activity
        Act: Attempt to remove unregistered participant
        Assert: Request fails with 404 status
        """
        # Arrange
        activity_name = "Chess Club"
        email = "notregistered@mergington.edu"
        
        # Act
        response = client.delete(
            f"/activities/{activity_name}/participants?email={email}"
        )
        
        # Assert
        assert response.status_code == 404
        result = response.json()
        assert "not found" in result["detail"]

    def test_remove_from_nonexistent_activity_fails(self, client):
        """
        Test that removing from a non-existent activity fails.
        
        Arrange: Activity doesn't exist
        Act: Attempt to remove participant from invalid activity
        Assert: Request fails with 404 status
        """
        # Arrange
        activity_name = "Nonexistent Activity"
        email = "student@mergington.edu"
        
        # Act
        response = client.delete(
            f"/activities/{activity_name}/participants?email={email}"
        )
        
        # Assert
        assert response.status_code == 404
        result = response.json()
        assert "not found" in result["detail"]


class TestIntegrationFlow:
    """Integration tests for complete workflows."""

    def test_signup_and_remove_workflow(self, client):
        """
        Test complete workflow: signup -> verify -> remove -> verify.
        
        Arrange: Student and activity ready
        Act: Sign up, verify, remove, verify again
        Assert: State changes correctly at each step
        """
        # Arrange
        activity_name = "Gym Class"
        email = "testuser@mergington.edu"
        
        # Act 1: Sign up
        signup_response = client.post(
            f"/activities/{activity_name}/signup?email={email}"
        )
        
        # Assert 1: Signup succeeds
        assert signup_response.status_code == 200
        
        # Act 2: Verify signup
        activities_1 = client.get("/activities").json()
        
        # Assert 2: Participant added
        assert email in activities_1[activity_name]["participants"]
        
        # Act 3: Remove participant
        remove_response = client.delete(
            f"/activities/{activity_name}/participants?email={email}"
        )
        
        # Assert 3: Removal succeeds
        assert remove_response.status_code == 200
        
        # Act 4: Verify removal
        activities_2 = client.get("/activities").json()
        
        # Assert 4: Participant removed
        assert email not in activities_2[activity_name]["participants"]

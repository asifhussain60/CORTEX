"""
ADO API Response Fixtures — Single Source of Truth for All 60 Golden Tests.

These payloads are based on real Azure DevOps REST API v7.1 responses with
$expand=all.  All fields are present as they appear in production — no
simplification, no missing nested objects.

Story used across all tests: #692945 "User can reset password via email"
Organisation: HQY01  |  Project: V5  |  Sprint: Sprint 14

Authority: CORE-008 (TDD) · CORE-035 (single canonical fixtures)
"""

from __future__ import annotations

from typing import Any, Dict, List


# ──────────────────────────────────────────────────────────────────────────────
# PRIMARY FIXTURE — Work Item 692945 (User Story, Active)
# Returned by: GET /_apis/wit/workitems/692945?$expand=all&api-version=7.1
# ──────────────────────────────────────────────────────────────────────────────

ADO_STORY_692945_RAW: Dict[str, Any] = {
    "id": 692945,
    "rev": 12,
    "fields": {
        "System.Id": 692945,
        "System.Title": "User can reset password via email",
        "System.State": "Active",
        "System.WorkItemType": "User Story",
        "System.Description": (
            "<div>As a registered user I want to reset my password via email "
            "so that I can regain access when I forget my credentials.</div>"
        ),
        "System.Tags": "auth; security; password-reset",
        "System.AssignedTo": {
            "displayName": "Jane Doe",
            "uniqueName": "jane.doe@company.com",
            "id": "usr-jane-doe-001",
            "imageUrl": "https://dev.azure.com/HQY01/_api/_common/identityImage?id=usr-jane-doe-001",
        },
        "System.AreaPath": "V5\\Authentication",
        "System.IterationPath": "V5\\Sprint 14",
        "System.CreatedDate": "2026-01-15T09:00:00.000Z",
        "System.ChangedDate": "2026-02-20T14:30:00.000Z",
        "System.TeamProject": "V5",
        "System.AreaId": 1042,
        "System.IterationId": 88,
        "System.Reason": "Moved to state Active",
        "System.CommentCount": 3,
        "Microsoft.VSTS.Scheduling.StoryPoints": 5.0,
        "Microsoft.VSTS.Common.Priority": 2,
        "Microsoft.VSTS.Common.AcceptanceCriteria": (
            "<div>"
            "<b>Scenario 1: Successful reset request</b><br/>"
            "Given a registered user is on the login page<br/>"
            "When they click 'Forgot Password' and submit their email<br/>"
            "Then a password reset email is sent within 30 seconds<br/>"
            "<br/>"
            "<b>Scenario 2: Invalid email</b><br/>"
            "Given a user submits an email not registered in the system<br/>"
            "When the reset form is submitted<br/>"
            "Then a generic confirmation message is shown (no account enumeration)<br/>"
            "<br/>"
            "<b>Scenario 3: Expired reset link</b><br/>"
            "Given a user clicks a password reset link older than 24 hours<br/>"
            "When they attempt to set a new password<br/>"
            "Then they see an expiry error and are prompted to request a new link<br/>"
            "</div>"
        ),
        "Microsoft.VSTS.Common.ValueArea": "Business",
        "Microsoft.VSTS.Common.BusinessValue": 100,
        "Microsoft.VSTS.TCM.AutomatedTestName": None,
        "Microsoft.VSTS.TCM.AutomatedTestId": None,
    },
    "relations": [
        # Parent: Epic #689000
        {
            "rel": "System.LinkTypes.Hierarchy-Reverse",
            "url": "https://dev.azure.com/HQY01/_apis/wit/workItems/689000",
            "attributes": {"isLocked": False, "name": "Parent"},
        },
        # Child task: #692946
        {
            "rel": "System.LinkTypes.Hierarchy-Forward",
            "url": "https://dev.azure.com/HQY01/_apis/wit/workItems/692946",
            "attributes": {"isLocked": False, "name": "Child"},
        },
        # Child task: #692947
        {
            "rel": "System.LinkTypes.Hierarchy-Forward",
            "url": "https://dev.azure.com/HQY01/_apis/wit/workItems/692947",
            "attributes": {"isLocked": False, "name": "Child"},
        },
        # Linked Test Case: #700100
        {
            "rel": "Microsoft.VSTS.Common.TestedBy-Forward",
            "url": "https://dev.azure.com/HQY01/_apis/wit/workItems/700100",
            "attributes": {"isLocked": False, "name": "Tested By"},
        },
        # Linked Test Case: #700101
        {
            "rel": "Microsoft.VSTS.Common.TestedBy-Forward",
            "url": "https://dev.azure.com/HQY01/_apis/wit/workItems/700101",
            "attributes": {"isLocked": False, "name": "Tested By"},
        },
        # Linked Pull Request (ArtifactLink)
        {
            "rel": "ArtifactLink",
            "url": "vstfs:///Git/PullRequestId/v5-repo/1337",
            "attributes": {
                "isLocked": False,
                "name": "Pull Request",
                "id": "1337",
            },
        },
    ],
    "_links": {
        "self": {"href": "https://dev.azure.com/HQY01/_apis/wit/workItems/692945"},
        "workItemUpdates": {"href": "https://dev.azure.com/HQY01/_apis/wit/workItems/692945/updates"},
        "workItemRevisions": {"href": "https://dev.azure.com/HQY01/_apis/wit/workItems/692945/revisions"},
        "workItemComments": {"href": "https://dev.azure.com/HQY01/V5/_apis/wit/workItems/692945/comments"},
        "html": {"href": "https://dev.azure.com/HQY01/V5/_workitems/edit/692945"},
        "workItemType": {"href": "https://dev.azure.com/HQY01/V5/_apis/wit/workItemTypes/User%20Story"},
        "fields": {"href": "https://dev.azure.com/HQY01/_apis/wit/fields"},
    },
    "url": "https://dev.azure.com/HQY01/_apis/wit/workItems/692945",
}


# ──────────────────────────────────────────────────────────────────────────────
# CHILD TASK FIXTURE — #692946 (Backend implementation task)
# ──────────────────────────────────────────────────────────────────────────────

ADO_TASK_692946_RAW: Dict[str, Any] = {
    "id": 692946,
    "rev": 5,
    "fields": {
        "System.Id": 692946,
        "System.Title": "Implement password reset API endpoint",
        "System.State": "In Progress",
        "System.WorkItemType": "Task",
        "System.Description": "<div>POST /api/auth/password-reset</div>",
        "System.Tags": "backend; api",
        "System.AssignedTo": {
            "displayName": "Bob Smith",
            "uniqueName": "bob.smith@company.com",
            "id": "usr-bob-smith-001",
        },
        "System.AreaPath": "V5\\Authentication",
        "System.IterationPath": "V5\\Sprint 14",
        "System.TeamProject": "V5",
        "Microsoft.VSTS.Common.Priority": 2,
        "Microsoft.VSTS.Scheduling.RemainingWork": 4.0,
    },
    "relations": [
        {
            "rel": "System.LinkTypes.Hierarchy-Reverse",
            "url": "https://dev.azure.com/HQY01/_apis/wit/workItems/692945",
            "attributes": {"isLocked": False, "name": "Parent"},
        }
    ],
    "_links": {
        "html": {"href": "https://dev.azure.com/HQY01/V5/_workitems/edit/692946"},
    },
    "url": "https://dev.azure.com/HQY01/_apis/wit/workItems/692946",
}


# ──────────────────────────────────────────────────────────────────────────────
# CHILD TASK FIXTURE — #692947 (Frontend implementation task)
# ──────────────────────────────────────────────────────────────────────────────

ADO_TASK_692947_RAW: Dict[str, Any] = {
    "id": 692947,
    "rev": 3,
    "fields": {
        "System.Id": 692947,
        "System.Title": "Implement forgot password UI flow",
        "System.State": "New",
        "System.WorkItemType": "Task",
        "System.Description": "<div>React form + email input + success message</div>",
        "System.Tags": "frontend; ui",
        "System.AssignedTo": None,
        "System.AreaPath": "V5\\Authentication",
        "System.IterationPath": "V5\\Sprint 14",
        "System.TeamProject": "V5",
        "Microsoft.VSTS.Common.Priority": 2,
        "Microsoft.VSTS.Scheduling.RemainingWork": 6.0,
    },
    "relations": [
        {
            "rel": "System.LinkTypes.Hierarchy-Reverse",
            "url": "https://dev.azure.com/HQY01/_apis/wit/workItems/692945",
            "attributes": {"isLocked": False, "name": "Parent"},
        }
    ],
    "_links": {
        "html": {"href": "https://dev.azure.com/HQY01/V5/_workitems/edit/692947"},
    },
    "url": "https://dev.azure.com/HQY01/_apis/wit/workItems/692947",
}


# ──────────────────────────────────────────────────────────────────────────────
# TEST CASE FIXTURE — #700100 (Automated test case linked to story)
# ──────────────────────────────────────────────────────────────────────────────

ADO_TEST_CASE_700100_RAW: Dict[str, Any] = {
    "id": 700100,
    "rev": 8,
    "fields": {
        "System.Id": 700100,
        "System.Title": "Verify password reset email is sent",
        "System.State": "Ready",
        "System.WorkItemType": "Test Case",
        "System.Tags": "automation; regression",
        "System.AreaPath": "V5\\Authentication",
        "System.IterationPath": "V5\\Sprint 14",
        "System.TeamProject": "V5",
        "Microsoft.VSTS.TCM.AutomatedTestName": "AuthTests.PasswordReset.TestEmailSent",
        "Microsoft.VSTS.TCM.AutomatedTestStorage": "auth-tests.dll",
        "Microsoft.VSTS.TCM.AutomatedTestId": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
        "Microsoft.VSTS.TCM.AutomatedTestType": "Unit Test",
    },
    "_links": {
        "html": {"href": "https://dev.azure.com/HQY01/V5/_workitems/edit/700100"},
    },
    "url": "https://dev.azure.com/HQY01/_apis/wit/workItems/700100",
}


# ──────────────────────────────────────────────────────────────────────────────
# WIQL RESPONSE FIXTURE — bulk story query result
# Returned by: POST /{project}/_apis/wit/wiql?api-version=7.1
# ──────────────────────────────────────────────────────────────────────────────

ADO_WIQL_RESPONSE: Dict[str, Any] = {
    "queryType": "flat",
    "queryResultType": "workItem",
    "asOf": "2026-02-25T10:00:00.000Z",
    "columns": [
        {"referenceName": "System.Id", "name": "ID", "url": "https://dev.azure.com/HQY01/_apis/wit/fields/System.Id"},
        {"referenceName": "System.Title", "name": "Title", "url": "https://dev.azure.com/HQY01/_apis/wit/fields/System.Title"},
    ],
    "workItems": [
        {"id": 692945, "url": "https://dev.azure.com/HQY01/_apis/wit/workItems/692945"},
        {"id": 692940, "url": "https://dev.azure.com/HQY01/_apis/wit/workItems/692940"},
        {"id": 692935, "url": "https://dev.azure.com/HQY01/_apis/wit/workItems/692935"},
    ],
}


# ──────────────────────────────────────────────────────────────────────────────
# BATCH RESPONSE FIXTURE — workitemsbatch response
# Returned by: POST /_apis/wit/workitemsbatch?api-version=7.1
# ──────────────────────────────────────────────────────────────────────────────

ADO_BATCH_RESPONSE: Dict[str, Any] = {
    "count": 3,
    "value": [
        {
            "id": 692945,
            "rev": 12,
            "fields": {
                "System.Id": 692945,
                "System.Title": "User can reset password via email",
                "System.State": "Active",
                "System.WorkItemType": "User Story",
                "System.Tags": "auth; security; password-reset",
                "System.AssignedTo": {
                    "displayName": "Jane Doe",
                    "uniqueName": "jane.doe@company.com",
                },
                "System.AreaPath": "V5\\Authentication",
                "System.IterationPath": "V5\\Sprint 14",
                "System.CreatedDate": "2026-01-15T09:00:00.000Z",
                "System.ChangedDate": "2026-02-20T14:30:00.000Z",
                "Microsoft.VSTS.Scheduling.StoryPoints": 5.0,
                "Microsoft.VSTS.Common.Priority": 2,
                "Microsoft.VSTS.Common.AcceptanceCriteria": "<div>Given...</div>",
            },
            "_links": {
                "html": {"href": "https://dev.azure.com/HQY01/V5/_workitems/edit/692945"},
            },
        },
        {
            "id": 692940,
            "rev": 7,
            "fields": {
                "System.Id": 692940,
                "System.Title": "User can log in with MFA",
                "System.State": "Resolved",
                "System.WorkItemType": "User Story",
                "System.Tags": "auth; mfa",
                "System.AssignedTo": {"displayName": "Alice Jones", "uniqueName": "alice.jones@company.com"},
                "System.AreaPath": "V5\\Authentication",
                "System.IterationPath": "V5\\Sprint 13",
                "System.CreatedDate": "2026-01-05T09:00:00.000Z",
                "System.ChangedDate": "2026-02-10T11:00:00.000Z",
                "Microsoft.VSTS.Scheduling.StoryPoints": 8.0,
                "Microsoft.VSTS.Common.Priority": 1,
                "Microsoft.VSTS.Common.AcceptanceCriteria": "<div>Given MFA is enabled...</div>",
            },
            "_links": {
                "html": {"href": "https://dev.azure.com/HQY01/V5/_workitems/edit/692940"},
            },
        },
        {
            "id": 692935,
            "rev": 3,
            "fields": {
                "System.Id": 692935,
                "System.Title": "User can update profile photo",
                "System.State": "New",
                "System.WorkItemType": "User Story",
                "System.Tags": "",
                "System.AssignedTo": None,
                "System.AreaPath": "V5\\Profile",
                "System.IterationPath": "V5\\Sprint 15",
                "System.CreatedDate": "2026-02-01T09:00:00.000Z",
                "System.ChangedDate": "2026-02-01T09:00:00.000Z",
                "Microsoft.VSTS.Scheduling.StoryPoints": None,
                "Microsoft.VSTS.Common.Priority": 3,
                "Microsoft.VSTS.Common.AcceptanceCriteria": None,
            },
            "_links": {
                "html": {"href": "https://dev.azure.com/HQY01/V5/_workitems/edit/692935"},
            },
        },
    ],
}


# ──────────────────────────────────────────────────────────────────────────────
# ADO 404 RESPONSE — returned when item ID does not exist
# ──────────────────────────────────────────────────────────────────────────────

ADO_404_RESPONSE: Dict[str, Any] = {
    "$id": "1",
    "innerException": None,
    "message": "TF401232: Work item 999999 does not exist, or you do not have permissions to read it.",
    "typeName": "Microsoft.TeamFoundation.WorkItemTracking.Server.WorkItemDoesNotExistException",
    "typeKey": "WorkItemDoesNotExistException",
    "errorCode": 600256,
    "eventId": 3200,
}


# ──────────────────────────────────────────────────────────────────────────────
# ADO HEALTH CHECK RESPONSE — GET /_apis/projects?api-version=7.1&$top=1
# ──────────────────────────────────────────────────────────────────────────────

ADO_HEALTH_PROJECTS_RESPONSE: Dict[str, Any] = {
    "count": 1,
    "value": [
        {
            "id": "proj-v5-guid-0001",
            "name": "V5",
            "url": "https://dev.azure.com/HQY01/_apis/projects/proj-v5-guid-0001",
            "state": "wellFormed",
            "revision": 456,
            "visibility": "private",
        }
    ],
}


# ──────────────────────────────────────────────────────────────────────────────
# USER REQUEST STRINGS — realistic inputs from users
# ──────────────────────────────────────────────────────────────────────────────

REQUEST_FULL_URL = (
    "implement https://dev.azure.com/HQY01/V5/_workitems/edit/692945"
)

REQUEST_HASH_ID = (
    "Can you implement the work on #692945 for the password reset feature?"
)

REQUEST_BARE_ID_WITH_HINT = (
    "Let's tackle user story 692945 in Sprint 14"
)

REQUEST_MULTIPLE_IDS = (
    "Review #692945 and #692940 — both are in the Authentication area"
)

REQUEST_NO_ADO_ID = (
    "Refactor the authentication module to reduce cyclomatic complexity"
)

REQUEST_BARE_ID_NO_HINT = (
    "The answer is 692945"  # Should NOT trigger ADO lookup — no context hint
)


# ──────────────────────────────────────────────────────────────────────────────
# EXPECTED MAPPED VALUES — what _map_to_context should produce from 692945
# ──────────────────────────────────────────────────────────────────────────────

EXPECTED_STORY_692945 = {
    "id": "692945",
    "title": "User can reset password via email",
    "state": "Active",
    "type": "User Story",
    "assignee": "Jane Doe",
    "story_points": 5.0,
    "priority": 2,
    "area_path": "V5\\Authentication",
    "iteration_path": "V5\\Sprint 14",
    "parent_id": 689000,
    "child_task_ids": [692946, 692947],
    "linked_test_case_ids": [700100, 700101],
    "linked_pr_ids": ["1337"],
    "url": "https://dev.azure.com/HQY01/V5/_workitems/edit/692945",
    "tags": ["auth", "security", "password-reset"],
    "acceptance_criteria_contains": "Scenario 1: Successful reset request",
}

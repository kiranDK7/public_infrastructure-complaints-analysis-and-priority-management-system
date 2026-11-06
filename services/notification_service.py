"""
Notification Service for Smart CivicCare 2.0.
Dispatches real-time in-app alerts across the 13-stage complaint lifecycle.
"""

from models.database import create_notification, query_db

class NotificationService:
    @staticmethod
    def notify_status_change(complaint_id, ticket_id, citizen_id, new_status, remarks=""):
        status_messages = {
            'SUBMITTED': f"Ticket #{ticket_id} submitted and queued for smart triage.",
            'PENDING': f"Ticket #{ticket_id} is pending municipal review.",
            'UNDER REVIEW': f"Ticket #{ticket_id} is currently under municipal technical inspection.",
            'ASSIGNED': f"Ticket #{ticket_id} has been dispatched to the specialized department.",
            'ACCEPTED': f"The assigned field officer has accepted Ticket #{ticket_id} and scheduled ground action.",
            'WORK IN PROGRESS': f"Ground repair crews have actively commenced maintenance work on #{ticket_id}.",
            'ON HOLD': f"Work on Ticket #{ticket_id} has been temporarily paused. Reason: {remarks or 'Procuring specialized spares'}.",
            'RESOLVED': f"Work on Ticket #{ticket_id} is marked complete. Please verify the completion evidence.",
            'AWAITING CITIZEN VERIFICATION': f"Action completed for #{ticket_id}! Please inspect the completion proof and verify.",
            'COMPLETED': f"Ticket #{ticket_id} has been verified and permanently closed. Thank you for making our city safer!",
            'REOPENED': f"Ticket #{ticket_id} was reopened by the citizen. Escalating to Zonal Department Head.",
            'ESCALATED': f"CRITICAL: Ticket #{ticket_id} exceeded response SLA and has been escalated to Commissioner level.",
            'REJECTED': f"Ticket #{ticket_id} could not be approved. Reason: {remarks or 'Out of municipal jurisdiction'}."
        }

        msg = status_messages.get(new_status, f"Status updated to {new_status} for Ticket #{ticket_id}.")
        title = f"Status: {new_status}"
        create_notification(citizen_id, complaint_id, title, msg, notification_type='status_update')

    @staticmethod
    def notify_officer_assignment(officer_id, complaint_id, ticket_id, title):
        create_notification(
            officer_id,
            complaint_id,
            "New Work Assignment",
            f"You have been assigned Ticket #{ticket_id} ('{title[:35]}...'). Please inspect and accept.",
            notification_type='assignment'
        )

    @staticmethod
    def notify_new_message(target_user_id, complaint_id, ticket_id, sender_name, message_snippet):
        create_notification(
            target_user_id,
            complaint_id,
            f"New Message on #{ticket_id}",
            f"{sender_name}: '{message_snippet[:60]}...'",
            notification_type='message'
        )

notification_service = NotificationService()


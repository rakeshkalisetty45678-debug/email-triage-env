TASKS = {
    "spam_detection": {
        "name": "spam_detection",
        "difficulty": "easy",
        "description": "Identify whether the given email is spam or not spam.",
        "max_steps": 1,
        "emails": [
            {
                "id": "001",
                "subject": "URGENT: You won $1,000,000!",
                "sender": "noreply@suspicious-site.com",
                "body": "Click here immediately to claim your prize...",
                "expected": {
                    "category": "spam",
                    "priority": "low",
                    "action": "delete"
                }
            },
            {
                "id": "002",
                "subject": "Q3 Report Review needed by EOD",
                "sender": "manager@company.com",
                "body": "Please review the attached Q3 report and send feedback.",
                "expected": {
                    "category": "work",
                    "priority": "high",
                    "action": "reply"
                }
            },
            {
                "id": "003",
                "subject": "Your Netflix subscription is expiring!",
                "sender": "billing@netflix-fake.com",
                "body": "Update your payment details immediately or lose access...",
                "expected": {
                    "category": "spam",
                    "priority": "low",
                    "action": "delete"
                }
            }
        ]
    },
    "email_categorization": {
        "name": "email_categorization",
        "difficulty": "medium",
        "description": "Categorize and prioritize the given email correctly.",
        "max_steps": 2,
        "emails": [
            {
                "id": "004",
                "subject": "Team lunch this Friday!",
                "sender": "colleague@company.com",
                "body": "Hey! We are planning a team lunch this Friday at 1pm.",
                "expected": {
                    "category": "personal",
                    "priority": "low",
                    "action": "read"
                }
            },
            {
                "id": "005",
                "subject": "CRITICAL: Server down in production!",
                "sender": "devops@company.com",
                "body": "Production server is down. Immediate action required!",
                "expected": {
                    "category": "urgent",
                    "priority": "high",
                    "action": "reply"
                }
            },
            {
                "id": "006",
                "subject": "Monthly Newsletter - April 2026",
                "sender": "newsletter@techdigest.com",
                "body": "This months top stories in tech...",
                "expected": {
                    "category": "newsletter",
                    "priority": "low",
                    "action": "archive"
                }
            }
        ]
    },
    "inbox_triage": {
        "name": "inbox_triage",
        "difficulty": "hard",
        "description": "Triage a full inbox of 5 emails — categorize, prioritize, and action each one correctly.",
        "max_steps": 5,
        "emails": [
            {
                "id": "007",
                "subject": "Invoice #4521 Payment Due",
                "sender": "accounts@vendor.com",
                "body": "Your invoice of $5000 is due by April 10th.",
                "expected": {
                    "category": "work",
                    "priority": "high",
                    "action": "reply"
                }
            },
            {
                "id": "008",
                "subject": "Congratulations! You are selected!",
                "sender": "winner@lottery-fake.com",
                "body": "You have been selected for a $500 gift card. Click now!",
                "expected": {
                    "category": "spam",
                    "priority": "low",
                    "action": "delete"
                }
            },
            {
                "id": "009",
                "subject": "Project deadline moved to Monday",
                "sender": "pm@company.com",
                "body": "Hi team, the project deadline has been moved to this Monday.",
                "expected": {
                    "category": "urgent",
                    "priority": "high",
                    "action": "reply"
                }
            },
            {
                "id": "010",
                "subject": "Weekend BBQ at my place!",
                "sender": "friend@gmail.com",
                "body": "Hey! Having a BBQ this weekend, you are invited!",
                "expected": {
                    "category": "personal",
                    "priority": "low",
                    "action": "reply"
                }
            },
            {
                "id": "011",
                "subject": "Your AWS bill is ready",
                "sender": "billing@aws.amazon.com",
                "body": "Your AWS bill for March 2026 is ready to view.",
                "expected": {
                    "category": "work",
                    "priority": "medium",
                    "action": "read"
                }
            }
        ]
    }
}
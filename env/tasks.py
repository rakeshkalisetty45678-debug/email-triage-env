SCENARIOS = {
    "board_crunch": {
        "title": "Board Crunch With Family Constraint",
        "objective": (
            "Protect the CEO's board-prep time while resolving an investor request, "
            "a security escalation, and a family commitment with minimal relationship damage."
        ),
        "stakeholder_hints": [
            {
                "name": "Asha Menon",
                "role": "CEO",
                "preference_hint": "Protects commitments made to family unless a company-level crisis is explicit.",
            },
            {
                "name": "Nikhil Rao",
                "role": "Chief of Staff",
                "preference_hint": "Can absorb finance prep and vendor follow-ups, but not security incidents.",
            },
            {
                "name": "Mira Shah",
                "role": "Security Lead",
                "preference_hint": "Needs immediate escalation with crisp decisions, not vague reassurance.",
            },
        ],
        "calendar_slots": [
            {"slot_id": "thu_0900", "label": "Thu 09:00-09:30", "duration_minutes": 30},
            {"slot_id": "thu_1700", "label": "Thu 17:00-17:30", "duration_minutes": 30},
            {"slot_id": "fri_1830", "label": "Fri 18:30-19:00", "duration_minutes": 30},
        ],
        "delegates": [
            {
                "name": "Nikhil Rao",
                "role": "Chief of Staff",
                "specialties": ["finance", "operations", "vendor"],
                "capacity": 2,
                "trust_level": "high",
            },
            {
                "name": "Mira Shah",
                "role": "Security Lead",
                "specialties": ["security", "incident response"],
                "capacity": 1,
                "trust_level": "high",
            },
        ],
        "threads": [
            {
                "thread_id": "t1",
                "sender": "Jordan Lee",
                "sender_role": "Lead Investor",
                "subject": "Can we do Friday 6:30 pm?",
                "body": (
                    "I can only speak Friday 6:30 pm before my flight. "
                    "Need confidence on the board narrative."
                ),
                "visible_constraints": [
                    "Investor has one available slot: Friday 6:30 pm.",
                    "CEO promised family dinner Friday evening.",
                ],
                "social_risk": "high",
                "asks": ["Schedule a short meeting or propose a principled alternative."],
                "expected": {
                    "decision": "decline",
                    "acceptable_decisions": ["decline", "clarify"],
                    "priority": "high",
                    "keywords": ["board", "family", "alternative"],
                    "forbidden_slot": "fri_1830",
                },
            },
            {
                "thread_id": "t2",
                "sender": "mira@company.com",
                "sender_role": "Security Lead",
                "subject": "Unknown device login on production admin",
                "body": (
                    "We detected a privileged login from an unrecognized device. "
                    "Need approval to lock admin sessions and start incident comms."
                ),
                "visible_constraints": [
                    "Potential production security incident.",
                    "Fast approval is more valuable than polished phrasing.",
                ],
                "social_risk": "critical",
                "asks": ["Approve a response owner and send a crisp escalation note."],
                "expected": {
                    "decision": "delegate",
                    "acceptable_decisions": ["delegate", "reply"],
                    "priority": "critical",
                    "target_person": "Mira Shah",
                    "keywords": ["lock", "incident", "approve"],
                },
            },
            {
                "thread_id": "t3",
                "sender": "finance@company.com",
                "sender_role": "Finance Ops",
                "subject": "Board packet appendix still incomplete",
                "body": (
                    "We need one executive decision on vendor spend ranges before "
                    "the appendix can go out."
                ),
                "visible_constraints": [
                    "Can be delegated to a trusted operator.",
                    "Must be resolved before Thursday evening.",
                ],
                "social_risk": "medium",
                "asks": ["Delegate prep work or draft a decision request."],
                "expected": {
                    "decision": "delegate",
                    "acceptable_decisions": ["delegate", "reply"],
                    "priority": "high",
                    "target_person": "Nikhil Rao",
                    "keywords": ["vendor", "board", "appendix"],
                },
            },
            {
                "thread_id": "t4",
                "sender": "partner@home.com",
                "sender_role": "Family",
                "subject": "Still on for Friday dinner?",
                "body": (
                    "Just checking that Friday dinner is still protected. "
                    "It has been a rough week for the kids."
                ),
                "visible_constraints": [
                    "Relationship repair matters if earlier business pressure grew.",
                    "A respectful confirmation helps close the loop.",
                ],
                "social_risk": "high",
                "asks": ["Send a clear response that protects the commitment."],
                "expected": {
                    "decision": "reply",
                    "acceptable_decisions": ["reply"],
                    "priority": "high",
                    "keywords": ["dinner", "protected", "family"],
                },
            },
        ],
    },
    "launch_week": {
        "title": "Launch Week Coalition Management",
        "objective": (
            "Coordinate product, legal, and sales leaders during launch week without "
            "double-booking the executive or burning partner trust."
        ),
        "stakeholder_hints": [
            {
                "name": "Ritu Kapoor",
                "role": "VP Product",
                "preference_hint": "Values rapid decisions and hates unresolved blockers lingering overnight.",
            },
            {
                "name": "Dev Malhotra",
                "role": "Head of Legal",
                "preference_hint": "Prefers async review unless there is external press exposure.",
            },
            {
                "name": "Samir Dutt",
                "role": "Sales Director",
                "preference_hint": "Will push for meetings, but prep can often be delegated.",
            },
        ],
        "calendar_slots": [
            {"slot_id": "mon_1000", "label": "Mon 10:00-10:30", "duration_minutes": 30},
            {"slot_id": "mon_1630", "label": "Mon 16:30-17:00", "duration_minutes": 30},
            {"slot_id": "tue_1130", "label": "Tue 11:30-12:00", "duration_minutes": 30},
        ],
        "delegates": [
            {
                "name": "Ritu Kapoor",
                "role": "VP Product",
                "specialties": ["launch", "product", "roadmap"],
                "capacity": 1,
                "trust_level": "high",
            },
            {
                "name": "Aman Verma",
                "role": "Executive Assistant",
                "specialties": ["logistics", "follow-up", "customer scheduling"],
                "capacity": 2,
                "trust_level": "high",
            },
        ],
        "threads": [
            {
                "thread_id": "l1",
                "sender": "sales@bigco.com",
                "sender_role": "Enterprise Buyer",
                "subject": "Need pricing commitment before pilot",
                "body": (
                    "Procurement wants a pricing answer before Tuesday noon or the pilot slips."
                ),
                "visible_constraints": [
                    "Needs a response before Tuesday noon.",
                    "The executive does not need to attend the logistics call personally.",
                ],
                "social_risk": "high",
                "asks": ["Decide whether to delegate follow-up or schedule a meeting."],
                "expected": {
                    "decision": "delegate",
                    "acceptable_decisions": ["delegate", "reply"],
                    "priority": "high",
                    "target_person": "Aman Verma",
                    "keywords": ["pricing", "pilot", "timeline"],
                },
            },
            {
                "thread_id": "l2",
                "sender": "legal@company.com",
                "sender_role": "Head of Legal",
                "subject": "Press quote review",
                "body": (
                    "I can review the quote async tonight. A meeting is only needed if "
                    "we are changing the claim language."
                ),
                "visible_constraints": [
                    "Async review is usually better than forcing a meeting.",
                    "Meeting slot scarcity matters later in the scenario.",
                ],
                "social_risk": "medium",
                "asks": ["Pick async handling unless a meeting is justified."],
                "expected": {
                    "decision": "reply",
                    "acceptable_decisions": ["reply", "delegate"],
                    "priority": "medium",
                    "keywords": ["async", "quote", "review"],
                },
            },
            {
                "thread_id": "l3",
                "sender": "product@company.com",
                "sender_role": "VP Product",
                "subject": "Launch blocker triage",
                "body": (
                    "Two launch blockers need executive arbitration. "
                    "I can do Monday 4:30 pm or Tuesday 11:30 am."
                ),
                "visible_constraints": [
                    "This is the one thread that benefits from live arbitration.",
                    "Tuesday 11:30 keeps Monday free for async review.",
                ],
                "social_risk": "critical",
                "asks": ["Schedule the best slot for blocker resolution."],
                "expected": {
                    "decision": "schedule",
                    "acceptable_decisions": ["schedule"],
                    "priority": "critical",
                    "chosen_slot": "tue_1130",
                    "keywords": ["blocker", "decision", "launch"],
                },
            },
            {
                "thread_id": "l4",
                "sender": "cofounder@company.com",
                "sender_role": "Co-founder",
                "subject": "Keep Monday 10 free for recruiting candidate",
                "body": "Important relationship call. Please avoid burning Monday 10 am.",
                "visible_constraints": [
                    "Monday 10 am should stay free unless there is no acceptable alternative.",
                ],
                "social_risk": "high",
                "asks": ["Acknowledge and protect the slot."],
                "expected": {
                    "decision": "reply",
                    "acceptable_decisions": ["reply"],
                    "priority": "high",
                    "keywords": ["protected", "candidate", "Monday"],
                },
            },
        ],
    },
}


"""
Built-in JSON schemas for common document types.
Pass these into LLMStructurer.structure() as the schema argument.
"""

INVOICE_SCHEMA = {
    "type": "object",
    "properties": {
        "invoice_number": {"type": "string"},
        "vendor_name": {"type": "string"},
        "vendor_address": {"type": "string"},
        "client_name": {"type": "string"},
        "invoice_date": {"type": "string"},
        "due_date": {"type": "string"},
        "line_items": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "description": {"type": "string"},
                    "quantity": {"type": "number"},
                    "unit_price": {"type": "number"},
                    "total": {"type": "number"},
                },
            },
        },
        "subtotal": {"type": "number"},
        "tax": {"type": "number"},
        "total_amount": {"type": "number"},
        "currency": {"type": "string"},
        "payment_terms": {"type": "string"},
    },
}

CONTRACT_SCHEMA = {
    "type": "object",
    "properties": {
        "contract_title": {"type": "string"},
        "parties": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "name": {"type": "string"},
                    "role": {"type": "string"},
                    "address": {"type": "string"},
                },
            },
        },
        "effective_date": {"type": "string"},
        "expiry_date": {"type": "string"},
        "governing_law": {"type": "string"},
        "key_obligations": {"type": "array", "items": {"type": "string"}},
        "payment_terms": {"type": "string"},
        "termination_clauses": {"type": "array", "items": {"type": "string"}},
        "confidentiality": {"type": "boolean"},
        "total_value": {"type": "number"},
    },
}

RFP_SCHEMA = {
    "type": "object",
    "properties": {
        "rfp_title": {"type": "string"},
        "issuing_organization": {"type": "string"},
        "rfp_number": {"type": "string"},
        "submission_deadline": {"type": "string"},
        "contact_person": {"type": "string"},
        "contact_email": {"type": "string"},
        "project_summary": {"type": "string"},
        "requirements": {"type": "array", "items": {"type": "string"}},
        "evaluation_criteria": {"type": "array", "items": {"type": "string"}},
        "budget_range": {"type": "string"},
        "timeline": {"type": "string"},
        "deliverables": {"type": "array", "items": {"type": "string"}},
    },
}

RESUME_SCHEMA = {
    "type": "object",
    "properties": {
        "full_name": {"type": "string"},
        "email": {"type": "string"},
        "phone": {"type": "string"},
        "location": {"type": "string"},
        "summary": {"type": "string"},
        "skills": {"type": "array", "items": {"type": "string"}},
        "experience": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "company": {"type": "string"},
                    "role": {"type": "string"},
                    "start_date": {"type": "string"},
                    "end_date": {"type": "string"},
                    "responsibilities": {"type": "array", "items": {"type": "string"}},
                },
            },
        },
        "education": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "institution": {"type": "string"},
                    "degree": {"type": "string"},
                    "year": {"type": "string"},
                },
            },
        },
        "certifications": {"type": "array", "items": {"type": "string"}},
    },
}

SCHEMAS = {
    "invoice": INVOICE_SCHEMA,
    "contract": CONTRACT_SCHEMA,
    "rfp": RFP_SCHEMA,
    "resume": RESUME_SCHEMA,
}

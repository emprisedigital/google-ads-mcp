import logging
import os
from pathlib import Path
from typing import Any, Dict, List
from google.protobuf.json_format import MessageToDict


def exemptible_policy_keys_by_operation(failure: Any) -> Dict[int, List[Any]]:
    """Map operation index -> list of exemptible PolicyViolationKeys from a GoogleAdsFailure.

    Lets a mutate be retried with operation.exempt_policy_violation_keys so
    policy-exemptible content (e.g. PRC abortion / pregnancy-test keywords and ads)
    can be created via the API instead of erroring out.
    """
    keys_by_op: Dict[int, List[Any]] = {}
    for error in failure.errors:
        pvd = error.details.policy_violation_details
        if not (pvd.key.policy_name or pvd.key.violating_text):
            continue
        if not pvd.is_exemptible:
            continue
        op_index = 0
        for fpe in error.location.field_path_elements:
            if fpe.field_name == "operations":
                op_index = fpe.index
        keys_by_op.setdefault(op_index, []).append(pvd.key)
    return keys_by_op


def get_logger(name: str) -> logging.Logger:
    logger = logging.getLogger(name)
    if not logger.hasHandlers():
        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
    logger.setLevel(logging.INFO)
    return logger


def load_dotenv(dotenv_path: str = ".env") -> None:
    if not Path(dotenv_path).exists():
        raise FileNotFoundError(f"Dotenv file not found: {dotenv_path}")

    with Path(dotenv_path).open() as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if "=" not in line:
                continue
            key, value = line.split("=", 1)
            key = key.strip()
            value = value.strip().strip('"').strip("'")
            os.environ.setdefault(key, value)


def format_customer_id(customer_id: str) -> str:
    """Format a customer ID by removing hyphens.

    Google Ads customer IDs can be provided with or without hyphens.
    This function ensures they are in the format expected by the API (without hyphens).

    Args:
        customer_id: The customer ID with or without hyphens (e.g., "123-456-7890" or "1234567890")

    Returns:
        The customer ID without hyphens (e.g., "1234567890")
    """
    return customer_id.replace("-", "")


def serialize_proto_message(
    message: Any, use_integers_for_enums: bool = False
) -> Dict[str, Any]:
    """Serialize a proto-plus message to a dictionary.

    Args:
        message: A proto-plus message object
        use_integers_for_enums: If True, return enum values as integers instead of strings

    Returns:
        A dictionary representation of the message
    """
    try:
        # For proto-plus messages, we need to convert to the underlying protobuf message
        if hasattr(message, "_pb"):
            # This is a proto-plus message
            return MessageToDict(
                message._pb,
                preserving_proto_field_name=True,
                use_integers_for_enums=use_integers_for_enums,
            )
        else:
            # This is a regular protobuf message
            return MessageToDict(
                message,
                preserving_proto_field_name=True,
                use_integers_for_enums=use_integers_for_enums,
            )
    except Exception as e:
        # Fallback to manual conversion if MessageToDict fails
        logger = get_logger(__name__)
        logger.warning(f"Failed to serialize message with MessageToDict: {e}")

        # Try to convert manually
        result = {}
        if hasattr(message, "__dict__"):
            for key, value in message.__dict__.items():
                if not key.startswith("_"):
                    result[key] = str(value) if value is not None else None
        return result

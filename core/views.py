from rest_framework.decorators import api_view
from drf_yasg.utils import swagger_auto_schema
from django.http import JsonResponse
from .utils import *
from .serializers import *

@api_view(['GET'])
def mcp_manifest(request):
    return JsonResponse({
        "tools": [
            {
                "type": "function",
                "function": {
                    "name": "check_token",
                    "description": "Scan an EVM token contract for scam indicators.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "address": {"type": "string"},
                            "chain_id": {"type": "integer", "description": "EVM chain ID"}
                        },
                        "required": ["address", "chain_id"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "check_wallet",
                    "description": "Check if a wallet address is blacklisted or malicious.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "address": {"type": "string"},
                            "chain_id": {"type": "integer"}
                        },
                        "required": ["address", "chain_id"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "check_nft",
                    "description": "Analyze an NFT contract/token ID for authenticity and risk.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "contract": {"type": "string"},
                            "token_id": {"type": "string"},
                            "chain_id": {"type": "integer"}
                        },
                        "required": ["contract", "token_id", "chain_id"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "check_url",
                    "description": "Check if a URL or dApp is flagged as phishing.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "url": {"type": "string"}
                        },
                        "required": ["url"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "simulate_sol_tx",
                    "description": "Simulate a Solana transaction to detect hidden risks.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "tx_base64": {"type": "string", "description": "Base64-encoded Solana transaction"}
                        },
                        "required": ["tx_base64"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "check_sol_token",
                    "description": "Analyze a Solana SPL token for scam indicators.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "address": {"type": "string"}
                        },
                        "required": ["address"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "verify_donation",
                    "description": "Check if a transaction hash represents a donation to a verified address.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "tx_hash": {"type": "string"},
                            "chain_id": {"type": "integer"},
                            "chain": {
                                "type": "string",
                                "enum": ["evm", "solana"],
                                "default": "evm"
                            }
                        },
                        "required": ["tx_hash"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "list_verified_causes",
                    "description": "List currently known verified donation recipients.",
                    "parameters": {
                        "type": "object",
                        "properties": {}
                    }
                }
            }
        ]
    })


@swagger_auto_schema(method='post', request_body=CheckTokenSerializer)
@api_view(['POST'])
def check_token(request):
    serializer = CheckTokenSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    data = fetch_goplus(
        f"/api/v1/token_security/{serializer.validated_data['chain_id']}",
        params={"contract_addresses": serializer.validated_data['address']}
    )
    if isinstance(data, dict) and data.get("error"):
        return error_response(data.get("message"), data.get("code"), data.get("raw"))
    return success_response({
        "address": serializer.validated_data['address'],
        "scam_risk": data.get("is_honeypot", "0"),
        "raw": data
    })


@swagger_auto_schema(method='post', request_body=CheckWalletSerializer)
@api_view(['POST'])
def check_wallet(request):
    serializer = CheckWalletSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    data = fetch_goplus(
        f"/api/v1/address_security/{serializer.validated_data['chain_id']}",
        params={"address": serializer.validated_data['address']}
    )
    if isinstance(data, dict) and data.get("error"):
        return error_response(data.get("message"), data.get("code"), data.get("raw"))
    return success_response({
        "malicious_label": data.get("malicious_label"),
        "security_level": data.get("security_level"),
        "raw": data
    })


@swagger_auto_schema(method='post', request_body=CheckNFTSerializer)
@api_view(['POST'])
def check_nft(request):
    serializer = CheckNFTSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    data = fetch_goplus(
        f"/api/v1/nft_security/{serializer.validated_data['chain_id']}",
        params={
            "contract_address": serializer.validated_data['contract'],
            "token_id": serializer.validated_data['token_id']
        }
    )
    if isinstance(data, dict) and data.get("error"):
        return error_response(data.get("message"), data.get("code"), data.get("raw"))
    return success_response({
        "authenticity_risk": data.get("security_risk"),
        "raw": data
    })


@swagger_auto_schema(method='post', request_body=CheckURLSerializer)
@api_view(['POST'])
def check_url(request):
    serializer = CheckURLSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    url = serializer.validated_data['url']

    # Primary check via GoPlus
    data = fetch_goplus("/api/v1/phishing_site/", params={"url": url})
    if isinstance(data, dict) and data.get("error"):
        return error_response(data.get("message"), data.get("code"), data.get("raw"))

    # If GoPlus returns no "phishing", it will fallback to Google + feeds
    if not data.get("phishing"):
        # This will try Google Safe Browsing
        google_result = fetch_google_safe_browsing(url)
        if google_result.get("phishing") == 1:
            return success_response({
                "is_phishing": 1,
                "raw": google_result
            })

        # This will try 3rd-party feeds
        feed_result = check_against_feeds(url)
        if feed_result.get("phishing") == 1:
            return success_response({
                "is_phishing": 1,
                "raw": feed_result
            })

    return success_response({
        "is_phishing": data.get("phishing", 0),
        "raw": data
    })


@swagger_auto_schema(method='post', request_body=SimulateSolTxSerializer)
@api_view(['POST'])
def simulate_sol_tx(request):
    serializer = SimulateSolTxSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    data = fetch_goplus("/api/v1/solana_transaction_simulate", method="POST", body={"transaction": serializer.validated_data['tx_base64']})
    if isinstance(data, dict) and data.get("error"):
        return error_response(data.get("message"), data.get("code"), data.get("raw"))
    return success_response({
        "simulated": True,
        "risk_detected": data.get("risk_level", "low"),
        "raw": data
    })


@swagger_auto_schema(method='post', request_body=CheckSolTokenSerializer)
@api_view(['POST'])
def check_sol_token(request):
    serializer = CheckSolTokenSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    data = fetch_goplus("/api/v1/token_security/101", params={"contract_address": serializer.validated_data['address']})
    if isinstance(data, dict) and data.get("error"):
        return error_response(data.get("message"), data.get("code"), data.get("raw"))
    return success_response({
        "scam_risk": data.get("is_honeypot", "0"),
        "raw": data
    })


@swagger_auto_schema(method='post', request_body=VerifyDonationSerializer)
@api_view(['POST'])
def verify_donation(request):
    serializer = VerifyDonationSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    result = get_verified_causes()
    causes = result["verified_causes"]
    tx_hash = serializer.validated_data.get("tx_hash")
    chain_id = serializer.validated_data.get("chain_id")
    chain = serializer.validated_data.get("chain", "evm")

    if not causes and result["failed_sources"]:
        return error_response("All cause sources failed", raw=result["failed_sources"], status=503)

    if chain == "solana":
        tx = fetch_solana_tx(tx_hash)
        to_addresses = [
            ix.get("parsed", {}).get("info", {}).get("destination")
            for ix in tx.get("transaction", {}).get("message", {}).get("instructions", [])
            if ix.get("parsed", {}).get("info", {}).get("destination")
        ]
        match = next((c for c in causes if c['chain'] == "solana" and c['address'] in to_addresses), None)
        return success_response({
            "chain": "solana",
            "tx_hash": tx_hash,
            "to": to_addresses,
            "verified": bool(match),
            "cause": match.get("name") if match else None
        })

    tx = fetch_covalent_tx(tx_hash, chain_id)
    if tx.get("error"):
        return error_response(tx.get("message", "Unable to retrieve transaction."), raw=tx)
    to_address = tx.get("to_address", "").lower()
    match = next((c for c in causes if c['chain'] == "evm" and c.get("chain_id") == chain_id and c['address'].lower() == to_address), None)
    return success_response({
        "chain_id": chain_id,
        "tx_hash": tx_hash,
        "to": to_address,
        "verified": bool(match),
        "cause": match.get("name") if match else None
    })


@api_view(['GET'])
def list_verified_causes(request):
    result = get_verified_causes()
    return success_response({
        "causes": result["verified_causes"],
        "failed_sources": result["failed_sources"]
    })

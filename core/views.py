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

    token_info = list(data.values())[0] if isinstance(data, dict) and len(data) else {}

    return success_response({
        "address": serializer.validated_data['address'],
        "scam_risk": token_info.get("is_honeypot", "0"),
        "blacklisted": token_info.get("is_blacklisted", "0"),
        "creator_address": token_info.get("creator_address"),
        "buy_tax": token_info.get("buy_tax"),
        "sell_tax": token_info.get("sell_tax"),
        "holder_count": token_info.get("holder_count"),
        "top_holders": token_info.get("holders", [])[:3],  # Optional: limit to 3
        "warning_flags": {
            "honeypot_with_same_creator": token_info.get("honeypot_with_same_creator"),
            "slippage_modifiable": token_info.get("slippage_modifiable"),
            "transfer_pausable": token_info.get("transfer_pausable"),
            "is_mintable": token_info.get("is_mintable"),
            "owner_address": token_info.get("owner_address")
        }
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
        "malicious_label": data.get("malicious_label", "unknown"),
        "security_level": data.get("security_level", "unknown"),
        "note": "If malicious_label is not null, this wallet may be suspicious."
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
        "security_risk": data.get("security_risk", "unknown"),
        "verified_contract": data.get("contract_address"),
        "note": "This NFT was analyzed for known risks. Review before minting or buying."
    })


@swagger_auto_schema(method='post', request_body=CheckURLSerializer)
@api_view(['POST'])
def check_url(request):
    serializer = CheckURLSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    url = serializer.validated_data['url']

    # Step 1: This will try GoPlus first
    goplus_result = fetch_goplus("/api/v1/phishing_site/", params={"url": url})

    if isinstance(goplus_result, dict) and goplus_result.get("error"):
        return success_response({
            "is_phishing": False,
            "source": "goplus-failure",
            "note": "GoPlus failed to scan the URL. Please retry later or use an alternate service."
        })

    # If GoPlus says phishing = 1 that means its flagged
    if goplus_result.get("phishing") == 1:
        return success_response({
            "is_phishing": True,
            "source": "goplus",
            "note": "Flagged by GoPlus security engine."
        })

    # Step 2: This will fall back to this and try Google Safe Browsing even goplus cannot detect it
    google_result = fetch_google_safe_browsing(url)
    if google_result.get("phishing") == 1:
        return success_response({
            "is_phishing": True,
            "source": "google",
            "note": "Flagged as phishing by Google Safe Browsing"
        })

    if google_result.get("error"):
        return success_response({
            "is_phishing": False,
            "source": "google-fallback-failed",
            "note": "Google Safe Browsing scan failed. Scan may be incomplete."
        })

    # Step 3: Fall back to Community Feeds if both above could not locate it
    feed_result = check_against_feeds(url)
    if feed_result.get("phishing") == 1:
        return success_response({
            "is_phishing": True,
            "source": feed_result.get("source", "community-feeds"),
            "note": "Flagged by phishing feed data (OpenPhish, URLhaus, or PhishTank)."
        })

    # If none of the above worked, return clean website note to user
    return success_response({
        "is_phishing": False,
        "source": "none-detected",
        "note": "No phishing flags from GoPlus, Google, or feeds."
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
        "risk_level": data.get("risk_level", "low"),
        "note": "This transaction was simulated to detect hidden behavior."
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
        "mintable": data.get("is_mintable", "0"),
        "transfer_pausable": data.get("transfer_pausable", "0"),
        "owner_address": data.get("owner_address", "unknown"),
        "note": "This SPL token was scanned for honeypot and control flags."
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
        return error_response("All cause sources failed", raw=result["failed_sources"]) 

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

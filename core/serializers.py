from rest_framework import serializers

class CheckTokenSerializer(serializers.Serializer):
    address = serializers.CharField()
    chain_id = serializers.IntegerField()

class CheckWalletSerializer(serializers.Serializer):
    address = serializers.CharField()
    chain_id = serializers.IntegerField()

class CheckNFTSerializer(serializers.Serializer):
    contract = serializers.CharField()
    token_id = serializers.CharField()
    chain_id = serializers.IntegerField()

class CheckURLSerializer(serializers.Serializer):
    url = serializers.URLField()

class SimulateSolTxSerializer(serializers.Serializer):
    tx_base64 = serializers.CharField()

class CheckSolTokenSerializer(serializers.Serializer):
    address = serializers.CharField()

class VerifyDonationSerializer(serializers.Serializer):
    tx_hash = serializers.CharField()
    chain_id = serializers.IntegerField(required=False)
    chain = serializers.ChoiceField(choices=["evm", "solana"], default="evm", required=False)

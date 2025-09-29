# routes/payments.py
import os
from fastapi import APIRouter, Body, Depends, HTTPException
from models.payment import PaymentSchema
from .auth import get_current_user
import mercadopago

sdk = mercadopago.SDK(os.getenv("MERCADOPAGO_ACCESS_TOKEN"))
router = APIRouter()

@router.post("/create-pix", tags=["Pagamentos"])
async def create_pix_payment(
    payment_details: PaymentSchema = Body(...),
    current_user: dict = Depends(get_current_user)
):
    """
    Cria uma cobrança PIX usando a Chave Privada (Access Token) no backend.
    """
    user_name = current_user.get("name", "Comprador")
    user_email = current_user.get("email")

    try:
        payment_data = {
            "transaction_amount": payment_details.amount,
            "description": payment_details.description,
            "payment_method_id": "pix",
            "payer": { "email": user_email, "first_name": user_name.split(' ')[0] },
            "notification_url": "https://vertexplay.com.br/webhook",
        }

        payment_response = sdk.payment().create({"body": payment_data})
        payment = payment_response.get("response")

        if payment_response.get("status") in [200, 201]:
            qr_code_data = payment.get("point_of_interaction", {}).get("transaction_data", {})
            return {
                "status": "pagamento_iniciado",
                "payment_id": payment.get("id"),
                "qr_code": qr_code_data.get("qr_code"),
                "qr_code_base64": qr_code_data.get("qr_code_base64"),
            }
        else:
            # Esta linha irá imprimir o erro exato retornado pelo Mercado Pago no seu console
            print("Erro retornado pelo Mercado Pago:", payment)
            raise HTTPException(
                status_code=payment_response.get("status", 400),
                detail=payment.get("message", "Erro ao criar pagamento com o Mercado Pago")
            )

    except Exception as e:
        # Esta linha irá imprimir qualquer outro erro inesperado no seu console
        print(f"Erro inesperado na criação do pagamento: {e}")
        raise HTTPException(status_code=500, detail="Ocorreu um erro interno ao processar o pagamento.")
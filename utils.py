import base64

def change_receipt_for_binary(receipt_path):
    with open(receipt_path, "rb") as f:
        receipt_data = base64.b64encode(f.read()).decode('utf-8')

    return f"data:image/jpg;base64,{receipt_data}"
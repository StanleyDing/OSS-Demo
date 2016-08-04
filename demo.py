import requests

from flask import Flask, request, render_template

from gcoin import *


app = Flask(__name__)

BASE_URL = 'http://store1.diqi.us:9876'


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/address', methods=['POST'])
def address():
    message = request.form.get('message')
    print message

    # create private key, public key, and address
    priv = sha256(str(message))
    pub = privtopub(priv)
    addr = pubtoaddr(pub)
    address_response = {
        'priv': priv,
        'pub': pub,
        'addr': addr
    }
    return render_template('new_address.html', **address_response)

@app.route('/balance', methods=['GET'])
def balance():
    address = request.args.get('address')

    # get address balance
    url = BASE_URL + '/base/v1/balance/%s' % address
    response = requests.get(url)
    balance_dict = response.json()
    return render_template('balance.html', data=balance_dict)

@app.route('/license', methods=['POST'])
def license():
    address = request.form.get('address')
    color_id = request.form.get('color_id')
    name = request.form.get('name')
    description = request.form.get('description')
    metadata_link = request.form.get('metadata_link')

    # create license
    payload = {
        'address': address,
        'color_id': color_id,
        'name': name,
        'description': description,
        'metadata_link': metadata_link,
        'member_control': 'False'
    }
    url = BASE_URL + '/base/v1/license/create'
    response = requests.get(url, params=payload)
    return response.json()['tx_id']

@app.route('/mint', methods=['POST'])
def mint():
    mint_address = request.form.get('mint_address')
    color_id = request.form.get('color_id')
    amount = request.form.get('amount')
    priv = request.form.get('priv')

    # create mint tx
    payload = {
        'mint_address': mint_address,
        'color_id': color_id,
        'amount': amount
    }
    url = BASE_URL + '/base/v1/mint/create'
    response = requests.get(url, params=payload)

    # sign
    raw_tx = str(response.json()['raw_tx'])
    signed_tx = signall(raw_tx, priv)

    # broadcast
    url = BASE_URL + '/base/v1/mint/send'
    response = requests.post(url, data={'raw_tx': signed_tx})
    return response.json()['tx_id']

@app.route('/send', methods=['POST'])
def send():
    from_address = request.form.get('from_address')
    to_address = request.form.get('to_address')
    color_id = request.form.get('color_id')
    amount = request.form.get('amount')
    priv = request.form.get('priv')

    # create raw tx
    payload = {
        'from_address': from_address,
        'to_address': to_address,
        'color_id': color_id,
        'amount': amount
    }
    url = BASE_URL + '/base/v1/transaction/create'
    response = requests.get(url, params=payload)

    # sign
    raw_tx = str(response.json()['raw_tx'])
    signed_tx = signall(raw_tx, priv)

    # broadcast
    url = BASE_URL + '/base/v1/transaction/send'
    response = requests.post(url, data={'raw_tx': signed_tx})
    return response.json()['tx_id']

if __name__ == '__main__':
    app.run(debug=True)

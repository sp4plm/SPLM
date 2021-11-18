# -*- coding: utf-8 -*-

from app import app

# app.run(debug=True, port=5001)
app.run(host="splm.herokuapp.com", port=80, debug=False)
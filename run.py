# -*- coding: utf-8 -*-

from app import app

# app.run(debug=True, port=5001)
app.run(host="0.0.0.0", port=8080, debug=True)
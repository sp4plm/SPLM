# -*- coding: utf-8 -*-
import os
from app import app

# app.run(debug=True, port=5001)

port = int(os.environ.get('PORT', 33507))
app.run(host="0.0.0.0", port=port, debug=True)
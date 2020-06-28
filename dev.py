from royaltyapp import create_app

import os

app = create_app()

"""Conditional to run the application."""
if __name__ == '__main__':
    app.run(debug=True)



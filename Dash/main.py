from dash import Dash, html

app = Dash()

app.layout = html.Div(
    children=[
        html.H1(children='Hello Dash'),
        html.Div(
            children='Dash: A web application framework for Python.',
        ),
    ]
)

application = app.server

if __name__ == '__main__':
    application.run(host='0.0.0.0', port=9000, debug=True)

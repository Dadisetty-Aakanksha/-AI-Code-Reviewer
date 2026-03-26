
import reflex as rx

config = rx.Config(
    app_name = "ai_code_reviewer",
    plugins=[
        rx.plugins.SitemapPlugin(),
        rx.plugins.TailwindV4Plugin(),
    ]
)
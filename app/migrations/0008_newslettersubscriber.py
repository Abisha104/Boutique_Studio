from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("app", "0007_alter_stockitem_options_remove_stockitem_category_and_more"),
    ]

    operations = [
        migrations.CreateModel(
            name="NewsletterSubscriber",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("email", models.EmailField(max_length=254, unique=True)),
                ("is_active", models.BooleanField(default=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
            ],
            options={
                "verbose_name": "Newsletter Subscriber",
                "verbose_name_plural": "Newsletter Subscribers",
                "ordering": ["-created_at"],
            },
        ),
    ]

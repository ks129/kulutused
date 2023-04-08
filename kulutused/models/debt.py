from django.contrib.auth.models import User
from django.db.models import CASCADE, CharField, ForeignKey, Model, PositiveIntegerField


class Debt(Model):
    """Contains all data about how much does one user owe to another."""

    payer = ForeignKey(User, on_delete=CASCADE, related_name='payer')
    to_who = ForeignKey(User, on_delete=CASCADE, related_name='to_who')
    amount = PositiveIntegerField(help_text='Tagasimakse puhul uuenda seda välja.')
    comments = CharField(max_length=250)

    def save(self, *args, **kwargs) -> None:
        """Delete debt entry in case amount = 0."""
        super(Debt, self).save(*args, **kwargs)

        if self.amount == 0:
            # Delete this entry to keep table smaller
            self.delete()

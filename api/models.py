from django.db import models


class ExpansionSet(models.Model):
    name = models.CharField(max_length=100)
    release_date = models.DateField(null=True, blank=True)
    total_cards = models.IntegerField(default=0)

    def __str__(self):
        return self.name


class Card(models.Model):
    RARITY_CHOICES = [
        ('Common', 'Common'),
        ('Uncommon', 'Uncommon'),
        ('Rare', 'Rare'),
        ('Rare Holocarbon', 'Rare Holocarbon'),
        ('Rare Ultra', 'Rare Ultra'),
        ('Rare Secret', 'Rare Secret'),
    ]

    name = models.CharField(max_length=100)
    rarity = models.CharField(max_length=50, choices=RARITY_CHOICES)
    image_url = models.URLField(blank=True, null=True)
    average_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    set = models.ForeignKey(ExpansionSet, on_delete=models.CASCADE, related_name='cards')

    def __str__(self):
        return f"{self.name} ({self.set.name})"


class CollectionItem(models.Model):
    CONDITION_CHOICES = [
        ('Mint', 'Mint'),
        ('Near Mint', 'Near Mint'),
        ('Excellent', 'Excellent'),
        ('Good', 'Good'),
        ('Fair', 'Fair'),
        ('Poor', 'Poor'),
    ]

    card = models.ForeignKey(Card, on_delete=models.CASCADE, related_name='collection_items')
    condition = models.CharField(max_length=50, choices=CONDITION_CHOICES)
    quantity = models.IntegerField(default=1)
    acquired_date = models.DateField(auto_now_add=True)
    grade = models.CharField(max_length=20, blank=True, null=True)
    purchase_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    market_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    def __str__(self):
        return f"{self.card.name} x{self.quantity}"

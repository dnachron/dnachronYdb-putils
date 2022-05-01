from django.db import models

# Create your models here.
class YMutations(models.Model):
    class MutationTypeChoices(models.TextChoices):
        SNP = "SNP", "SNP"
        INDEL = "INDEL", "INDEL"

    name = models.CharField(max_length=25)

    position = models.PositiveIntegerField()
    mutation_type = models.CharField(max_length=5, choices=MutationTypeChoices.choices)
    ancestral = models.CharField(max_length=100)
    derived = models.CharField(max_length=100)

    join_date = models.DateField()

    ycc_haplogroup = models.TextField(blank=True, null=True)
    isogg_haplogroup = models.TextField(blank=True, null=True)
    ref = models.TextField(blank=True, null=True)
    comment = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{str(self.position)} {self.ancestral} {self.derived}"

    class Meta:
        db_table = "ymutation"
        indexes = [
            models.Index(fields=["name"]),
            models.Index(fields=["position"]),
        ]
        constraints = [models.UniqueConstraint(fields=["name"], name="%(app_label)s_%(class)s_unique_name")]


class YErrorMutation(models.Model):
    name = models.CharField(max_length=25)
    join_date = models.DateField()

    class Meta:
        db_table = "ymutation_error"
        indexes = [
            models.Index(fields=["name"]),
        ]
        constraints = [models.UniqueConstraint(fields=["name"], name="%(app_label)s_%(class)s_unique_name")]

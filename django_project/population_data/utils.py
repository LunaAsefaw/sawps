from population_data.models import (
    AnnualPopulation,
    AnnualPopulationPerActivity
)


def copy_owned_species_fields(instance: AnnualPopulation):
    """
    This migration function is used to copy Owned Species' fields into
    Annual Population. Remove this once Owned Species is removed.
    """
    instance.user = instance.owned_species.user
    instance.taxon = instance.owned_species.taxon
    instance.property = instance.owned_species.property
    instance.area_available_to_species = (
        instance.owned_species.area_available_to_species
    )
    instance.save()


def assign_annual_population(
    instance: AnnualPopulationPerActivity,
    AnnualPopModel=None,
    AnnualPopPAModel=None
):
    """
    This migration function is used to assign Annual Population object into
    Annual Population Per Activity. Remove this once Owned Species is removed.
    """
    AnnualPopModel = AnnualPopModel if AnnualPopModel else AnnualPopulation
    AnnualPopPAModel = AnnualPopPAModel \
        if AnnualPopPAModel \
        else AnnualPopulationPerActivity

    annual_population = AnnualPopModel.objects.filter(
        owned_species=instance.owned_species,
        year=instance.year
    ).first()

    if not annual_population:
        population_activity = AnnualPopPAModel.objects.filter(
            year=instance.year,
            owned_species=instance.owned_species
        )
        total = sum([pop_act.total for pop_act in population_activity])
        annual_population = AnnualPopModel.objects.create(
            owned_species=instance.owned_species,
            year=instance.year,
            taxon=instance.owned_species.taxon,
            property=instance.owned_species.property,
            total=total
        )
    instance.annual_population = annual_population
    instance.save()

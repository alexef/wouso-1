import django.db.models
import os.path
from django.db import models
from django.conf import settings

class Modifier(models.Model):
    """ Basic unic for all the magic.
    It is extended by:
        - Artifact (adding image, groupping and percents)
        - Spell (all of artifact + time cast)
    """
    class Meta:
        abstract = True

    name = models.CharField(max_length=100)


class ArtifactGroup(models.Model):
    """ A group of artifacts for a Species. It cannot contain two artifacts of the same name."""
    name = models.CharField(max_length=100)
    
    def __unicode__(self):
        return self.name

class Artifact(Modifier):
    """ The generic artifact model. This should contain the name (identifier) and group,
    but also personalization such as: image (icon) and title
    """
    class Meta:
        unique_together = ('name', 'group', 'percents')

    title = models.CharField(max_length=100) # Maturator
    image = models.ImageField(upload_to=settings.MEDIA_ARTIFACTS_DIR, blank=True, null=True)
    group = models.ForeignKey(ArtifactGroup)

    percents = models.IntegerField(default=100)

    @property
    def path(self):
        """ Image can be stored inside uploads or in theme, return the
        full path or the css class. """
        if self.image:
            return "%s/%s" % (settings.MEDIA_ARTIFACTS_URL, os.path.basename(str(self.image)))
        return "%s-%s" %  (self.group.name.lower(), self.name)

    @classmethod
    def DEFAULT(kls):
        # TODO: get rid of me
        return ArtifactGroup.objects.get_or_create(name='Default')[0]

    @classmethod
    def get_level_1(kls):
        """ Temporary method for setting default artifact until God and Guildes """
        # TODO: I think this is deprecated
        try:
            return Artifact.objects.get(name='level-1')
        except:
            return None
    
    def __unicode__(self):
        return u"%s [%s]" % (self.name, self.group.name)


class NoArtifactLevel(object):
    """
    Mock an artifact object
    """
    def __init__(self, level):
        self.name = 'level-%s' % level
        self.title = 'Level %s' % level
        self.image = ''
        self.path = 'default-%s' % self.name
        self.group = None


class Spell(Artifact):
    TYPES = (('o', 'neutral'), ('p', 'positive'), ('n', 'negative'))

    description = models.TextField() # Extended description shown in the magic place
    type = models.CharField(max_length=1, choices=TYPES, default='o')
    price = models.FloatField(default=10)       # Spell price in gold.
    due_days = models.IntegerField(default=3) # How many days may the spell be active


class SpellHistory(models.Model):
    TYPES = (('b', 'bought'), ('u', 'used'), ('c', 'cleaned'), ('e', 'expired'))

    type = models.CharField(max_length=1, choices=TYPES)
    user_from = models.ForeignKey('user.Player', related_name='sh_from')
    user_to = models.ForeignKey('user.Player', blank=True, null=True, default=None, related_name='sh_to')
    date = models.DateTimeField(auto_now_add=True)
    spell = models.ForeignKey(Spell)

    @classmethod
    def log(cls, type, user, spell, user_to=None):
        cls.objects.create(user_from=user, spell=spell, user_to=user_to, type=type)

    @classmethod
    def bought(cls, user, spell):
        cls.log('b', user, spell)

    @classmethod
    def expired(cls, user, spell):
        cls.log('e', user, spell)

    @classmethod
    def used(cls, user, spell, dest):
        if spell.name == 'dispell':
            type = 'c'
        else:
            type = 'u'
        cls.log(type, user, spell, user_to=dest)

    def __unicode__(self):
        if self.type == 'b':
            return u"%s bought %s" % (self.user_from, self.spell)
        if self.type == 'c':
            return u"%s cleared %s" % (self.user_from, self.user_to)
        if self.type == 'u':
            return u"%s cast %s on %s" % (self.user_from, self.spell, self.user_to)
        if self.type == 'e':
            return u"%s expired %s" % (self.user_from, self.spell)
        return "%s %s %s" % (self.type, self.user_from, self.spell)


# Tolbe

class RaceArtifactAmount(models.Model):
    class Meta:
        unique_together = ('race', 'artifact')

    race = models.ForeignKey('user.Race')
    artifact = models.ForeignKey(Artifact)
    amount = models.IntegerField(default=1)


class GroupArtifactAmount(models.Model):
    """ Tie artifact and amount to the owner group """
    class Meta:
        unique_together = ('group', 'artifact')
    group = models.ForeignKey('user.PlayerGroup')
    artifact = models.ForeignKey(Artifact)
    amount = models.IntegerField(default=1)


class PlayerArtifactAmount(models.Model):
    """ Tie artifact and amount to the owner user """
    class Meta:
        unique_together = ('player', 'artifact')
    player = models.ForeignKey('user.Player')
    artifact = models.ForeignKey(Artifact)
    amount = models.IntegerField(default=1)

    def __unicode__(self):
        return u"%s has %s [%d]" % (self.player, self.artifact, self.amount)


class PlayerSpellAmount(models.Model):
    """ Tie spells to collecting user """
    class Meta:
        unique_together = ('player', 'spell')
    player = models.ForeignKey('user.Player')
    spell = models.ForeignKey(Spell)
    amount = models.IntegerField(default=1)

    def __unicode__(self):
        return u"%s has %s [%d]" % (self.player, self.spell, self.amount)


class PlayerSpellDue(models.Model):
    """ Tie spell, casting user, duration with the victim player """
    class Meta:
        unique_together = ('player', 'spell')
    player = models.ForeignKey('user.Player')
    spell = models.ForeignKey(Spell)
    source = models.ForeignKey('user.Player', related_name='spell_source')
    due = models.DateTimeField()

    seen = models.BooleanField(default=False, blank=True) # if the target have seen it

    @staticmethod
    def get_expired(date):
        return PlayerSpellDue.objects.filter(due__lte=date)

    def __unicode__(self):
        return u"%s casted on %s until %s [%s]" % (self.spell, self.player, self.due, self.source)

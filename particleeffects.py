from panda3d.core import Filename
from direct.particles.ParticleEffect import ParticleEffect


class ParticleEffects:
    base.enableParticles()
    p = ParticleEffect()
    p.cleanup()
    p = ParticleEffect()
    p.loadConfig(Filename('bullet_trail.ptf'))
    p.setH(-90)
    p.setY(20)

    def __init__(self, t):
        ParticleEffects.p.start(t)
